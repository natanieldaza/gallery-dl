# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://pawchive.pw/"""

from .common import Extractor, Message
from .. import text, util
import itertools

BASE_PATTERN = r"(?:https?://)?(?:www\.)?pawchive\.(?:pw|st)"
USER_PATTERN = BASE_PATTERN + r"/([^/?#]+)/user/([^/?#]+)"


class PawchiveExtractor(Extractor):
    """Base class for pawchive extractors"""
    category = "pawchive"
    root = "https://pawchive.pw"
    root_dl = "https://file.pawchive.pw"
    directory_fmt = ("{category}", "{service}", "{user}")
    filename_fmt = "{id}_{title[:180]}_{num:>02}_{filename[:180]}.{extension}"
    archive_fmt = "{service}_{user}_{id}_{num}"
    cookies_domain = ".pawchive.pw"
    useragent = util.USERAGENT_GALLERYDL
    request_interval = 1.0

    def _init(self):
        if domain := self.config("domain"):
            self.root = (text.root_from_url(self.url) if domain == "auto" else
                         text.ensure_http_scheme(domain))
            lhs, sep, rhs = self.root.partition("://")
            self.root_dl = f"{lhs}{sep}file.{rhs}"
            self.cookies_domain = "." + rhs

        if revisions := self.config("revisions"):
            self.revisions = True
            self.revisions_unique = (revisions == "unique")
        else:
            self.revisions = False
        order = self.config("order-revisions")
        self.revisions_reverse = order[0] in {"r", "a"} if order else False

        self.api = PawchiveAPI(self)
        self._find_inline = text.re(
            r'src="(?:https?://(?:pawchive\.(?:pw|st)))?(/inline/[^"]+'
            r'|/[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{64}\.[^"]+)').findall

    def items(self):
        find_hash = text.re(r"/[0-9a-f]{2}/[0-9a-f]{2}/([0-9a-f]{64})").match
        generators = self._build_file_generators(self.config("files"))
        archives = True if self.config("archives") else False
        archives_type = dict if self.config("archives-format") in {
            "dict", "object"} else list
        comments = True if self.config("comments") else False
        previews = True if self.config("previews") else False
        original = True if self.config("original", True) else False
        creator_info = {} if self.config("metadata", True) else None
        exts_archive = util.EXTS_ARCHIVE
        root_thmb = self.root.replace("://", "://img.") + "/thumbnail/data"
        exts_thmb = util.EXTS_IMAGE

        if duplicates := self.config("duplicates"):
            if isinstance(duplicates, str):
                duplicates = set(duplicates.split(","))
            elif isinstance(duplicates, (list, tuple)):
                duplicates = set(duplicates)
            else:
                duplicates = {"file", "attachment", "inline"}
        else:
            duplicates = ()

        # prevent files from being sent with gzip compression
        headers = {"Accept-Encoding": "identity"}

        posts = self.posts()
        if max_posts := self.config("max-posts"):
            posts = itertools.islice(posts, max_posts)
        if self.revisions:
            posts = self._revisions(posts)

        for post in posts:
            headers["Referer"] = (f"{self.root}/{post['service']}/user/"
                                  f"{post['user']}/post/{post['id']}")
            post["_http_headers"] = headers
            post["date"] = self._parse_datetime(
                post.get("published") or post.get("added") or "")
            service = post["service"]
            creator_id = post["user"]

            if not post.get("has_full", True):
                self.log.warning("%s: Incomplete/Missing file import ('%s')",
                                 post["id"], post.get("preview_state"))

            if creator_info is not None:
                key = f"{service}_{creator_id}"
                if key not in creator_info:
                    try:
                        creator = creator_info[key] = self.api.creator_profile(
                            service, creator_id)
                    except self.exc.HttpError:
                        self.log.warning("%s/%s/%s: 'Creator not found'",
                                         service, creator_id, post["id"])
                        creator = creator_info[key] = util.NONE
                else:
                    creator = creator_info[key]

                post["user_profile"] = creator
                post["username"] = creator["name"]

            if comments:
                post["comments"] = cmts = self.api.creator_post_comments(
                    service, creator_id, post["id"])
                if not isinstance(cmts, list):
                    self.log.debug("%s/%s: %s", creator_id, post["id"], cmts)
                    post["comments"] = ()

            if tags := post.get("tags"):
                if isinstance(tags, str):
                    post["tags"] = tags[1:-1].replace('"', '').split(",")
            else:
                post["tags"] = ()

            files = []
            hashes = set()
            warning = True
            post_archives = post["archives"] = archives_type()

            for file in itertools.chain.from_iterable(
                    g(post) for g in generators):
                try:
                    path = file["path"]
                except KeyError:
                    if warning:
                        warning = False
                        self.log.debug(file)
                        self.log.warning("%s: Incomplete import", post["id"])
                    continue

                if "\\" in path:
                    file["path"] = path = path.replace("\\", "/")

                if path[0] == "/":
                    file["url"] = f"{self.root_dl}/data{path}"
                else:
                    file["url"] = path

                if match := find_hash(path):
                    file["hash"] = hash = match[1]
                    if file["type"] not in duplicates and hash in hashes:
                        self.log.debug("Skipping %s %s (duplicate)",
                                       file["type"], path)
                        continue
                    hashes.add(hash)
                else:
                    file["hash"] = hash = ""

                if name := file.get("name"):
                    text.nameext_from_name(name, file)
                    ext = text.ext_from_url(path)
                    if not file["extension"]:
                        file["extension"] = ext
                else:
                    text.nameext_from_url(path, file)
                    ext = file["extension"]

                if ext in exts_archive or \
                        ext == "bin" and file["extension"] in exts_archive:
                    file["type"] = "archive"
                    if archives:
                        try:
                            archive = self.api.file(hash)
                            archive.update(file)
                        except Exception as exc:
                            self.log.warning(
                                "%s: Failed to retrieve archive metadata of "
                                "'%s' (%s: %s)", post["id"], file.get("name"),
                                exc.__class__.__name__, exc)
                            archive = file.copy()
                    else:
                        archive = file.copy()
                    if archives_type is dict:
                        post_archives[hash] = archive
                    else:
                        post_archives.append(archive)

                file["file_id"] = file.pop("id", None)
                files.append(file)

            post["count"] = len(files)
            yield Message.Directory, "", post
            if original:
                for post["num"], file in enumerate(files, 1):
                    if not file.get("preview_only"):
                        url = file["url"]
                        file["original"] = True
                        if previews:
                            file["_fallback"] = (root_thmb + file["path"],)
                    elif previews:
                        url = root_thmb + file["path"]
                        file["extension"] = "webp"
                        file["original"] = False
                    else:
                        self.log.info("%s: Skipping %s ('preview only')",
                                      post["id"], file["path"][7:])
                        continue
                    post.update(file)
                    yield Message.Url, url, post
            else:
                for post["num"], file in enumerate(files, 1):
                    if file["extension"] in exts_thmb:
                        file["extension"] = "webp"
                        post.update(file)
                        post["original"] = False
                        yield Message.Url, root_thmb + file["path"], post
                    else:
                        self.log.warning("%s: Skipping %s",
                                         post["id"], file["path"][7:])

    def _extract_file(self, post):
        file = post["file"]
        if not file or "path" not in file:
            return ()
        file["type"] = "file"
        return (file,)

    def _extract_attachments(self, post):
        for attachment in post["attachments"]:
            attachment["type"] = "attachment"
        return post["attachments"]

    def _extract_inline(self, post):
        for path in self._find_inline(post.get("content") or ""):
            yield {"path": path, "name": path, "type": "inline"}

    def _build_file_generators(self, filetypes):
        if filetypes is None:
            return (self._extract_file,
                    self._extract_attachments,
                    self._extract_inline)

        genmap = {
            "file"       : self._extract_file,
            "attachments": self._extract_attachments,
            "inline"     : self._extract_inline,
        }
        if isinstance(filetypes, str):
            filetypes = filetypes.split(",")
        return [genmap[ft] for ft in filetypes]

    def _parse_datetime(self, date_string):
        if len(date_string) > 19:
            date_string = date_string[:19]
        return self.parse_datetime_iso(date_string)

    def _revisions(self, posts):
        return itertools.chain.from_iterable(
            self._revisions_post(post) for post in posts)

    def _revisions_get(self, post):
        return self.api.creator_post_revisions(
            post["service"], post["user"], post["id"])

    def _revisions_post(self, post):
        revs = self._revisions_get(post)

        post["revision_id"] = 0
        if not revs:
            post["revision_hash"] = self._revision_hash(post)
            post["revision_index"] = 1
            post["revision_count"] = 1
            return (post,)

        revs.insert(0, post)
        for rev in revs:
            rev["revision_hash"] = self._revision_hash(rev)

        if self.revisions_unique:
            uniq = []
            last = None
            for rev in revs:
                if last != rev["revision_hash"]:
                    last = rev["revision_hash"]
                    uniq.append(rev)
            revs = uniq

        cnt = idx = len(revs)
        for rev in revs:
            rev["revision_index"] = idx
            rev["revision_count"] = cnt
            idx -= 1

        if self.revisions_reverse:
            revs.reverse()

        return revs

    def _revisions_all(self, post):
        post["revision_id"] = 0
        revs = self._revisions_get(post)
        revs.insert(0, post)

        cnt = idx = len(revs)
        for rev in revs:
            rev["revision_hash"] = self._revision_hash(rev)
            rev["revision_index"] = idx
            rev["revision_count"] = cnt
            idx -= 1

        if self.revisions_reverse:
            revs.reverse()

        return revs

    def _revision_hash(self, revision):
        rev = {key: revision.get(key)
               for key in ("id", "user", "service", "title", "content",
                           "embed", "published", "edited", "captions", "tags")}
        rev["file"] = revision["file"].copy()
        rev["file"].pop("name", None)
        rev["attachments"] = [att.copy() for att in revision["attachments"]]
        for att in rev["attachments"]:
            att.pop("name", None)
        return util.sha1(util.json_dumps(rev))

    def _expand(self, posts):
        if self.config("expand") or \
                self.config("endpoint") in {"posts+", "legacy+"}:
            def gen():
                creator_post = self.api.creator_post
                for post in posts:
                    yield creator_post(
                        post["service"], post["user"], post["id"])
            return gen()
        return posts


