# -*- coding: utf-8 -*-

# Copyright 2019-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://500px.com/"""

from .common import Extractor, Message
from .. import text, util

BASE_PATTERN = r"(?:https?://)?(?:web\.)?500px\.com"


class _500pxExtractor(Extractor):
    """Base class for 500px extractors"""
    category = "500px"
    directory_fmt = ("{category}", "{user[username]}",
                     "{group[title]:?//}{group[id]:? (/)/}")
    filename_fmt = ("{num:?/ />02}{date:%Y-%m-%d} "
                    "{title:?/ /}({id}).{extension}")
    archive_fmt = "{id}"
    root = "https://500px.com"
    cookies_domain = ".500px.com"
    _warning = True

    def _init(self):
        self.headers = {"x-500px-platform": "Web"}

        name = "x-500px-device-id-prod"
        if value := self.cookies.get(name, domain=self.cookies_domain):
            self.headers[name] = value
        else:
            self.headers[name] = value = util.generate_uuid()
            self.cookies.set(name, value, domain=self.cookies_domain)

        name = "x-500px-csrf-token-prod"
        if value := self.cookies.get(name, domain=self.cookies_domain):
            self.headers[name] = value
        else:
            self.headers[name] = value = util.generate_token(43)
            self.cookies.set(name, value, domain=self.cookies_domain)

        if self._warning:
            if not self.cookies_check(("x-500px-access-token-prod",)):
                self.log.warning("no 'x-500px-access-token-prod' cookie set")
                self.log.warning("image dimensions restricted to 1024px")
            _500pxExtractor._warning = False

    def items(self):
        seen = set()

        for photo in self.photos():
            type = photo.get("__typename")
            if type == "PhotoGroup":
                group = photo

                variables = {
                    "excludeNsfw": False,
                    "groupId"    : group["id"],
                }
                photos = self.request_graphql("getPhotosByGroupId", variables)

                data = {
                    "group": group,
                    "count": len(photos),
                    "user" : group.pop("uploader"),
                    "type" : "group",
                }

                yield Message.Directory, "", data
                for num, photo in enumerate(photos, 1):
                    seen.add(photo["id"])
                    url = photo["urls"]["size_4k"]
                    photo.update(data)
                    photo["num"] = num
                    photo["type"] = "photo"
                    photo["id_num"] = url.rsplit("/", 2)[1]
                    photo["date"] = self.parse_datetime_iso(
                        photo["uploadedAt"])
                    photo["date_taken"] = self.parse_datetime_iso(
                        photo["takenAt"])
                    text.nameext_from_url(url, photo)
                    yield Message.Url, url, photo
            elif photo["id"] not in seen:
                if type == "Video":
                    url = photo["videoUrl"]
                    photo["type"] = "video"
                else:
                    url = photo["urls"]["size_4k"]
                    photo["type"] = "photo"
                    photo["date_taken"] = self.parse_datetime_iso(
                        photo["takenAt"])

                photo["num"] = 0
                photo["count"] = 1
                photo["id_num"] = url.rsplit("/", 2)[1]
                photo["date"] = self.parse_datetime_iso(photo["uploadedAt"])
                text.nameext_from_url(url, photo)
                yield Message.Directory, "", photo
                yield Message.Url, url, photo

    def request_graphql(self, opname, variables):
        url = "https://api-neo.500px.com/graphql"
        headers = {
            **self.headers,
            "Accept": "application/graphql-response+json,"
                      "application/json;q=0.9",
            "content-type": "application/json",
        }
        body = {
            "operationName": opname,
            "variables"    : variables,
            "extensions"   : {"clientLibrary": {
                "name"     : "@apollo/client",
                "version"  : "4.1.6",
            }},
            "query"        : self.utils("graphql", opname),
        }
        self.log.debug("%s\n%s", opname, variables)
        return self.request_json(
            url, method="POST", headers=headers, json=body,
        )["data"].popitem()[1]

    def _pagination(self, opname, variables):
        while True:
            data = self.request_graphql(opname, variables)

            if data.__class__ is list:
                yield from data
            else:
                for edge in data["edges"]:
                    yield edge["node"]

            info = data.get("pageInfo")
            if not info or not info.get("hasNextPage"):
                break
            variables["after"] = info["endCursor"]


class _500pxUserExtractor(_500pxExtractor):
    """Extractor for photos from a user's photostream on 500px.com"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/(?!photo/|liked)(?:p/)?([^/?#]+)/?(?:$|[?#])"
    example = "https://500px.com/USER"

    def photos(self):
        self.kwdict["user"] = user = self.request_graphql(
            "getUserProfile", {"username": self.groups[0]})

        variables = {
            "sort"         : "CREATED_AT_DESC",
            "first"        : 20,
            "resourceTypes": ("PHOTO", "PHOTO_GROUP", "VIDEO"),
            "excludeNsfw"  : False,
            "userId"       : user["id"],
        }

        return self._pagination("pageResources", variables)


class _500pxGalleryExtractor(_500pxExtractor):
    """Extractor for photo galleries on 500px.com"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{user[username]}",
                     "Galleries", "{gallery[name]} ({gallery[id]})")
    pattern = BASE_PATTERN + r"/gallery/([^/?#]+)"
    example = "https://500px.com/gallery/ID"

    def photos(self):
        self.kwdict["gallery"] = gallery = self.request_graphql(
            "GetGalleryById", {"id": self.groups[0]})
        self.kwdict["user"] = self.request_graphql(
            "getUserProfile", {"username": gallery["creator"]["username"]})

        variables = {
            "first"    : 20,
            "galleryId": gallery["id"]
        }

        return self._pagination("PageGalleryItems", variables)


class _500pxGroupExtractor(_500pxExtractor):
    """Extractor for photo groups"""
    subcategory = "group"
    pattern = BASE_PATTERN + r"/photo-group/([^/?#]+)"
    example = "https://500px.com/photo-group/1a2B3"

    def photos(self):
        self.kwdict["group"] = group = self.request_graphql(
            "getPhotoGroupById", {"id": self.groups[0]})
        return (group,)


class _500pxPostExtractor(_500pxExtractor):
    """Extractor for individual posts from 500px.com"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/(photo|video)/([^/?#]+)"
    example = "https://500px.com/photo/1a2B3"

    def __init__(self, match):
        self.subcategory = match[1]
        _500pxExtractor.__init__(self, match)

    def photos(self):
        type, id = self.groups
        opname = "getPhotoById" if type == "photo" else "getVideoById"
        photo = self.request_graphql(opname, {"id": id})
        photo["user"] = photo.pop("uploader")
        return (photo,)
