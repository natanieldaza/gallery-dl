# -*- coding: utf-8 -*-

# Copyright 2016-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hentai2read.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text, util

BASE_PATTERN = r"(?:https?://)?(?:www\.)?hentai2read\.com"


class Hentai2readBase():
    """Base class for hentai2read extractors"""
    category = "hentai2read"
    root = "https://hentai2read.com"

    def _manga_info(self, manga_id, page=None):
        if page is None:
            url = f"{self.root}/original/{manga_id}"
            page = self.request(url).text

        data = self._extract_data(page)
        book = data["book"]
        manga_url = book.get("url") or ""
        jsonld = data.get("jsonLd")[0]

        return {
            "manga"       : book.get("title"),
            "manga_id"    : book.get("id"),
            "manga_url"   : self.root + manga_url,
            "manga_slug"  : manga_url[manga_url.find("-")+1:],
            "manga_cover" : book.get("cover"),
            "description" : book.get("description"),
            "type"        : book["type"]["label"],
            "status"      : book["status"]["label"],
            "author"      : [a["name"] for a in jsonld.get("author") or ()],
            "tags"        : jsonld.get("genre"),
            "lang"        : jsonld.get("inLanguage"),
            "manga_date"  : self.parse_datetime_iso(
                jsonld.get("dateModified")),
        }

    def _extract_data(self, page):
        return util.json_loads(text.extr(
            page, 'data-page="app" type="application/json">', "<"))["props"]


class Hentai2readChapterExtractor(Hentai2readBase, ChapterExtractor):
    """Extractor for a single manga chapters from hentai2read.com"""
    archive_fmt = "{chapter_id}_{page}"
    pattern = BASE_PATTERN + r"(/reader/\d+(?:-[^/?#]*)?/\d+)"
    example = "https://hentai2read.com/reader/12345-TITLE/12345"

    def metadata(self, page):
        self.data = data = self._extract_data(page)
        ch = data["chapter"]
        chapter, sep, minor = ch["number"].partition(".")
        return {
            **self.cache(self._manga_info, data["book"]["id"]),
            "chapter": text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "chapter_id": ch["id"],
            "title": ch["label"].partition(": ")[2],
        }

    def images(self, page):
        return [(url, None) for url in self.data["images"]]


class Hentai2readMangaExtractor(Hentai2readBase, MangaExtractor):
    """Extractor for hmanga from hentai2read.com"""
    chapterclass = Hentai2readChapterExtractor
    pattern = (BASE_PATTERN +
               r"(/((?:original|doujinshi)/\d+(?:-[^/?#]*)?|[^/?#]+))")
    example = "https://hentai2read.com/original/12345-TITLE/"

    def chapters(self, page):
        data = self._extract_data(page)
        manga = self.cache(self._manga_info, data["book"]["id"], page)

        results = []
        for ch in data["chapters"]:
            chapter, sep, minor = ch["number"].partition(".")
            results.append((self.root + ch["url"], {
                **ch,
                **manga,
                "chapter": text.parse_int(chapter),
                "chapter_minor": sep + minor,
                "chapter_id": ch["id"],
                "date": self.parse_datetime(ch["date"], "%b %d, %Y"),
            }))
        return results