class PawchiveUserExtractor(PawchiveExtractor):
    """Extractor for all posts from a pawchive user listing"""
    subcategory = "user"
    pattern = USER_PATTERN + r"/?(?:\?([^#]+))?(?:$|\?|#)"
    example = "https://pawchive.pw/SERVICE/user/12345"

    def __init__(self, match):
        self.subcategory = match[1]
        PawchiveExtractor.__init__(self, match)

    def posts(self):
        service, creator_id, query = self.groups
        params = text.parse_query(query)

        return self._expand(self.api.creator_posts(
            service, creator_id,
            params.get("o"), params.get("q"), params.get("tag")))


class PawchivePostExtractor(PawchiveExtractor):
    """Extractor for a single pawchive post"""
    subcategory = "post"
    pattern = USER_PATTERN + r"/post/([^/?#]+)(/revisions?(?:/(\d*))?)?"
    example = "https://pawchive.pw/SERVICE/user/12345/post/12345"

    def __init__(self, match):
        self.subcategory = match[1]
        PawchiveExtractor.__init__(self, match)

    def posts(self):
        service, creator_id, post_id, revision, revision_id = self.groups
        post = self.api.creator_post(service, creator_id, post_id)
        if not revision:
            return (post,)

        self.revisions = False
        revs = self._revisions_all(post)
        if not revision_id:
            return revs

        for rev in revs:
            if str(rev["revision_id"]) == revision_id:
                return (rev,)
        raise self.exc.NotFoundError("revision")


