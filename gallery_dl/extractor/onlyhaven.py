# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://cum.st/"""

from .common import Extractor, Message
from .. import text, util

BASE_PATTERN = r"(?:https?://)?(?:www\.)?cum\.st"
USER_PATTERN = BASE_PATTERN + r"/creators/([^/?#]+)/([^/?#]+)"


class OnlyhavenExtractor(Extractor):
    """Base class for onlyhaven extractors"""
    category = "onlyhaven"
    root = "https://cum.st"
    root_dl = "https://e1.cum.st/media"
    directory_fmt = ("{category}", "{service}", "{user}")
    filename_fmt = "{id}_{title[:180]}_{num:>02}_{filename[:180]}.{extension}"
    archive_fmt = "{service}_{user}_{id}_{num}"
    cookies_domain = ".cum.st"

    def _init(self):
        if domain := self.config("domain"):
            self.root = (text.root_from_url(self.url) if domain == "auto" else
                         text.ensure_http_scheme(domain))
            lhs, sep, rhs = self.root.partition("://")
            self.root_dl = f"{lhs}{sep}e1.{rhs}/media"
            self.cookies_domain = "." + rhs

        self.api = OnlyhavenAPI(self)
        self._find_inline = text.re(
            r'src="(?:https?://(?:cum\.(?:st)))?(/inline/[^"]+'
            r'|/[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{64}\.[^"]+)').findall

    def items(self):
        creator_info = {} if self.config("metadata", True) else None

        # prevent files from being sent with gzip compression
        headers = {"Accept-Encoding": "identity"}

        for post in self.posts():
            post["_http_headers"] = headers
            post["date"] = self.parse_timestamp(
                post.get("published") or post.get("added") or 0)
            service = post["service"]
            post["user"] = creator_id = \
                post.get("creatorId") or self.creator_id
            if chtml := post.get("captionHtml"):
                post["title"] = text.unescape(text.remove_html(
                    chtml.partition("\n")[0]))
            else:
                post["title"] = post.get(
                    "caption", "").partition("\n")[0].strip()

            if creator_info is not None:
                key = f"{service}_{creator_id}"
                if key in creator_info:
                    creator = creator_info[key]
                else:
                    try:
                        creator = creator_info[key] = self.api.creator_profile(
                            service, creator_id)
                    except self.exc.HttpError:
                        self.log.warning("%s/%s/%s: 'Creator not found'",
                                         service, creator_id, post["id"])
                        creator = creator_info[key] = util.NONE

                post["user_profile"] = creator
                post["username"] = creator["name"]

            files = []
            for file in post["attachments"]:
                try:
                    variant = max(file["variants"],
                                  key=lambda v: v.get("bytes", 0))
                except LookupError as exc:
                    if file.get("locked"):
                        self.log.warning("%s/%s: 'Locked' file",
                                         post["id"], file.get("position"))
                    else:
                        self.log.warning("%s/%s: General error (%s: %s)",
                                         post["id"], file.get("position"),
                                         exc.__clasa__.__name__, exc)
                    continue
                path = variant["name"]
                file["url"] = f"{self.root_dl}/{file['storageKey']}/{path}"

                if name := file.get("originalFilename"):
                    text.nameext_from_name(name, file)
                    if not file["extension"]:
                        file["extension"] = text.ext_from_url(path)
                else:
                    text.nameext_from_url(path, file)

                files.append(file)

            post["count"] = len(files)
            yield Message.Directory, "", post
            for post["num"], file in enumerate(files, 1):
                file["file_id"] = file.pop("id", None)
                post.update(file)
                yield Message.Url, file["url"], post


