# -*- coding: utf-8 -*-

# Copyright 2018-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.behance.net/"""

from .common import Extractor, Message
from .. import text, util

BASE_PATTERN = r"(?:https?://)?(?:www\.)?behance\.net"


class BehanceExtractor(Extractor):
    """Base class for behance extractors"""
    category = "behance"
    root = "https://www.behance.net"
    request_interval = (2.0, 4.0)
    browser = "firefox"
    tls12 = False

    def _init(self):
        self._bcp = self.cookies.get("bcp", domain="www.behance.net")
        if not self._bcp:
            self._bcp = util.generate_uuid()
            self.cookies.set("bcp", self._bcp, domain="www.behance.net")

    def items(self):
        for gallery in self.galleries():
            gallery["_extractor"] = BehanceGalleryExtractor
            yield Message.Queue, gallery["url"], self._update(gallery)

    def galleries(self):
        """Return all relevant gallery URLs"""

    def request_html(self, url, **kwargs):
        kwargs["headers"] = {
            "Accept": "text/html,application/xhtml+xml,"
                      "application/xml;q=0.9,*/*;q=0.8",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Priority": "u=0, i",
        }
        kwargs["cookies"] = {
            "gk_suid": "50010966",
            "gki": "feature_progressive_profile:false,",
            "gpv": "behance.net:profile:default",
        }

        try:
            return Extractor.request(self, url, **kwargs).text
        except self.exc.HttpError as exc:
            if exc.status != 403 or not (value := text.extr(
                    exc.response.text, "js_challenge_value=", ";")):
                raise

        kwargs["interval"] = False
        self.cookies.set("js_challenge_value", value, domain="www.behance.net")
        return Extractor.request(self, url, **kwargs).text

    def request_graphql(self, opname, variables):
        url = self.root + "/v3/graphql"
        headers = {
            "X-BCP" : self._bcp,
            "X-Requested-With": "XMLHttpRequest",
        }
        data = {
            "query"    : self.utils("graphql", opname),
            "variables": variables,
        }

        return self.request_json(
            url, method="POST", headers=headers, json=data)["data"]

    def _update(self, data):
        # compress data to simple lists
        if (fields := data.get("fields")) and isinstance(fields[0], dict):
            data["fields"] = [
                field.get("name") or field.get("label")
                for field in fields
            ]

        data["owners"] = [
            owner.get("display_name") or owner.get("displayName")
            for owner in data["owners"]
        ]

        tags = data.get("tags") or ()
        if tags and isinstance(tags[0], dict):
            tags = [tag["title"] for tag in tags]
        data["tags"] = tags

        data["date"] = self.parse_timestamp(
            data.get("publishedOn") or data.get("conceived_on") or 0)

        if creator := data.get("creator"):
            creator["name"] = creator["url"].rpartition("/")[2]

        # backwards compatibility
        data["gallery_id"] = data["id"]
        data["title"] = data["name"]
        data["user"] = ", ".join(data["owners"])

        return data


