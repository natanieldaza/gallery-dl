# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.xasiat.com"""

from .common import Extractor, Message
from .. import text, dt

BASE_PATTERN = r"(?:https?://)?(?:www\.)?xasiat\.com((?:/(fr|ja))?"


class XasiatExtractor(Extractor):
    category = "xasiat"
    root = "https://www.xasiat.com"

    def items(self):
        data = {"_extractor": (XasiatAlbumExtractor if self.groups[2] else
                               XasiatVideoExtractor)}
        for url in self.posts():
            yield Message.Queue, url, data

    def posts(self):
        return self._pagination(*self.groups)

    def _end_marker(self, lang):
        next = ("Next" if lang is None else
                "次へ" if lang == "ja" else "En avant")
        return f"><span>{next}</span><"

    def _pagination(self, path, lang, type, pnum=1):
        url = f"{self.root}{path}/"
        type = "video" if type is None else "album"
        params = {
            "mode"    : "async",
            "function": "get_block",
            "block_id": f"list_{type}s_common_{type}s_list",
            "sort_by" : "post_date",
            "from"    : pnum,
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest",
        }

        marker = self._end_marker(lang)
        find_posts = text.re(r'(?s)class="item  ">\s*<a href="([^"]+)').findall
        while True:
            params["_"] = int(dt.time.time() * 1000)

            page = self.request(url, params=params, headers=headers).text
            yield from find_posts(page)

            if marker in page:
                break
            params["from"] += 1


class XasiatAlbumExtractor(XasiatExtractor):
    subcategory = "album"
    directory_fmt = ("{category}", "{title}")
    archive_fmt = "{album_url}_{num}"
    pattern = BASE_PATTERN + r"/albums/(\d+)/[^/?#]+)"
    example = "https://www.xasiat.com/albums/12345/TITLE/"

    def items(self):
        path, lang, album_id = self.groups
        url = f"{self.root}{path}/"
        response = self.request(url)
        extr = text.extract_from(response.text)

        title = extr("<h1>", "<")
        info = extr('class="info-content"', "</div>")
        images = extr('class="images"', "</div>")

        urls = list(text.extract_iter(images, 'href="', '"'))
        categories = text.re(r'categories/[^"]+\">\s*(.+)\s*</a').findall(info)
        data = {
            "title": text.unescape(title),
            "model": text.re(
                r'top_models1"></i>\s*(.+)\s*</span').findall(info),
            "tags": text.re(
                r'tags/[^"]+\">\s*(.+)\s*</a').findall(info),
            "album_category": categories[0] if categories else "",
            "album_url": response.url,
            "album_id": text.parse_int(album_id),
            "count": len(urls),
            "lang": "en" if lang is None else lang,
        }

        yield Message.Directory, "", data
        for data["num"], url in enumerate(urls, 1):
            text.nameext_from_name(url.rsplit("/", 2)[1], data)
            yield Message.Url, url, data


class XasiatVideoExtractor(XasiatExtractor):
    subcategory = "video"
    directory_fmt = ("{category}",)
    filename_fmt = "{video_id} {title}.{extension}"
    archive_fmt = "{video_url}"
    pattern = BASE_PATTERN + r"/videos/(\d+)/[^/?#]+)"
    example = "https://www.xasiat.com/videos/12345/TITLE/"

    def items(self):
        path, lang, video_id = self.groups
        url = f"{self.root}{path}/"
        response = self.request(url)
        extr = text.extract_from(response.text)

        data = {
            "title": text.unescape(extr(
                'property="og:title" content="', '"')),
            "thumbnail": text.unescape(extr(
                'property="og:image" content="', '"')),
            "date": self.parse_datetime_iso(extr(
                'property="video:release_date" content="', '"')),
            "duration": text.parse_int(extr(
                'property="video:duration" content="', '"')),
            "views": text.parse_int(extr(
                '"userInteractionCount": "', '"')),
            "likes": text.parse_int(extr(
                '"userInteractionCount": "', '"')),
            "width": text.parse_int(extr(
                'property="og:video:width" content="', '"')),
            "height": text.parse_int(extr(
                'property="og:video:height" content="', '"')),
            "tags": extr('property="video:tag" content="', '"').split(", "),
            "video_url": response.url,
            "video_id": text.parse_int(video_id),
            "count": 1,
            "type": "video",
            "lang": "en" if lang is None else lang,
        }

        info = extr('class="info-content"', "</div>")

        if self.config("format") in {"SD", "sd", "480p"}:
            url = extr("video_url: '", "'")
            data["format"] = "SD"
        else:
            url = extr("video_alt_url: '", "'")
            data["format"] = "Best Quality"

        data["model"] = text.re(
            r'top_models1"></i>\s*(.+)\s*</span').findall(info)
        categories = text.re(
            r'categories/[^"]+\">\s*(.+)\s*</a').findall(info)
        data["video_category"] = categories[0] if categories else ""

        yield Message.Directory, "", data
        text.nameext_from_name(url.rsplit("/", 2)[1], data)
        yield Message.Url, url, data


class XasiatTagExtractor(XasiatExtractor):
    subcategory = "tag"
    pattern = BASE_PATTERN + r"/(albums/)?tags/[^/?#]+)"
    example = "https://www.xasiat.com/albums/tags/TAG/"


class XasiatCategoryExtractor(XasiatExtractor):
    subcategory = "category"
    pattern = BASE_PATTERN + r"/(albums/)?categories/[^/?#]+)"
    example = "https://www.xasiat.com/albums/categories/CATEGORY/"


class XasiatModelExtractor(XasiatExtractor):
    subcategory = "model"
    pattern = BASE_PATTERN + r"/(albums/)?models/[^/?#]+)"
    example = "https://www.xasiat.com/albums/models/MODEL/"


class XasiatSearchExtractor(XasiatExtractor):
    subcategory = "search"
    pattern = BASE_PATTERN + r"/(search/))([^/?#]+)"
    example = "https://www.xasiat.com/search/QUERY/"

    def _pagination(self, path, lang, type, query, pnum=1):
        url = f"{self.root}{path}{query}/"
        params = {
            "mode"    : "async",
            "function": "get_block",
            "block_id": "list_albums_albums_list_search_result",
            "q"       : text.unquote(query),
            "category_ids": "",
            "sort_by" : "",
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest",
        }

        marker = self._end_marker(lang)
        find_posts = text.re(r'class="item  ">\s*<a href="([^"]+)').findall
        while True:
            params["from_videos"] = pnum
            params["from_albums"] = pnum
            params["_"] = int(dt.time.time() * 1000),

            page = self.request(url, params=params, headers=headers).text
            yield from find_posts(page)

            if marker in page:
                break
            pnum += 1
