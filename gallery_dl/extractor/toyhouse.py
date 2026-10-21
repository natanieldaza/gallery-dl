# -*- coding: utf-8 -*-

# Copyright 2022-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://toyhou.se/"""

from .common import Extractor, Message
from .. import text, util

BASE_PATTERN = r"(?:https?://)?(?:www\.)?toyhou\.se"


class ToyhouseExtractor(Extractor):
    """Base class for toyhouse extractors"""
    category = "toyhouse"
    root = "https://toyhou.se"
    directory_fmt = ("{category}", "{user|artists!S}")
    archive_fmt = "{id}"

    def _init(self):
        self.offset = 0

    def items(self):
        for post in util.advance(self.posts(), self.offset):
            text.nameext_from_url(post["url"], post)
            post["id"], _, post["hash"] = post["filename"].partition("_")
            yield Message.Directory, "", post
            yield Message.Url, post["url"], post

    def skip_files(self, num):
        self.offset += num
        return num

    def _parse_post(self, post, needle=' href="'):
        extr = text.extract_from(post)
        data = {
            "url": extr(needle, '"'),
            "detail": "\n".join(text.split_html(extr(
                'class="image-detail', 'class="image-credit'))[2:-2]),
            "date": (v := extr('', "</div")) and
            self.parse_datetime(
                v[v.find('mb-1">')+6:], "%d %b %Y, %I:%M:%S %p"),
            "artists": self._split(extr(
                '<div class="artist-credit',
                '<div class="image-character'), "</div>", " "),
            "characters": self._split(
                extr('', 'class="image-') or
                extr('', 'id="footer"') or
                extr('', '\n                </div>'), "</a>", ""),
        }

        url = data["url"]
        data["status"] = ("watermark" if "/watermarks/" in url else
                          "thumbnail" if "/thumbnails/" in url else "original")
        return data

    def _split(self, html, end, ws):
        return [
            text.unescape(text.remove_html(item[item.find(">")+1:], ws, ws))
            for item in text.extract_iter(html, "<a", end)
        ]

    def _pagination(self, url):
        params = {"page": 1}

        while True:
            page = self.request(url, params=params).text

            if params["page"] == 1:
                if self._check_content_warning(page):
                    continue
                self._extract_webpage(page)

            cnt = 0
            for post in text.extract_iter(
                    page, '<li class="gallery-item">', '</li>'):
                cnt += 1
                yield self._parse_post(post)

            if cnt < 18:
                break
            params["page"] += 1

    def _extract_webpage(self, page):
        extr = text.extract_from(page)
        kw = self.kwdict
        if user := extr('class="user-name">', '</'):
            kw["user"] = text.extr(user, 'href="https://toyhou.se/', '"')
            kw["display_name"] = text.unescape(user[user.rfind(">")+1:])
        if folder := extr('class="character-folder', '</a'):
            kw["folder"] = text.unescape(folder[folder.rfind(">")+1:])
            kw["folder_id"] = text.extr(folder, '/folder:', '"')
        if char := extr('class="character-name">', '</'):
            kw["character"] = text.unescape(char[char.rfind(">")+1:])
            kw["character_id"], _, kw["character_slug"] = text.extr(
                char, ' href="/', '"').partition(".")
        if tab := self.groups[1]:
            if tab[0] == "/":
                kw["variant_id"] = tid = tab[1:tab.find(".")]
                kw["variant_slug"] = extr(f"/{tid}.", '/')
            else:
                kw["tab_id"] = tid = tab[:tab.find(".")]
                kw["tab_slug"] = extr(f"/{tid}.", '"')
                kw["tab"] = text.unescape(extr("</i>", "<").strip())

    def _check_content_warning(self, page):
        if ">Content Warning<" not in page:
            return False

        data = {
            text.extr(input, 'name="', '"'): text.unescape(
                text.extr(input, 'value="', '"'))
            for input in text.extract_iter(page, "<input ", ">")
        }

        if not data.get("_token"):
            return False
        self.log.info("Accepting 'Content Warning'")
        self.request(self.root + "/~account/warnings/accept",
                     method="POST", data=data, allow_redirects=False)
        return True


class ToyhouseArtExtractor(ToyhouseExtractor):
    """Extractor for artworks of a toyhouse user"""
    subcategory = "art"
    pattern = BASE_PATTERN + r"/([^/?#]+)/art"
    example = "https://www.toyhou.se/USER/art"

    def posts(self):
        return self._pagination(f"{self.root}/{self.groups[0]}/art")

    def _extract_webpage(self, page):
        if user := text.extr(page, 'class="display-user', '</'):
            kw = self.kwdict
            kw["user"] = text.extr(user, 'href="https://toyhou.se/', '"')
            kw["display_name"] = text.unescape(user[user.rfind(">")+1:])


class ToyhouseCharacterGalleryExtractor(ToyhouseExtractor):
    """Extractor for a toyhouse character's gallery"""
    subcategory = "character-gallery"
    directory_fmt = ("{category}", "{user}", "Characters",
                     "{character} ({character_id})",
                     "{tab:?//}{tab_id:? (/)/}")
    pattern = BASE_PATTERN + r"/(\d+\.[\w-]*)/(?:(\d+\.[\w-]*)/)?gallery"
    example = "https://www.toyhou.se/12345.CHARACTER/gallery"

    def posts(self):
        char, tab = self.groups
        if tab is None:
            url = f"{self.root}/{char}/gallery"
        else:
            cid, _, cname = char.partition(".")
            url = f"{self.root}/{cid}.{cname or 'name'}/{tab}/gallery"
        return self._pagination(url)


class ToyhouseImageExtractor(ToyhouseExtractor):
    """Extractor for individual toyhouse images"""
    subcategory = "image"
    pattern = (r"(?:https?://)?(?:"
               r"(?:www\.)?toyhou\.se/"
               r"(~images|\d+\.[\w-]*(/\d+\.[\w-]*)?)|"
               r"f\d+\.toyhou\.se/file/[^/?#]+/(?:image|watermark|thumbnail)s"
               r")/(\d+)")
    example = "https://toyhou.se/~images/12345"

    def posts(self):
        path, tab, image_id = self.groups
        if path is None:
            path = "~images"
        url = f"{self.root}/{path}/{image_id}"
        response = self.request(url)
        page = response.text
        if self._check_content_warning(page):
            page = self.request(response.url).text
        self._extract_webpage(page)
        return (self._parse_post(page, '<img class="mw-100" src="'),)