class BehanceGalleryExtractor(BehanceExtractor):
    """Extractor for image galleries from www.behance.net"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{owners:J, }", "{id} {name}")
    filename_fmt = "{category}_{id}_{num:>02}.{extension}"
    archive_fmt = "{id}_{num}"
    pattern = BASE_PATTERN + r"/gallery/(\d+)"
    example = "https://www.behance.net/gallery/12345/TITLE"

    def _init(self):
        BehanceExtractor._init(self)

        if modules := self.config("modules"):
            if isinstance(modules, str):
                modules = modules.split(",")
            self.modules = set(modules)
        else:
            self.modules = {"image", "video", "mediacollection", "embed"}

    def items(self):
        data = self.get_gallery_data()
        imgs = self.get_images(data)
        data["count"] = len(imgs)

        yield Message.Directory, "", data
        for data["num"], (url, module) in enumerate(imgs, 1):
            data["module"] = module
            data["extension"] = (module.get("extension") or
                                 text.ext_from_url(url))
            yield Message.Url, url, data

    def get_gallery_data(self):
        """Collect gallery info dict"""
        url = f"{self.root}/gallery/{self.groups[0]}/a"
        page = self.request_html(url)

        data = util.json_loads(text.extr(
            page, 'id="beconfig-store_state">', '</script>'))
        return self._update(data["project"]["project"])

    def get_images(self, data):
        """Extract image results from an API response"""
        if not data["modules"]:
            access = data.get("matureAccess")
            if access == "logged-out":
                raise self.exc.AuthorizationError(
                    "Mature content galleries require logged-in cookies")
            if access == "restricted-safe":
                raise self.exc.AuthorizationError(
                    "Mature content blocked in account settings")
            if access and access != "allowed":
                raise self.exc.AuthorizationError()
            return ()

        results = []
        for module in data["modules"]:
            mtype = module["__typename"][:-6].lower()

            if mtype not in self.modules:
                self.log.debug("Skipping '%s' module", mtype)
                continue

            if mtype == "image":
                sizes = {
                    size["url"].rsplit("/", 2)[1]: size
                    for size in module["imageSizes"]["allAvailable"]
                }
                size = (sizes.get("source") or
                        sizes.get("max_3840") or
                        sizes.get("fs") or
                        sizes.get("hd") or
                        sizes.get("disp"))
                results.append((size["url"], module))

            elif mtype == "video":
                try:
                    url = text.extr(module["embed"], 'src="', '"')
                    page = self.request(text.unescape(url)).text

                    url = text.extr(page, '<source src="', '"')
                    if text.ext_from_url(url) == "m3u8":
                        url = "ytdl:" + url
                        module["_ytdl_manifest"] = "hls"
                        module["extension"] = "mp4"
                    results.append((url, module))
                    continue
                except Exception as exc:
                    self.log.debug("%s: %s", exc.__class__.__name__, exc)

                try:
                    renditions = module["videoData"]["renditions"]
                except Exception:
                    self.log.warning("No download URLs for video %s",
                                     module.get("id") or "???")
                    continue

                try:
                    url = [
                        r["url"] for r in renditions
                        if text.ext_from_url(r["url"]) != "m3u8"
                    ][-1]
                except Exception as exc:
                    self.log.debug("%s: %s", exc.__class__.__name__, exc)
                    url = "ytdl:" + renditions[-1]["url"]

                results.append((url, module))

            elif mtype == "mediacollection":
                for component in module["components"]:
                    for size in component["imageSizes"].values():
                        if size:
                            parts = size["url"].split("/")
                            parts[4] = "source"
                            results.append(("/".join(parts), module))
                            break

            elif mtype == "embed":
                if embed := (module.get("originalEmbed") or
                             module.get("fluidEmbed")):
                    embed = text.unescape(text.extr(embed, 'src="', '"'))
                    module["extension"] = "mp4"
                    results.append(("ytdl:" + embed, module))

            elif mtype == "text":
                module["extension"] = "txt"
                results.append(("text:" + module["text"], module))

        return results


class BehanceUserExtractor(BehanceExtractor):
    """Extractor for a user's galleries from www.behance.net"""
    subcategory = "user"
    categorytransfer = True
    pattern = BASE_PATTERN + r"/([^/?#]+)/?$"
    example = "https://www.behance.net/USER"

    def galleries(self):
        endpoint = "GetProfileProjects"
        variables = {
            "username": self.groups[0],
            "after"   : "MAo=",  # "0" in base64
        }

        while True:
            data = self.request_graphql(endpoint, variables)
            items = data["user"]["profileProjects"]
            yield from items["nodes"]

            info = items["pageInfo"]
            if not info["hasNextPage"]:
                break
            variables["afterItem"] = info["endCursor"]


class BehanceCollectionExtractor(BehanceExtractor):
    """Extractor for a collection's galleries from www.behance.net"""
    subcategory = "collection"
    categorytransfer = True
    pattern = BASE_PATTERN + r"/(?:moodboard|collection)/(\d+)"
    example = "https://www.behance.net/collection/12345/TITLE"

    def galleries(self):
        endpoint = "GetMoodboardItemsAndRecommendations"
        variables = {
            "afterItem": "MAo=",  # "0" in base64
            "firstItem": 40,
            "id"       : int(self.groups[0]),
            "shouldGetItems"          : True,
            "shouldGetMoodboardFields": False,
            "shouldGetRecommendations": False,
        }

        while True:
            data = self.request_graphql(endpoint, variables)
            items = data["moodboard"]["items"]

            for node in items["nodes"]:
                yield node["entity"]

            info = items["pageInfo"]
            if not info["hasNextPage"]:
                break
            variables["afterItem"] = info["endCursor"]