class OnlyhavenUserExtractor(OnlyhavenExtractor):
    """Extractor for all posts from a onlyhaven user listing"""
    subcategory = "user"
    pattern = USER_PATTERN + r"/?(?:\?([^#]+))?(?:$|\?|#)"
    example = "https://cum.st/creators/SERVICE/12345"

    def __init__(self, match):
        self.subcategory = match[1]
        OnlyhavenExtractor.__init__(self, match)

    def posts(self):
        service, self.creator_id, query = self.groups
        params = text.parse_query(query)

        if self.config("endpoint") in {"posts+", "legacy+"}:
            endpoint = self.api.creator_posts_expand
        else:
            endpoint = self.api.creator_posts

        return endpoint(service, self.creator_id,
                        params.get("o"), params.get("q"),
                        params.get("type"), params.get("sort"))


class OnlyhavenPostExtractor(OnlyhavenExtractor):
    """Extractor for a single onlyhaven post"""
    subcategory = "post"
    pattern = USER_PATTERN + r"/post/([^/?#]+)"
    example = "https://cum.st/creators/SERVICE/12345/post/12345"

    def __init__(self, match):
        self.subcategory = match[1]
        OnlyhavenExtractor.__init__(self, match)

    def posts(self):
        service, self.creator_id, post_id = self.groups
        return (self.api.creator_post(service, self.creator_id, post_id),)


class OnlyhavenPostsExtractor(OnlyhavenExtractor):
    """Extractor for onlyhaven post listings"""
    subcategory = "posts"
    pattern = BASE_PATTERN + r"/posts(?:/?\?([^#]+))?"
    example = "https://cum.st/posts"

    def posts(self):
        self.creator_id = 0
        params = text.parse_query(self.groups[0])
        return self.api.posts(
            params.get("o"), params.get("q"),
            params.get("service"), params.get("type"), params.get("sort"))


class OnlyhavenAPI():
    """Interface for the OnlyHaven API

    https://cum.st/swagger/index.html
    """

    def __init__(self, extractor):
        self.extractor = extractor
        self.root = extractor.root + "/api"

    def account_favorites(self, type):
        endpoint = "/v1/account/favorites"
        params = {"type": type}
        return self._call(endpoint, params)

    def creators(self):
        endpoint = "/v1/creators"
        return self._call(endpoint)

    def creator_posts(self, service, creator_id,
                      offset=0, query=None, type=None, sort=None):
        endpoint = f"/v1/{service}/user/{creator_id}/posts"
        params = {"o": offset, "q": query, "type": type, "sort": sort}
        return self._pagination(endpoint, params, 50, "posts")

    def creator_posts_expand(self, service, creator_id,
                             offset=0, query=None, type=None, sort=None):
        for post in self.creator_posts(
                service, creator_id, offset, query, type, sort):
            yield self.creator_post(service, creator_id, post["id"])

    def creator_dms(self, service, creator_id):
        endpoint = f"/v1/{service}/user/{creator_id}/dms"
        return self._call(endpoint)

    def creator_post(self, service, creator_id, post_id):
        endpoint = f"/v1/{service}/user/{creator_id}/post/{post_id}"
        return self._call(endpoint)

    def creator_profile(self, service, creator_id):
        endpoint = f"/v1/{service}/user/{creator_id}/profile"
        return self._call(endpoint)

    def creator_links(self, service, creator_id):
        endpoint = f"/v1/{service}/user/{creator_id}/links"
        return self._call(endpoint)

    def posts(self, offset=0, query=None, service=None, type=None, sort=None):
        endpoint = "/v1/posts"
        params = {"o": offset, "q": query,
                  "service": service, "type": type, "sort": sort}
        return self._pagination(endpoint, params, 50, "posts")

    def _call(self, endpoint, params=None, headers=None, fatal=True):
        return self.extractor.request_json(
            self.root + endpoint, params=params, headers=headers,
            encoding="utf-8", fatal=fatal)

    def _pagination(self, endpoint, params, batch=50, key=None):
        offset = text.parse_int(params.get("o"))
        params["o"] = offset - offset % batch
        params["n"] = batch

        while True:
            data = self._call(endpoint, params)

            if key is not None:
                data = data.get(key)
            if not data:
                break
            yield from data

            if len(data) < batch:
                break
            params["o"] += batch
