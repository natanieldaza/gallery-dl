# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.imdb.com/"""

from .common import Extractor, Message
from .. import text, util

BASE_PATTERN = r"(?:https?://)?(?:www\.)?imdb\.com"

GQL_HASHES = {
    "NameImages":
        "4223ddf53fc6196821daf52d9ce5bb3080cae25db60f76bb8fd4ff7bd1ff94ce",
    "TitleImages":
        "1e5d5f0f8f7a27bad078b4eb915554a92f0123750f6e39abdd16ac981ef8a84c",
}


class ImdbExtractor(Extractor):
    """Base class for imdb extractors"""
    category = "imdb"
    root = "https://www.imdb.com"

    def request_graphql(self, opname, variables, sub="api"):
        extensions = {
            "persistedQuery": {
                "sha256Hash": GQL_HASHES[opname],
                "version"   : 1,
            }
        }
        params = {
            "operationName": opname,
            "variables"    : util.json_dumps(variables),
            "extensions"   : util.json_dumps(extensions),
        }
        headers = {
            "Accept": "application/graphql+json, application/json",
            "content-type": "application/json",
            "x-imdb-client-name": "imdb-web-next-localized",
            #  "x-amzn-sessionid": "...",
            #  "x-imdb-client-rid": "...",
            "x-imdb-user-language": "en-US",
            "x-imdb-user-country": "US",
            "x-imdb-consent-info": "eyJwdXJwb3NlcyI6W10sInZlbmRvcnMiOltdLCJhZ2"
                                   "TaWduYWwiOiJBRFVMVCIsImlzR2RwciI6dHJ1ZX0",
        }
        url = f"https://{sub}.graphql.imdb.com/"
        return self.request_json(url, params=params, headers=headers)

    def items_images(self, opname, callback=None):
        variables = {
            "after"   : "",
            "first"   : 20,
            "firstYes": True,
            "id"      : self.groups[0],
            "lastYes" : False,
        }

        while True:
            data = self.request_graphql(opname, variables)

            info = data["data"].popitem()[1]
            if callback is not None:
                callback(info)
                callback = None

            images = info["images"]
            self.kwdict["count"] = images["total"]
            for edge in images["edges"]:
                node = edge["node"]
                node.pop("correctionLink", None)
                node.pop("reportingLink", None)
                node["num"] = edge.get("position") or 0
                node["names"] = [
                    n["nameText"]["text"] for n in node.get("names") or ()]
                node["titles"] = [
                    t["titleText"]["text"] for t in node.get("titles") or ()]
                node["countries"] = [
                    c["text"] for c in node.get("countries") or ()]
                node["languages"] = [
                    c["text"] for c in node.get("languages") or ()]

                url = node["url"]
                yield Message.Directory, "", node
                yield Message.Url, url, text.nameext_from_url(url, node)

            if not images["pageInfo"]["hasNextPage"]:
                break
            variables["after"] = images["pageInfo"]["endCursor"]


class ImdbNameImagesExtractor(ImdbExtractor):
    subcategory = "name-images"
    directory_fmt = ("{category}", "{name}", "Photos")
    filename_fmt = "{num:>03}{titles:J - /? //} ({id}).{extension}"
    archive_fmt = "{name}.{id}"
    pattern = BASE_PATTERN + r"/name/(nm\d+)/mediaviewer"
    example = "https://www.imdb.com/name/nm012345/mediaviewer/"

    def items(self):
        return self.items_images("NameImages", self._callback)

    def _callback(self, info):
        kwdict = self.kwdict
        kwdict["name"] = info["nameText"]["text"]


class ImdbTitleImagesExtractor(ImdbExtractor):
    subcategory = "title-images"
    directory_fmt = ("{category}", "{title}", "Photos")
    filename_fmt = "{num:>03}{names:J - /? //} ({id}).{extension}"
    archive_fmt = "{title}.{id}"
    pattern = BASE_PATTERN + r"/title/(tt\d+)/mediaviewer"
    example = "https://www.imdb.com/title/tt012345/mediaviewer/"

    def items(self):
        return self.items_images("TitleImages", self._callback)

    def _callback(self, info):
        kwdict = self.kwdict
        kwdict["title"] = info["titleText"]["text"]
        kwdict["year"] = info["releaseYear"]["year"]
        kwdict["status"] = info["meta"]["publicationStatus"]