class PawchivePostsExtractor(PawchiveExtractor):
    """Extractor for pawchive post listings"""
    subcategory = "posts"
    pattern = BASE_PATTERN + r"/posts(?:/?\?([^#]+))?"
    example = "https://pawchive.pw/posts"

    def posts(self):
        params = text.parse_query(self.groups[0])
        return self._expand(self.api.posts(
            params.get("o"), params.get("q"), params.get("tag")))


class PawchiveFavoriteExtractor(PawchiveExtractor):
    """Extractor for pawchive favorites"""
    subcategory = "favorite"
    pattern = BASE_PATTERN + r"/(?:account/)?favorites(?:/?\?([^#]+))?"
    example = "https://pawchive.pw/favorites"

    def items(self):
        self.login()

        params = text.parse_query(self.groups[0])
        type = params.get("type") or self.config("favorites") or "artist"

        sort = params.get("sort")
        order = params.get("order") or "desc"

        if type == "artist":
            users = self.api.account_favorites("artist")

            if not sort:
                sort = "updated"
            users.sort(key=lambda x: x[sort] or util.NONE,
                       reverse=(order == "desc"))

            for user in users:
                user["_extractor"] = PawchiveUserExtractor
                url = f"{self.root}/{user['service']}/user/{user['id']}"
                yield Message.Queue, url, user

        elif type == "post":
            posts = self.api.account_favorites("post")

            if not sort:
                sort = "faved_seq"
            posts.sort(key=lambda x: x[sort] or util.NONE,
                       reverse=(order == "desc"))

            for post in posts:
                post["_extractor"] = PawchivePostExtractor
                url = (f"{self.root}/{post['service']}/user/"
                       f"{post['user']}/post/{post['id']}")
                yield Message.Queue, url, post

    def login(self):
        username, password = self._get_auth_info()
        if username:
            self.cookies_update(self.cache(
                self._login_impl, username, password,
                _exp=3650*86400, _mem=False))

    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = self.root + "/account/login"
        data = {"username": username, "password": password}

        response = self.request(url, method="POST", data=data, fatal=False)
        if response.status_code >= 400 or not response.history:
            msg = '"Username or password is incorrect"'
            raise self.exc.AuthenticationError(msg)

        return {c.name: c.value for c in response.history[0].cookies}


