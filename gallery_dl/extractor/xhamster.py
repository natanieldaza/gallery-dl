# -*- coding: utf-8 -*-

# Copyright 2019-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://xhamster.com/"""

from .common import Extractor, Message
from .. import text, util

BASE_PATTERN = (r"(?:https?://)?((?:[\w-]+\.)?xhamster"
                r"(?:\d?\.(?:com|one|desi)|\.porncache\.net))")


class XhamsterExtractor(Extractor):
    """Base class for xhamster extractors"""
    category = "xhamster"

    def __init__(self, match):
        self.root = "https://" + match[1]
        Extractor.__init__(self, match)


class XhamsterGalleryExtractor(XhamsterExtractor):
    """Extractor for image galleries on xhamster.com"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{user[name]}",
                     "{gallery[id]} {gallery[title]}")
    filename_fmt = "{num:>03}_{id}.{extension}"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"(/photos/gallery/[^/?#]+)"
    example = "https://xhamster.com/photos/gallery/12345"

    def items(self):
        data = self.metadata()
        yield Message.Directory, "", data
        for num, image in enumerate(self.images(), 1):
            url = image["imageURL"]
            image.update(data)
            text.nameext_from_url(url, image)
            image["num"] = num
            image["extension"] = "webp"
            yield Message.Url, url, image

    def metadata(self):
        data = self.data = self._extract_data(self.root + self.groups[1])

        gallery = data["galleryPage"]
        info = gallery["infoProps"]
        author = info["authorInfoProps"]
        user = info["subscribeButtonProps"]
        crumbs = gallery["breadCrumbsProps"]["breadCrumbs"]
        photos = gallery["photoItems"]

        return {
            "user":
            {
                "id"         : text.parse_int(user["id"]),
                "url"        : author["authorLink"],
                "name"       : author["authorName"],
                "verified"   : True if author.get("verified") else False,
                "subscribers": user["subscribers"],
            },
            "gallery":
            {
                "id"         : text.parse_int(gallery["id"]),
                "tags"       : [t["label"] for t in info["categoriesTags"]],
                "date"       : self.parse_timestamp(author["createdDate"]),
                "views"      : text.parse_int(info["viewsInfoProps"]["views"]),
                "title"      : crumbs[-1]["name"] if crumbs else "",
                "description": info["description"],
                "thumbnail"  : photos[0]["imgSrcset"] if photos else "",
            },
            "count": text.parse_int(gallery["photosCount"]),
        }

    def images(self):
        data = self.data
        self.data = None

        while True:
            for photo in data["galleryPage"]["photoItems"]:
                yield {
                    "id"      : photo["id"],
                    "imageURL": photo["imgSrc"],
                    "thumbURL": photo["imgSrcset"],
                    "pageURL" : photo["link"],
                    "comments": photo["commentsCount"],
                    "width"   : photo["originWidth"],
                    "height"  : photo["originHeight"],
                }

            pagination = data["galleryPage"]["paginationProps"]
            if pagination["currentPageNumber"] >= pagination["lastPageNumber"]:
                return
            url = (pagination["pageLinkTemplate"][:-3] +
                   str(pagination["currentPageNumber"] + 1))

            data = self._extract_data(url)

    def _extract_data(self, url):
        page = self.request(url).text
        return util.json_loads(text.extr(
            page, "window.initials=", "</script>").rstrip("\n\r;"))


class XhamsterUserExtractor(XhamsterExtractor):
    """Extractor for all galleries of an xhamster user"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/users/([^/?#]+)(?:/photos)?/?(?:$|[?#])"
    example = "https://xhamster.com/users/USER/photos"

    def items(self):
        url = f"{self.root}/users/{self.groups[1]}/photos"
        data = {"_extractor": XhamsterGalleryExtractor}

        while url:
            extr = text.extract_from(self.request(url).text)
            while True:
                url = extr(' role-pop" href="', '"')
                if not url:
                    break
                yield Message.Queue, url, data
            url = extr('data-page="next" href="', '"')
