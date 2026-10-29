# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://lensdump.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, util

BASE_PATTERN = r"(?:https?://)?lensdump\.com"


class LensdumpBase():
    """Base class for lensdump extractors"""
    category = "lensdump"
    root = "https://lensdump.com"

    def _init(self):
        self.cookies.set("ld_nsfw_ok", "1", domain="lensdump.com")

    def _pagination(self, page, begin, end):
        while True:
            yield from text.extract_iter(page, begin, end)

            pos = page.find(" data-load-more ")
            if pos < 0:
                break
            next = text.rextr(page, 'data-src="', '"', pos)
            if not next:
                break

            page = self.request(self.root + text.unescape(next)).text


class LensdumpAlbumExtractor(LensdumpBase, GalleryExtractor):
    subcategory = "album"
    pattern = BASE_PATTERN + r"/a/(\w+)(?:/?\?([^#]+))?"
    example = "https://lensdump.com/a/ID"

    def __init__(self, match):
        self.gallery_id, query = match.groups()
        if query:
            url = f"{self.root}/a/{self.gallery_id}/?{query}"
        else:
            url = f"{self.root}/a/{self.gallery_id}"
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        return {
            "gallery_id": self.gallery_id,
            "title": text.unescape(text.extr(
                page, 'property="og:title" content="', '"').strip())
        }

    def images(self, page):
        for image in self._pagination(page, '<a class="tile" ', '>'):

            data = util.json_loads(text.unquote(
                text.extr(image, "data-object='", "'") or
                text.extr(image, 'data-object="', '"')))
            image = data["image"]
            user = data.get("user")
            name = data.get("filename")

            image_id = name[:name.rfind(".")]
            image_url = image.get("url")
            image_title = data.get("title")
            if image_title is not None:
                image_title = text.unescape(image_title)

            yield (image_url, {
                "id"       : image_id,
                "url"      : image.get("url"),
                "title"    : image_title,
                "name"     : data.get("filename"),
                "filename" : image_id,
                "extension": data.get("extension"),
                "width"    : text.parse_int(data.get("width")),
                "height"   : text.parse_int(data.get("height")),
                "size"     : text.parse_int(image.get("size")),
                "user"     : user.get("username") if user else "",
            })


class LensdumpAlbumsExtractor(LensdumpBase, Extractor):
    """Extractor for album list from lensdump.com"""
    subcategory = "albums"
    pattern = BASE_PATTERN + r"/(?![ai]/)([^/?#]+)(?:/?\?([^#]+))?"
    example = "https://lensdump.com/USER"

    def items(self):
        user, query = self.groups
        url = f"{self.root}/{user}/"
        if query:
            params = text.parse_query(query)
        else:
            params = {"sort": "date_asc", "page": "1"}
        page = self.request(url, params=params).text

        base = self.root + "/a/"
        data = {"_extractor": LensdumpAlbumExtractor}
        for album_code in self._pagination(page, 'data-code="', '"'):
            yield Message.Queue, base + album_code, data


class LensdumpImageExtractor(LensdumpBase, Extractor):
    """Extractor for individual images on lensdump.com"""
    subcategory = "image"
    filename_fmt = "{category}_{id}{title:?_//}.{extension}"
    directory_fmt = ("{category}",)
    archive_fmt = "{id}"
    pattern = (r"(?:https?://)?(?:(?:i\d?\.)?lensdump\.com|\w\.l3n\.co)"
               r"/(?:i/)?(\w+)")
    example = "https://lensdump.com/i/ID"

    def items(self):
        key = self.groups[0]
        url = f"{self.root}/i/{key}"
        extr = text.extract_from(self.request(url).text)

        data = {
            "id"    : key,
            "title" : text.unescape(extr(
                'property="og:title" content="', '"')),
            "url"   : extr(
                'property="og:image" content="', '"'),
            "width" : text.parse_int(extr(
                'property="og:image:width" content="', '"')),
            "height": text.parse_int(extr(
                'property="og:image:height" content="', '"')),
            "date"  : self.parse_datetime_iso(extr('datetime="', '"')),
        }

        text.nameext_from_url(data["url"], data)
        yield Message.Directory, "", data
        yield Message.Url, data["url"], data
