# -*- coding: utf-8 -*-

# Copyright 2020-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.furaffinity.net/"""

from .common import Extractor, Message, Dispatch
from .. import text, util

BASE_PATTERN = r"(?:https?://)?(?:www\.|sfw\.)?(?:f[ux]|f?xfu)raffinity\.net"


class FuraffinityExtractor(Extractor):
    """Base class for furaffinity extractors"""
    category = "furaffinity"
    directory_fmt = ("{category}", "{user!l}")
    filename_fmt = "{id}{title:? //}.{extension}"
    archive_fmt = "{id}"
    cookies_domain = ".furaffinity.net"
    cookies_names = ("a", "b")
    root = "https://www.furaffinity.net"
    request_interval = 1.0
    _warning = True

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match[1]
        self.offset = 0

    def _init(self):
        self.external = self.config("external", False)

        if self.config("descriptions") == "html":
            self._process_description = str.strip
        if self.config("comments") == "html":
            self._process_comment = str.strip

        layout = self.config("layout")
        if layout and layout != "auto":
            self._new_layout = False if layout == "old" else True
        else:
            self._new_layout = None

        if self._warning:
            if not self.cookies_check(self.cookies_names):
                self.log.warning("no 'a' and 'b' session cookies set")
            FuraffinityExtractor._warning = False

    def items(self):
        metadata = self.metadata()
        for post_id in util.advance(self.posts(), self.offset):
            if post := self._parse_post(post_id):
                if metadata:
                    post.update(metadata)
                url = post.pop("url")
                yield Message.Directory, "", post
                yield Message.Url, url, post

                if self.external:
                    for url in text.extract_iter(
                            post["_description"], 'href="http', '"'):
                        yield Message.Queue, "http" + url, post

    def metadata(self):
        return None

    def skip_files(self, num):
        self.offset += num
        return num

    def _parse_post(self, post_id):
        url = f"{self.root}/view/{post_id}/"
        page = self.request(url).text
        extr = text.extract_from(page)

        if self._new_layout is None:
            self._new_layout = ("http-equiv=" not in extr("<meta ", ">"))

        pos = page.find(">Download<")
        if pos < 0:
            msg = text.remove_html(
                extr('System Message', '</section>') or
                extr('System Message', '</table>')
            ).partition(" . Continue ")[0]
            return self.log.warning(
                "Unable to download post %s (\"%s\")", post_id, msg)

        pi = text.parse_int
        rh = text.remove_html

        path = text.rextr(page, 'href="', '"', pos)
        data = text.nameext_from_url(path, {
            "id" : pi(post_id),
            "url": "https:" + path,
        })

        if self._new_layout:
            data["scraps"] = ("/scraps/" in extr(
                'class="minigallery-title', '</a>'))
            data["artist_url"] = extr('displayName" title=" ', ' "').strip()
            data["artist"] = extr('>', '<')
            data["_description"] = extr('user-submitted-links">', '</section>')
            data["views"] = pi(rh(extr('title="Views">', '</div>')))
            #  data["comments"] = pi(rh(extr('title="Comments">', '</div>')))
            data["favorites"] = pi(rh(extr('title="Favorites">', '</div>')))
            data["rating"] = extr('inline c-contentRating--', '"')
            info = text.split_html(extr('<span class="highlight">', '</div>'))
            size = len(info) >> 1
            info = {info[i].lower(): info[i + size] for i in range(size)}
            width, _, height = info.get("resolution", "").partition("x")
            data["fa_category"] = info.get("category", "")
            data["fa_subcategory"] = info.get("theme", "")
            data["species"] = info.get("species", "")
            data["width"] = pi(width)
            data["height"] = pi(height)
            data["size"] = text.parse_bytes(info.get("file size", "")[:-1])
            data["tags"] = text.split_html(extr('>Keywords</div>', '</div>'))
            data["folders"] = [
                name
                for folder in extr(
                    '>Folders</div>',
                    '<div class="comments-list">').split('</a>')
                if (name := rh(folder))
            ]
            data["comments"] = self._extract_comments(extr(
                'id="comments-submission"', '<script type="text/javascript">'))
            data["title"] = text.unescape(extr('data-artwork-title="', '"'))
        else:
            # old site layout
            data["scraps"] = (
                "/scraps/" in extr('class="minigallery-title', "</a>"))
            data["title"] = text.unescape(extr("<h2>", "</h2>"))
            data["artist_url"] = extr('title="', '"').strip()
            data["artist"] = extr(">", "<")
            data["fa_category"] = extr("<b>Category:</b>", "<").strip()
            data["theme"] = extr("<b>Theme:</b>", "<").strip()
            data["species"] = extr("<b>Species:</b>", "<").strip()
            data["gender"] = extr("<b>Gender:</b>", "<").strip()
            data["favorites"] = pi(extr("<b>Favorites:</b>", "<"))
            #  data["comments"] = pi(extr("<b>Comments:</b>", "<"))
            data["views"] = pi(extr("<b>Views:</b>", "<"))
            data["width"] = pi(extr("<b>Resolution:</b>", "x"))
            data["height"] = pi(extr("", "<"))
            data["tags"] = text.split_html(extr(
                'id="keywords">', '</div>'))[::2]
            data["rating"] = extr('<img alt="', ' ')
            data["_description"] = extr(
                '<td valign="top" align="left" width="70%" class="alt1" '
                'style="padding:8px">', '                               </td>')
            data["comments"] = self._extract_comments(extr(
                "<b>User comments</b>", '<script type="text/javascript">'))
            data["folders"] = ()  # folders not present in old layout

        data["user"] = self.user or data["artist_url"]
        data["date"] = self.parse_timestamp(data["filename"].partition(".")[0])
        data["description"] = self._process_description(data["_description"])
        data["thumbnail"] = (f"https://t.furaffinity.net/{post_id}@600-"
                             f"{path.rsplit('/', 2)[1]}.jpg")
        return data

    def _parse_journal(self, post_id):
        url = f"{self.root}/journal/{post_id}/"
        page = self.request(url).text
        extr = text.extract_from(page)

        if self._new_layout is None:
            self._new_layout = ("http-equiv=" not in extr("<meta ", ">"))

        if msg := (extr(">System Message", "</section>") or
                   extr("System Message", "</table>")):
            msg = text.remove_html(msg).partition(" . Continue ")[0]
            return self.log.warning("Unable to download journal %s (\"%s\")",
                                    post_id, msg)

        data = {
            "id": text.parse_int(post_id),
            "extension": "htm",
        }

        if self._new_layout:
            data["artist_url"] = extr('-displayName-block" href="/user/', '/"')
            data["artist"] = extr('-displayName">', '<')
            data["title"] = text.unescape(extr(
                'id="c-journalTitleTop__subject"><h3>', '<'))
            data["date"] = self.parse_timestamp(extr(
                'data-time="', '"'))
            data["rating"] = extr('alt="', ' ')
            data["url"] = "text:" + extr(
                'user-submitted-links">',
                '</div>\n                    </div>')
            data["comments"] = self._extract_comments(extr(
                'id="comments-journal"', '<script type="text/javascript">'))
        else:
            data["title"] = text.unescape(extr(
                '<div class="no_overflow">', '<'))
            data["artist_url"] = extr('-userName-block" href="/user/', '/"')
            data["artist"] = extr('</span>', '<')
            data["date"] = self.parse_timestamp(extr(
                'data-time="', '"'))
            data["rating"] = None
            data["url"] = "text:" + extr(
                '<div class="journal-body">',
                '</div>\n                    </td>').strip()
            data["comments"] = self._extract_comments(extr(
                'id="page-comments"', 'id="add_comment_form"'))

        data["user"] = self.user or data["artist_url"]
        return data

    def _process_description(self, description):
        return text.unescape(text.remove_html(description, "", ""))

    _process_comment = _process_description

    def _extract_comments(self, html):
        extr = text.extract_from(html)

        results = []
        if self._new_layout:
            while ts := extr('data-timestamp="', '"'):
                results.append({
                    "date": self.parse_timestamp(ts),
                    "id"  : extr('id="cid:', '"'),
                    "user": extr('href="/user/', '/'),
                    "text": self._process_comment(extr(
                        '<div class="user-submitted-links">',
                        '</div>\n            </comment-user-text>')),
                })
        else:
            while cid := extr('id="cid:', '"'):
                results.append({
                    "id"  : cid,
                    "date": self.parse_timestamp(extr(
                        'data-timestamp="', '"')),
                    "user": extr('href="/user/', '/'),
                    "text": self._process_comment(extr(
                        'class="message-text">',
                        '</div>\n        </td>\n    </tr>')),
                })
        return results

    def _pagination(self, path, folder=None):
        num = 1
        folder = "" if folder is None else f"/folder/{folder}/a"

        while True:
            url = f"{self.root}/{path}/{self.user}{folder}/{num}/"
            page = self.request(url).text
            post_id = None

            for post_id in text.extract_iter(page, 'id="sid-', '"'):
                yield post_id

            if not post_id:
                return
            num += 1

    def _pagination_favorites(self, start=None):
        path = f"/favorites/{self.user}/"
        if start is not None:
            path += start

        while path:
            page = self.request(self.root + path).text
            extr = text.extract_from(page)
            while True:
                post_id = extr('id="sid-', '"')
                if not post_id:
                    break
                self._favorite_id = text.parse_int(extr('data-fav-id="', '"'))
                yield post_id

            pos = page.find('type="submit">Next</button>')
            if pos >= 0:
                path = text.rextr(page, '<form action="', '"', pos)
                continue
            path = text.extr(page, 'right" href="', '"')

    def _pagination_journals(self, pnum=None):
        pnum = text.parse_int(pnum, 1)
        path = f"/journals/{self.user}/{pnum}"
        while True:
            page = self.request(self.root + path).text
            extr = text.extract_from(page)
            while True:
                post_id = extr('<a href="#jid:', '"')
                if not post_id:
                    break
                yield post_id

            pnum += 1
            path = f"/journals/{self.user}/{pnum}/"
            if path not in page:
                break

    def _pagination_search(self, query):
        url = self.root + "/search/"
        data = {
            "page"           : 1,
            "order-by"       : "relevancy",
            "order-direction": "desc",
            "range"          : "all",
            "range_from"     : "",
            "range_to"       : "",
            "rating-general" : "1",
            "rating-mature"  : "1",
            "rating-adult"   : "1",
            "type-art"       : "1",
            "type-music"     : "1",
            "type-flash"     : "1",
            "type-story"     : "1",
            "type-photo"     : "1",
            "type-poetry"    : "1",
            "mode"           : "extended",
        }

        data.update(query)
        if "page" in query:
            data["page"] = text.parse_int(query["page"])

        while True:
            page = self.request(url, method="POST", data=data).text
            post_id = None

            for post_id in text.extract_iter(page, 'id="sid-', '"'):
                yield post_id

            if not post_id:
                return

            if "next_page" in data:
                data["page"] += 1
            else:
                data["next_page"] = "Next"


