# -*- coding: utf-8 -*-

# Copyright 2016-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hentaihere.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text, util

BASE_PATTERN = r"(?:https?://)?(?:www\.)?hentaihere\.com"


class HentaihereBase():
    """Base class for hentaihere extractors"""
    category = "hentaihere"
    root = "https://hentaihere.com"

    def _manga_info(self, manga_id, page=None):
        if page is None:
            url = f"{self.root}/original/{manga_id}"
            page = self.request(url).text

        jsonld = self._extract_jsonld(page)[0]
        manga_url = jsonld.get("url")
        _, manga_type, manga_path = manga_url.rsplit("/", 2)

        return {
            "manga"       : jsonld.get("name"),
            "manga_id"    : manga_id,
            "manga_url"   : manga_url,
            "manga_slug"  : manga_path.partition("-")[2],
            "manga_cover" : jsonld.get("image"),
            "type"        : manga_type,
            "author"      : [a["name"] for a in jsonld.get("author") or ()],
            "tags"        : jsonld.get("genre"),
            "lang"        : jsonld.get("inLanguage"),
            "manga_date"  : self.parse_datetime_iso(
                jsonld.get("dateModified")),
        }


class HentaihereChapterExtractor(HentaihereBase, ChapterExtractor):
    """Extractor for a single manga chapter from hentaihere.com"""
    archive_fmt = "{chapter_id}_{page}"
    pattern = (BASE_PATTERN +
               r"(/reader/\d+(?:-[^/?#]*)?/\d+|/m/S\d+/[^/?#]+())")
    example = "https://hentaihere.com/reader/12345-TITLE/12345"

    def __init__(self, match):
        path, legacy = match.groups()
        url = f"{self.root}{path}/page-1" if legacy is None else None
        ChapterExtractor.__init__(self, match, url)

    def metadata(self, page):
        self.data = data = util.json_loads(text.extr(
            page, 'data-reader-data>', "<"))

        book = data["book"]
        if match := text.re(r"(\d+)(\S*)").search(book["chapter"]):
            chapter = match[1]
            minor = match[2]
        else:
            chapter = 0
            minor = ""

        h1 = text.extr(page, "<h1", "</h1>")
        return {
            **self.cache(self._manga_info, book["id"]),
            "chapter": text.parse_int(chapter),
            "chapter_minor": minor,
            "chapter_id": text.parse_int(
                data["chapterUrl"].rpartition("/")[2]),
            "title": text.unescape(h1[h1.find(":", h1.find("apter"))+2:]),
        }

    def images(self, page):
        images = self.data["images"]
        sizes = self.data["sizes"]
        return [
            (images[idx], {"width": sizes[idx][0], "height": sizes[idx][1]})
            for idx in range(len(images))
        ]


class HentaihereMangaExtractor(HentaihereBase, MangaExtractor):
    """Extractor for hmanga from hentaihere.com"""
    chapterclass = HentaihereChapterExtractor
    pattern = (BASE_PATTERN +
               r"(/(?:original|doujinshi)/(\d+)(?:-[^/?#]*)?|/m/S(\d+))")
    example = "https://hentaihere.com/original/12345-TITLE"

    def chapters(self, page):
        manga_id = text.parse_int(self.groups[1] or self.groups[2])
        manga = self.cache(self._manga_info, manga_id, page)

        latest = True
        results = []
        for opt in text.extract_iter(page, '<option value="', "/option>"):
            extr = text.extract_from(opt)
            chapter_id = text.parse_int(extr("", '"'))
            url = extr('data-read="', '"')
            chapter, sep, minor = extr(">Chapter ", " - ").partition(".")

            title = extr("", "<")
            if latest and title.endswith(" (latest)"):
                title = title[:-9]
                latest = False

            results.append((url, {
                **manga,
                "chapter": text.parse_int(chapter),
                "chapter_minor": sep + minor,
                "chapter_id": chapter_id,
                "title": text.unescape(title),
            }))
        return results
