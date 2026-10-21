# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://kagane.org/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?kagane\.(?:si|cx|moe|net|to|org)"


class KaganeBase():
    """Base class for kagane extractors"""
    category = "kagane"
    root = root_api = "https://kagane.si"

    def __init__(self, match):
        self.root = self.root_api = text.root_from_url(match[0])
        super().__init__(match)

    def _integrity(self):
        return self.request_json(
            f"{self.root}/api/integrity", method="POST")["token"]

    def _manga_info(self, sid):
        data = self.request_json(f"{self.root_api}/api/v2/series/{sid}")

        return {
            "manga_id": data["series_id"],
            "manga": data["title"],
            "manga_alt": [
                alt["title"]
                for alt in data["series_alternate_titles"]
            ],
            "type": data["format"],
            "content_rating": data["age_rating"],
            "status": data["publication_status"],
            "rating": data["average_rating"],
            "manga_date": self.parse_datetime_iso(data.get("created_at")),
            "genres": [g["genre_name"] for g in data.get("genres") or ()],
            "tags": [t["tag_name"] for t in data.get("tags") or ()],
            "lang": "en",
            "language": "English",
        }


class KaganeChapterExtractor(KaganeBase, ChapterExtractor):
    """Extractor for kagane manga chapters"""
    pattern = BASE_PATTERN + r"(/series/([\w-]+)/reader/([\w-]+))"
    example = "https://kagane.si/series/MANGA_ID/reader/CHAPTER_ID"

    def metadata(self, page):
        chstr = text.unescape(text.extr(
            page, 'property="og:title" content="', '"'))

        match = text.re(
            r"\s+-\s+"
            r"(?:[Vv]olume\s*(\d+)\s*)?"
            r"[Cc]hapter\s*(\d+)([^\s]*)?"
            r"(?:\s+-\s+(?:[Cc]h(?:apter|\.) [^\s]+(?:\s+-)?\s*)?(.+))?$"
        ).search(chstr)
        volume, chapter, minor, title = match.groups()

        return {
            **self.cache(self._manga_info, self.groups[1][-36:]),
            "chapter_id": self.groups[2],
            "title": title or "",
            "volume": text.parse_int(volume),
            "chapter": text.parse_int(chapter),
            "chapter_minor": minor,
            "chapter_string": chstr,
        }

    def images(self, page):
        cid = self.groups[2][-36:]
        url = f"{self.root_api}/api/v2/books/{cid}"
        headers = {"x-integrity-token": self.cache(
            self._integrity, _key=None, _exp=300, _mem=False)}
        resp = self.request_json(url, method="POST", headers=headers)

        return [
            (f"{resp['cache_url']}/api/v2/books/page/{cid}/{data['page_id']}"
             f".{data['ext']}?token={resp['access_token']}", data)
            for data in resp["manifest"]["pages"]
        ]


class KaganeMangaExtractor(KaganeBase, MangaExtractor):
    """Extractor for kagane manga"""
    chapterclass = KaganeChapterExtractor
    reverse = False
    pattern = BASE_PATTERN + r"/series/([\w-]+)"
    example = "https://kagane.si/series/MANGA_ID"

    def chapters(self, page):
        mid = self.groups[0][-36:]
        manga = self.cache(self._manga_info, mid)
        base = f"{self.root}/series/{mid}/reader/"

        url = f"{self.root_api}/api/v2/series/{mid}/books/index?fields=List"
        cinfo = self.request_json(url)

        #  0	"book_id"
        #  1	"sort_no"
        #  2	"chapter_no"
        #  3	"volume_no"
        #  4	"group_ix"
        #  5	"released_at"
        #  6	"title"
        #  7	"page_count"
        #  8	"published_on"
        #  9	"internal_release"

        results = []
        for ch in cinfo["books"]:
            chapter, sep, minor = ch[2].partition(".")
            results.append((base + ch[0], {
                **manga,
                "volume": text.parse_int(ch[3]),
                "chapter": text.parse_int(chapter),
                "chapter_minor": sep + minor,
                "chapter_id": ch[0],
                "date": self.parse_timestamp(ch[5]),
            }))
        return results