class FuraffinityGalleryExtractor(FuraffinityExtractor):
    """Extractor for a furaffinity user's gallery"""
    subcategory = "gallery"
    pattern = BASE_PATTERN + r"/gallery/([^/?#]+)(?:$|/(?!folder/))"
    example = "https://www.furaffinity.net/gallery/USER/"

    def posts(self):
        return self._pagination("gallery")


class FuraffinityFolderExtractor(FuraffinityExtractor):
    """Extractor for a FurAffinity folder"""
    subcategory = "folder"
    directory_fmt = ("{category}", "{user!l}",
                     "Folders", "{folder_id}{folder_name:? //}")
    pattern = BASE_PATTERN + r"/gallery/([^/?#]+)/folder/(\d+)(?:/([^/?#]+))?"
    example = "https://www.furaffinity.net/gallery/USER/folder/12345/FOLDER"

    def metadata(self):
        return {
            "folder_id"  : self.groups[1],
            "folder_name": self.groups[2] or "",
        }

    def posts(self):
        return self._pagination("gallery", self.groups[1])


class FuraffinityScrapsExtractor(FuraffinityExtractor):
    """Extractor for a furaffinity user's scraps"""
    subcategory = "scraps"
    directory_fmt = ("{category}", "{user!l}", "Scraps")
    pattern = BASE_PATTERN + r"/scraps/([^/?#]+)"
    example = "https://www.furaffinity.net/scraps/USER/"

    def posts(self):
        return self._pagination("scraps")


