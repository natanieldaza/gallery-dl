# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.dcinside.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text


class DcinsideGalleryExtractor(GalleryExtractor):
    category = "dcinside"
    subcategory = "gallery"
    root = "https://gall.dcinside.com"
    directory_fmt = ("{category}", "{username}")
    filename_fmt = "{id} {title} {num:>02}.{extension}"
    archive_fmt = "{id}_{num}"
    pattern = (r"(?:https?://)?gall\.dcinside\.com"
               r"(/(?:mgallery/)?board/view/?\?([^#]+))")
    example = "https://gall.dcinside.com/board/view/?id=ID&no=12345"

    def metadata(self, page):
        # potentially invalid JSON-LD due to unescaped " quotes
        # -> extract data manually
        extr = text.extract_from(page)
        params = text.parse_query(self.groups[1])

        return {
            "id"      : text.parse_int(params.get("no")),
            "board"   : params.get("id"),
            "title"   : extr('"headline":"', '",\r'),
            "content" : extr('"articleBody":"', '",\r'),
            "date"    : self.parse_datetime_iso(extr(
                '"datePublished":"', '"')),
            "display_name" : extr('"name":"', '",\r'),
            "username"     : extr('"url":"https://gallog.dcinside.com/', '"'),
            "comments"     : text.parse_int(extr(
                '"userInteractionCount": ', ' ')),
            "views"        : text.parse_int(extr(
                '"userInteractionCount": ', ' ')),
            "_http_headers": {"Accept-Encoding": "identity"},
        }

    def images(self, page):
        if write_div := text.extr(page, 'class="write_div', "</div>"):
            results = []
            for img in text.extract_iter(write_div, "<img", ">"):
                url = text.unescape(text.extr(img, ' data-original="', '"') or
                                    text.extr(img, ' src="', '"') or
                                    text.extr(img, " src='", "'"))
                results.append((url, {
                    "hash"     : text.extr(img, ' alt="', '"'),
                    "extension": "jpg",
                }))
            return results

        if image := text.extr(page, '"image":{', '}'):
            url = text.extr(image, '"URL":"', '"')
            return ((url, {"extension": "jpg"}),)


class DcinsideUserExtractor(Extractor):
    category = "dcinside"
    subcategory = "user"
    root = "https://gallog.dcinside.com"
    pattern = (r"(?:https?://)?gallog\.dcinside\.com/([^/?#]+)"
               r"(?:(/posting(?:/index)?)/?\?([^#]+))?")
    example = "https://gallog.dcinside.com/USER"

    def items(self):
        username, path, query = self.groups
        url = f"{self.root}/{username}{path or '/posting'}"
        params = text.parse_query(query)
        params["p"] = text.parse_int(params.get("p"), 1)

        data = {"_extractor": DcinsideGalleryExtractor}
        while True:
            page = self.request(url, params=params).text

            for href in text.extract_iter(
                    page, '<a class="link " href="', '"'):
                yield Message.Queue, text.unescape(href), data

            if "</em><a href=" not in page:
                break
            params["p"] += 1
