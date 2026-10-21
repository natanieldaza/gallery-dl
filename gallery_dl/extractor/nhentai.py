# -*- coding: utf-8 -*-

# Copyright 2015-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://nhentai.net/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, util
import collections
import random

BASE_PATTERN = r"(?:https?://)?nhentai\.net"


class NhentaiExtractor(Extractor):
    """Base class for nhentai extractors"""
    category = "nhentai"
    root = "https://nhentai.net"

    def _init(self):
        if api_key := self.config("api-key"):
            self.headers_api = {"Authorization": "Key " + api_key}
        else:
            self.headers_api = None

    def items(self):
        for gallery in self.galleries():
            url = f"{self.root}/g/{gallery['id']}/"
            gallery["_extractor"] = NhentaiGalleryExtractor
            yield Message.Queue, url, gallery

    def request_api(self, endpoint, params=None):
        url = f"{self.root}/api/v2{endpoint}"
        return self.request_json(url, params=params, headers=self.headers_api)

    def _pagination(self, endpoint, params):
        params["page"] = text.parse_int(params.get("page"), 1)

        while True:
            data = self.request_api(endpoint, params)

            yield from data["result"]

            if params["page"] >= data["num_pages"]:
                break
            params["page"] += 1


class NhentaiGalleryExtractor(GalleryExtractor, NhentaiExtractor):
    """Extractor for image galleries from nhentai.net"""
    pattern = BASE_PATTERN + r"/g/(\d+)"
    example = "https://nhentai.net/g/12345/"

    def metadata(self, _):
        self.data = data = self.request_api("/galleries/" + self.groups[0])

        title = data["title"]
        title_en = title.get("english", "")
        title_ja = title.get("japanese", "")

        info = collections.defaultdict(list)
        for tag in data["tags"]:
            info[tag["type"]].append(tag["name"])

        language = ""
        for language in info["language"]:
            if language != "translated":
                language = language.capitalize()
                break

        return {
            "title"     : title_en or title_ja,
            "title_en"  : title_en,
            "title_ja"  : title_ja,
            "title_pretty": title.get("pretty", ""),
            "gallery_id": data["id"],
            "media_id"  : text.parse_int(data["media_id"]),
            "date"      : self.parse_timestamp(data["upload_date"]),
            "scanlator" : info.get("scanlator", ""),
            "artist"    : info["artist"],
            "group"     : info["group"],
            "parody"    : info["parody"],
            "characters": info["character"],
            "tags"      : info["tag"],
            "type"      : info["category"][0] if "category" in info else "",
            "lang"      : util.language_to_code(language),
            "language"  : language,
        }

    def images(self, _):
        return [
            (f"https://i{random.randint(1, 4)}.nhentai.net/{page['path']}", {
                "width" : page["width"],
                "height": page["height"],
            })
            for page in self.data["pages"]
        ]


class NhentaiTagExtractor(NhentaiExtractor):
    """Extractor for nhentai tag searches"""
    subcategory = "tag"
    pattern = (BASE_PATTERN +
               r"/(artist|category|character|group|language|parody|tag)"
               r"/([^/?#]+)(?:/(popular[^/?#]*))?/?(?:\?([^#]+))?")
    example = "https://nhentai.net/tag/TAG/"

    def galleries(self):
        tag_type, slug, sort_path, qs = self.groups
        self.kwdict["search_tags"] = tag = self.request_api(
            f"/tags/{tag_type}/{slug}")

        params = text.parse_query(qs)
        return self._pagination("/galleries/tagged", {
            "tag_id": tag["id"],
            "sort"  : params.get("sort") or sort_path,
        })


class NhentaiSearchExtractor(NhentaiExtractor):
    """Extractor for nhentai search results"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/search/?\?([^#]+)"
    example = "https://nhentai.net/search/?q=QUERY"

    def galleries(self):
        params = text.parse_query(self.groups[0])
        return self._pagination("/search", {
            "query": params.get("q"),
            "sort" : params.get("sort"),
            "page" : params.get("page"),
        })


class NhentaiFavoriteExtractor(NhentaiExtractor):
    """Extractor for nhentai favorites"""
    subcategory = "favorite"
    pattern = BASE_PATTERN + r"/favorites/?(?:\?([^#]+))?"
    example = "https://nhentai.net/favorites/"

    def galleries(self):
        params = text.parse_query(self.groups[0])
        return self._pagination("/favorites", {
            "q"   : params.get("q"),
            "page": params.get("page"),
        })
