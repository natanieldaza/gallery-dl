# -*- coding: utf-8 -*-

# Copyright 2025-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://mangafire.to/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?mangafire\.to"


class MangafireBase():
    """Base class for mangafire extractors"""
    category = "mangafire"
    root = "https://mangafire.to"

    def _manga_info(self, manga_id):
        manga = self.request_api("/titles/" + manga_id)["data"]

        manga["manga"] = manga.pop("title")
        manga["manga_id"] = manga.pop("id")
        manga["manga_hid"] = manga.pop("hid")
        manga["manga_slug"] = manga.pop("slug")
        manga["manga_titles"] = manga.pop("altTitles")
        manga["cover"] = manga.pop("poster")["large"]
        manga["description"] = text.unescape(text.remove_html(
            manga.pop("synopsisHtml")))
        manga["author"] = [t["title"] for t in manga.pop("authors") or ()]
        manga["artist"] = [t["title"] for t in manga.pop("artists") or ()]
        manga["themes"] = [t["title"] for t in manga.pop("themes") or ()]
        manga["tags"] = [t["title"] for t in manga.pop("genres") or ()]
        manga["demographic"] = [
            t["title"] for t in manga.pop("demographics") or ()]

        return manga

    def _chapter_info(self, info):
        chapter_info = str(info["number"])
        type = info.get("type")

        if info.get("type") == "volume":
            return {
                "volume"        : info["number"],
                "volume_id"     : info.get("id", 0),
                "chapter"       : 0,
                "chapter_minor" : "",
                "chapter_string": chapter_info,
                "chapter_id"    : info.get("id", 0),
                "chapter_type"  : type,
                "official"      : (type.lower() == "official"),
                "title"         : info.get("name"),
                "lang"          : info.get("language"),
            }

        chapter, sep, minor = chapter_info.partition(".")
        return {
            "chapter"       : text.parse_int(chapter),
            "chapter_minor" : sep + minor,
            "chapter_string": chapter_info,
            "chapter_id"    : info.get("id", 0),
            "chapter_type"  : type,
            "official"      : (type.lower() == "official"),
            "title"         : info.get("name"),
            "lang"          : info.get("language"),
            "date"          : self.parse_timestamp(info.get("createdAt")),
        }

    def request_api(self, endpoint, params=None):
        if params is None:
            endpoint = f"{endpoint}?vrf={self.utils('vrf').generate(endpoint)}"
        else:
            endpoint = f"{endpoint}?{text.build_query(params)}"
            endpoint = f"{endpoint}&vrf={self.utils('vrf').generate(endpoint)}"
        return self.request_json(f"{self.root}/api{endpoint}", headers={
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
        })


class MangafireChapterExtractor(MangafireBase, ChapterExtractor):
    """Extractor for mangafire manga chapters"""
    directory_fmt = (
        "{category}", "{manga}",
        "{volume:?v/ />02}{chapter:?c//>03}{chapter_minor:?//}{title:?: //}")
    filename_fmt = (
        "{manga}{volume:?_v//>02}{chapter:?_c//>03}{chapter_minor:?//}_"
        "{page:>03}.{extension}")
    archive_fmt = (
        "{manga_id}_{chapter_id}_{page}")
    pattern = (BASE_PATTERN + r"/(?:title|manga)/(\w+)[\w-]*"
               r"/(chapter|volume)/(\d+)")
    example = "https://mangafire.to/title/ID-MANGA/chapter/123"

    def metadata(self, _):
        manga_id, type, chapter_id = self.groups

        try:
            ch = self.request_api(f"/{type}s/{chapter_id}")["data"]
            self.pages = ch.pop("pages")
        except Exception:
            raise self.exc.NotFoundError("chapter")

        return {
            **self.cache(self._manga_info, manga_id),
            **self._chapter_info(ch),
        }

    def images(self, page):
        return [
            (page.pop("url"), page)
            for page in self.pages
        ]


class MangafireMangaExtractor(MangafireBase, MangaExtractor):
    """Extractor for mangafire manga"""
    chapterclass = MangafireChapterExtractor
    pattern = BASE_PATTERN + r"/(?:title|manga)/(\w+)"
    example = "https://mangafire.to/title/ID-MANGA"

    def chapters(self, page):
        manga_id = self.groups[0]
        manga = self.cache(self._manga_info, manga_id)
        base = f"{self.root}{manga['url']}/chapter/"

        endpoint = f"/titles/{manga_id}/chapters"
        # for VRF generation,
        # query parameters MUST be in lexicographical order
        params = {
            "language": self.config("lang") or "en",
            "limit": "200",
            "order": "desc",
            "page" : 1,
            "sort" : "number",
        }

        results = []
        while True:
            data = self.request_api(endpoint, params)

            for ch in data["items"]:
                results.append((base + str(ch["id"]), {
                    **manga,
                    **self._chapter_info(ch),
                }))

            try:
                if not data["meta"]["hasNext"]:
                    break
            except Exception:
                break

            params["page"] += 1
        return results