class FuraffinityFavoriteExtractor(FuraffinityExtractor):
    """Extractor for a furaffinity user's favorites"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "{user!l}", "Favorites")
    pattern = BASE_PATTERN + r"/favorites/([^/?#]+)(/\d+/(?:next|prev))?"
    example = "https://www.furaffinity.net/favorites/USER/"

    def posts(self):
        return self._pagination_favorites(self.groups[1])

    def _parse_post(self, post_id):
        if post := FuraffinityExtractor._parse_post(self, post_id):
            post["favorite_id"] = self._favorite_id
        return post


class FuraffinityJournalsExtractor(FuraffinityExtractor):
    """Extractor for a furaffinity user's journal entries"""
    subcategory = "journals"
    directory_fmt = ("{category}", "{user!l}", "Journals")
    archive_fmt = "j_{id}"
    pattern = BASE_PATTERN + r"/journals/([^/?#]+)(/\d+)?"
    example = "https://www.furaffinity.net/journals/USER/"

    def posts(self):
        return self._pagination_journals(self.groups[1])

    _parse_post = FuraffinityExtractor._parse_journal


class FuraffinitySearchExtractor(FuraffinityExtractor):
    """Extractor for furaffinity search results"""
    subcategory = "search"
    directory_fmt = ("{category}", "Search", "{search}")
    pattern = BASE_PATTERN + r"/search(?:/([^/?#]+))?/?[?&]([^#]+)"
    example = "https://www.furaffinity.net/search/?q=QUERY"

    def __init__(self, match):
        FuraffinityExtractor.__init__(self, match)
        self.query = text.parse_query(match[2])
        if self.user and "q" not in self.query:
            self.query["q"] = text.unquote(self.user)

    def metadata(self):
        return {"search": self.query.get("q")}

    def posts(self):
        return self._pagination_search(self.query)


