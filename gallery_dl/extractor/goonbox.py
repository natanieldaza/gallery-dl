# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://goonbox.cr/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?goonbox\.cr"


class GoonboxExtractor(Extractor):
    """Base class for goonbox extractors"""
    category = "goonbox"
    root = "https://goonbox.cr"
    directory_fmt = ("{category}",
                     "{album[title]|''}{album[encoded_id]:? (/)/}")
    filename_fmt = "{num:?/ />03}{filename} ({encoded_id}).{extension}"
    archive_fmt = "{encoded_id}"

    def items(self):
        for img in self.images():
            try:
                url = img["original_url"]
            except Exception:
                continue

            img["date"] = self.parse_datetime_iso(
                img.get("created_at"))
            img["date_updated"] = self.parse_datetime_iso(
                img.get("updated_at"))

            if name := img.get("original_filename"):
                text.nameext_from_name(name, img)
                if not img["extension"]:
                    img["extension"] = text.ext_from_url(url)
            else:
                text.nameext_from_url(url, img)

            yield Message.Directory, "", img
            yield Message.Url, url, img


class GoonboxImageExtractor(GoonboxExtractor):
    subcategory = "image"
    pattern = BASE_PATTERN + r"/img/([^/?#]+)"
    example = "https://goonbox.cr/img/ID"

    def images(self):
        url = f"{self.root}/api/images/{self.groups[0].rpartition('.')[2]}"
        data = self.request_json(url)

        if "redirect" in data:
            url = data["redirect"]
            data = self.request_json(url)

        img = data["image"]
        img["count"] = 1
        img["num"] = 0

        if "album_nav" in data:
            try:
                nav = data["album_nav"]
                img["num"] = nav["total"] - nav["position"] + 1
            except Exception as exc:
                self.log.traceback(exc)

        return (img,)


class GoonboxAlbumExtractor(GoonboxExtractor):
    subcategory = "album"
    pattern = BASE_PATTERN + r"/a/([^/?#]+)"
    example = "https://goonbox.cr/a/ID"

    def images(self):
        url = f"{self.root}/api/albums/{self.groups[0].rpartition('.')[2]}"
        params = None
        num = 0

        while True:
            data = self.request_json(url, params=params)

            if "redirect" in data:
                url = data["redirect"]
                continue
            if "album" in data:
                album = data["album"]
                self.kwdict["album"] = album
                self.kwdict["count"] = num = album.get("images_count")

            for img in data["images"]:
                img["num"] = num
                num -= 1
                yield img

            try:
                pgn = data["pagination"]
                if pgn["current_page"] == pgn["last_page"]:
                    break
            except Exception:
                break

            if params is None:
                url += "/images"
                params = {"page": 2}
            else:
                params["page"] += 1


class GoonboxUserExtractor(GoonboxExtractor):
    subcategory = "user"
    directory_fmt = ("{category}", "{user[username]}")
    pattern = BASE_PATTERN + r"/u/([^/?#]+)"
    example = "https://goonbox.cr/u/USER"

    def images(self):
        url = f"{self.root}/api/users/{self.groups[0]}"
        self.kwdict["user"] = self.request_json(url)["user"]

        url += "/images"
        params = {"page": 1, "per_page": 100}
        num = None

        while True:
            data = self.request_json(url, params=params)
            pgn = data["pagination"]

            if num is None:
                self.kwdict["count"] = num = pgn["total"]

            for img in data["images"]:
                img["num"] = num
                num -= 1
                yield img

            if pgn["current_page"] >= pgn["last_page"]:
                break
            params["page"] += 1
