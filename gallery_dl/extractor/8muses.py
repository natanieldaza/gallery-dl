# -*- coding: utf-8 -*-

# Copyright 2019-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://comics.8muses.com/"""

from .common import Extractor, Message
from .. import text, util


class _8musesAlbumExtractor(Extractor):
    """Extractor for image albums on comics.8muses.com"""
    category = "8muses"
    subcategory = "album"
    directory_fmt = ("{category}", "{album[path]:I}")
    filename_fmt = "{page:>03}.{extension}"
    archive_fmt = "{hash}"
    root = "https://comics.8muses.com"
    pattern = (r"(?:https?://)?(?:comics\.|www\.)?8muses\.com"
               r"/(?:porn|comics)/(album/[^?#]+)(\?[^#]+)?")
    example = "https://comics.8muses.com/porn/album/PATH/TITLE"

    def items(self):
        path, params = self.groups
        if params is None:
            params = ""
        url = f"{self.root}/porn/{path}{params}"

        while True:
            data = self._unobfuscate(text.extr(
                self.request(url).text,
                'id="ractive-public" type="text/plain">', '</script>'))

            if images := data.get("pictures"):
                count = len(images)
                album = self._make_album(data["album"])
                yield Message.Directory, "", {"album": album, "count": count}
                for num, image in enumerate(images, 1):
                    url = f"{self.root}/image/fl/{image['publicUri']}"
                    img = {
                        "url"      : url,
                        "page"     : num,
                        "hash"     : image["publicUri"],
                        "count"    : count,
                        "album"    : album,
                        "extension": "jpg",
                    }
                    yield Message.Url, url, img

            if albums := data.get("albums"):
                for album in albums:
                    permalink = album.get("permalink")
                    if not permalink:
                        self.log.debug("Private album")
                        continue

                    url = f"{self.root}/porn/album/{permalink}"
                    yield Message.Queue, url, {
                        "url"       : url,
                        "name"      : (album.get("name") or
                                       album.get("displayName")),
                        "private"   : album.get("isPrivate"),
                        "_extractor": _8musesAlbumExtractor,
                    }

            if data["page"] >= data["pages"]:
                return
            tail, _, head = path.rstrip("/").rpartition("/")
            if head.isdecimal():
                path = tail
            url = f"{self.root}/porn/{path}/{data['page'] + 1}{params}"

    def _make_album(self, album):
        return {
            "id"     : album["id"],
            "path"   : album["path"].split("/"),
            "title"  : album["name"],
            "private": album["isPrivate"],
            "url"    : f"{self.root}/porn/album/{album['permalink']}",
            "parent" : text.parse_int(album["parentId"]),
            "views"  : text.parse_int(album["numberViews"]),
            "likes"  : text.parse_int(album["numberLikes"]),
            "date"   : self.parse_datetime_iso(album["updatedAt"]),
        }

    def _unobfuscate(self, data):
        return util.json_loads("".join([
            chr(33 + (ord(c) + 14) % 94) if "!" <= c <= "~" else c
            for c in text.unescape(data.strip("\t\n\r !"))
        ]))