class FuraffinityPostExtractor(FuraffinityExtractor):
    """Extractor for individual posts on furaffinity"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/(?:view|full)/(\d+)"
    example = "https://www.furaffinity.net/view/12345/"

    def posts(self):
        post_id = self.user
        self.user = None
        return (post_id,)


class FuraffinityJournalExtractor(FuraffinityExtractor):
    """Extractor for a single furaffinity journal"""
    subcategory = "journal"
    directory_fmt = FuraffinityJournalsExtractor.directory_fmt
    archive_fmt = FuraffinityJournalsExtractor.archive_fmt
    pattern = BASE_PATTERN + r"/journal/(\d+)"
    example = "https://www.furaffinity.net/journal/12345/"

    posts = FuraffinityPostExtractor.posts
    _parse_post = FuraffinityExtractor._parse_journal


class FuraffinityUserExtractor(Dispatch, FuraffinityExtractor):
    """Extractor for furaffinity user profiles"""
    pattern = BASE_PATTERN + r"/user/([^/?#]+)"
    example = "https://www.furaffinity.net/user/USER/"

    def items(self):
        base = self.root
        user = self.user + "/"
        return self._dispatch_extractors((
            (FuraffinityGalleryExtractor , f"{base}/gallery/{user}"),
            (FuraffinityScrapsExtractor  , f"{base}/scraps/{user}"),
            (FuraffinityFavoriteExtractor, f"{base}/favorites/{user}"),
            (FuraffinityJournalsExtractor, f"{base}/journals/{user}"),
        ), ("gallery",))


class FuraffinityFollowingExtractor(FuraffinityExtractor):
    """Extractor for a furaffinity user's watched users"""
    subcategory = "following"
    pattern = BASE_PATTERN + "/watchlist/by/([^/?#]+)"
    example = "https://www.furaffinity.net/watchlist/by/USER/"

    def items(self):
        url = f"{self.root}/watchlist/by/{self.user}/"
        data = {"_extractor": FuraffinityUserExtractor}

        while True:
            page = self.request(url).text

            for path in text.extract_iter(page, '<a href="', '"'):
                yield Message.Queue, self.root + path, data

            path = text.rextr(page, 'action="', '"')
            if url.endswith(path):
                return
            url = self.root + path


class FuraffinitySubmissionsExtractor(FuraffinityExtractor):
    """Extractor for new furaffinity submissions"""
    subcategory = "submissions"
    pattern = BASE_PATTERN + r"(/msg/submissions(?:/[^/?#]+)?)"
    example = "https://www.furaffinity.net/msg/submissions"

    def posts(self):
        self.user = None
        return self._pagination_submissions(self.root + self.groups[0])

    def _pagination_submissions(self, url):
        next_new = text.re(r">Next \d+</a>").search
        next_old = text.re(r">&gt;&gt;&gt; Next \d+ &gt;&gt;").search

        while True:
            page = self.request(url).text

            for post_id in text.extract_iter(page, 'id="sid-', '"'):
                yield post_id

            if not (m := next_new(page)) and not (m := next_old(page)):
                break
            path = text.rextr(page, 'href="', '"', m.start())
            url = self.root + text.unescape(path)
