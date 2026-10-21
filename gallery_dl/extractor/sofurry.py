# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://sofurry.com/"""

from .common import Extractor, Message, Dispatch
from .. import text, util

BASE_PATTERN = r"(?:https?://)?(?:www\.)?sofurry\.com"


class SofurryExtractor(Extractor):
    """Base class for sofurry extractors"""
    category = "sofurry"
    root = "https://sofurry.com"
    directory_fmt = ("{category}", "{author[handle]}")
    filename_fmt = "{date:%Y-%m-%d} {id}{title:? //}{num:? //:>02}.{extension}"
    archive_fmt = "{id}_{num}"
    page_start = 0
    per_page = 24
    offset = 0
    request_interval = (0.5, 1.5)

    def items(self):
        original = self.config("original", True)

        posts = self.posts()
        if self.offset:
            util.advance(posts, self.offset)
        for submission_id in posts:
            url = f"{self.root}/s/{submission_id}.data"
            data = self._unpack(self.request_json(url))
            post = data["routes/submission.$id"]["data"]["submission"]

            files = post["content"]
            post["count"] = len(files)
            post["date"] = self.parse_datetime_iso(post["publishedAt"])

            yield Message.Directory, "", post
            if original:
                if len(files) == 1:
                    file = files[0]
                    post["extension"] = file["extension"]
                    post["file_id"] = file["id"]
                    post["file_title"] = file["title"]
                    post["file_description"] = file["description"]
                    post["meta"] = file["meta"]
                else:
                    post["extension"] = "zip"
                post["filename"] = post["title"]
                post["num"] = 0

                url = f"{self.root}/api/submission-download/{submission_id}"
                yield Message.Url, url, post

            else:
                files.sort(key=lambda f: f.get("position", 0))
                for post["num"], file in enumerate(files, 1):
                    url = file["displayUrl"]
                    post["file_id"] = file["id"]
                    post["file_title"] = file["title"]
                    post["file_description"] = file["description"]
                    post["filename"] = url[url.rfind("/")+1:]
                    post["extension"] = "webp"
                    post["meta"] = file["meta"]
                    yield Message.Url, url, post

    def skip_posts(self, num):
        pages, self.offset = divmod(num, self.per_page)
        self.page_start += pages
        return num

    def _pagination(self, url, params, subs=None):
        params["page"] = self.page_start
        params["per_page"] = "24"

        if subs is None or self.page_start > 0:
            subs = self.request_json(url, params=params)["submissions"]

        while True:
            for submission in subs["data"]:
                yield submission["id"]

            if not subs.get("hasNextPage"):
                break
            params["page"] += 1

            subs = self.request_json(url, params=params)["submissions"]

    def _profile_data(self, handle):
        url = f"{self.root}/u/{handle}/gallery.data?_routes=profile"
        return self._unpack(self.request_json(url))["profile"]["data"]

    def _unpack(self, pack):
        def resolve(item):
            if item.__class__ is dict:
                return {
                    pack[int(key[1:])]: (resolve(pack[value])
                                         if value > 0 else None)
                    for key, value in item.items()
                }
            if item.__class__ is list:
                return [
                    resolve(pack[value]) if value > 0 else None
                    for value in item
                ]
            return item

        return resolve(pack[0])


class SofurryUserExtractor(Dispatch, SofurryExtractor):
    pattern = BASE_PATTERN + r"/u/([^/?#]+)/?(?:$|\?|#)"
    example = "https://sofurry.com/u/USER"

    def items(self):
        base = f"{self.root}/u/{self.groups[0]}/"
        return self._dispatch_extractors((
            (SofurryGalleryExtractor , base + "gallery"),
            (SofurryFavoriteExtractor, base + "likes"),
        ), ("gallery",))


class SofurryFolderExtractor(SofurryExtractor):
    subcategory = "folder"
    directory_fmt = ("{category}", "{user[handle]}",
                     "{folder[name]} ({folder[id]})")
    pattern = BASE_PATTERN + r"/u/([^/?#]+)/gallery/?\?folder=([^&#]+)([^#]*)"
    example = "https://sofurry.com/u/USER/gallery?folder=iD"

    def posts(self):
        handle, folder_id, query = self.groups

        data = self.cache(self._profile_data, handle)
        for folder in data["folders"]:
            if folder["id"] == folder_id:
                break
        else:
            raise self.exc.NotFoundError("folder")
        self.kwdict["folder"] = folder
        self.kwdict["user"] = data["profile"]

        url = self.root + "/api/profile"
        params = text.parse_query(query)
        params["handle"] = handle
        params["tab"] = "folder"
        params["folder_id"] = folder_id
        return self._pagination(url, params)


class SofurryGalleryExtractor(SofurryExtractor):
    subcategory = "gallery"
    directory_fmt = ("{category}", "{user[handle]}")
    pattern = BASE_PATTERN + r"/u/([^/?#]+)/gallery(?:/?\?([^#]+))?"
    example = "https://sofurry.com/u/USER/gallery"

    def posts(self):
        handle, query = self.groups

        data = self.cache(self._profile_data, handle)
        self.kwdict["user"] = data["profile"]

        url = self.root + "/api/profile"
        params = text.parse_query(query)
        params["handle"] = handle
        params["tab"] = "gallery"
        return self._pagination(url, params, data["gallery"])


class SofurryFavoriteExtractor(SofurryExtractor):
    subcategory = "favorite"
    directory_fmt = ("{category}", "{user[handle]}", "Likes")
    archive_fmt = "f{user[handle]}_{id}_{num}"
    pattern = BASE_PATTERN + r"/u/([^/?#]+)/likes(?:/?\?([^#]+))?"
    example = "https://sofurry.com/u/USER/likes"

    def posts(self):
        handle, query = self.groups
        self.kwdict["user"] = self.cache(self._profile_data, handle)["profile"]

        url = self.root + "/api/profile"
        params = text.parse_query(query)
        params["handle"] = handle
        params["tab"] = "likes"
        return self._pagination(url, params)


class SofurrySubmissionExtractor(SofurryExtractor):
    subcategory = "submission"
    pattern = BASE_PATTERN + r"/s/([^/?#]+)"
    example = "https://sofurry.com/s/ID"
    skip_posts = None

    def posts(self):
        return (self.groups[0],)