class PawchiveArtistsExtractor(PawchiveExtractor):
    """Extractor for pawchive artists"""
    subcategory = "artists"
    pattern = BASE_PATTERN + r"/artists(?:\?([^#]+))?"
    example = "https://pawchive.pw/artists"

    def items(self):
        users = self.api.creators()
        params = text.parse_query(self.groups[0])

        if params.get("service"):
            service = params["service"].lower()
            users = [user for user in users
                     if user["service"] == service]

        if params.get("q"):
            q = params["q"].lower()
            users = [user for user in users
                     if q in user["name"].lower()]

        sort = params.get("sort_by") or "favorited"
        order = params.get("order") or "desc"
        users.sort(key=lambda user: user[sort] or util.NONE,
                   reverse=(order != "asc"))

        for user in users:
            user["_extractor"] = PawchiveUserExtractor
            url = f"{self.root}/{user['service']}/user/{user['id']}"
            yield Message.Queue, url, user


class PawchiveAPI():
    """Interface for the Pawchive API

    https://pawchive.pw/api/swagger_schema
    """

    def __init__(self, extractor):
        self.extractor = extractor
        self.root = extractor.root + "/api"

    def posts(self, offset=0, query=None, tags=None):
        endpoint = "/v1/posts"
        params = {"q": query, "o": offset, "tag": tags}
        return self._pagination(endpoint, params, 50)

    def file(self, file_hash):
        endpoint = "/v1/search_hash/" + file_hash
        return self._call(endpoint)

    def creators(self):
        endpoint = "/v1/creators"
        return self._call(endpoint)

    def creator_posts(self, service, creator_id,
                      offset=0, query=None, tags=None):
        endpoint = f"/v1/{service}/user/{creator_id}"
        params = {"o": offset, "tag": tags, "q": query}
        return self._pagination(endpoint, params, 50)

    def creator_announcements(self, service, creator_id):
        endpoint = f"/v1/{service}/user/{creator_id}/announcements"
        return self._call(endpoint)

    def creator_dms(self, service, creator_id):
        endpoint = f"/v1/{service}/user/{creator_id}/dms"
        return self._call(endpoint)

    def creator_fancards(self, service, creator_id):
        endpoint = f"/v1/{service}/user/{creator_id}/fancards"
        return self._call(endpoint)

    def creator_post(self, service, creator_id, post_id):
        endpoint = f"/v1/{service}/user/{creator_id}/post/{post_id}"
        return self._call(endpoint)

    def creator_post_comments(self, service, creator_id, post_id):
        endpoint = f"/v1/{service}/user/{creator_id}/post/{post_id}/comments"
        return self._call(endpoint, fatal=False)

    def creator_post_revisions(self, service, creator_id, post_id):
        endpoint = f"/v1/{service}/user/{creator_id}/post/{post_id}/revisions"
        return self._call(endpoint, fatal=False)

    def creator_profile(self, service, creator_id):
        endpoint = f"/v1/{service}/user/{creator_id}/profile"
        return self._call(endpoint)

    def creator_links(self, service, creator_id):
        endpoint = f"/v1/{service}/user/{creator_id}/links"
        return self._call(endpoint)

    def creator_tags(self, service, creator_id):
        endpoint = f"/v1/{service}/user/{creator_id}/tags"
        return self._call(endpoint)

    def account_favorites(self, type):
        endpoint = "/v1/account/favorites"
        params = {"type": type}
        return self._call(endpoint, params)

    def _call(self, endpoint, params=None, headers=None, fatal=True):
        return self.extractor.request_json(
            self.root + endpoint, params=params, headers=headers,
            encoding="utf-8", fatal=fatal)

    def _pagination(self, endpoint, params, batch=50, key=None):
        offset = text.parse_int(params.get("o"))
        params["o"] = offset - offset % batch

        while True:
            data = self._call(endpoint, params)

            if key is not None:
                data = data.get(key)
            if not data:
                return
            yield from data

            if len(data) < batch:
                return
            params["o"] += batch
