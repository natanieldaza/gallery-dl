# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://fapello.com/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?fapello\.(?:com|su)"


class FapelloExtractor(Extractor):
    """Base class for fapello extractors"""
    category = "fapello"
    root = "https://fapello.com"

    def __init__(self, match):
        self.root = text.root_from_url(match[0])
        Extractor.__init__(self, match)


class FapelloPostExtractor(FapelloExtractor):
    """Extractor for individual posts on fapello.com"""
    subcategory = "post"
    directory_fmt = ("{category}", "{model}")
    filename_fmt = "{model}_{id}.{extension}"
    archive_fmt = "{type}_{model}_{id}"
    pattern = BASE_PATTERN + r"/(?!search/|popular_videos/)([^/?#]+)/(\d+)"
    example = "https://fapello.com/MODEL/12345/"

    def items(self):
        model, id = self.groups
        url = f"{self.root}/{model}/{id}/"
        page = text.extr(
            self.request(url, allow_redirects=False).text,
            'class="uk-align-center"', "</div>", None)
        if page is None:
            raise self.exc.NotFoundError("post")

        data = {
            "model": model,
            "id"   : text.parse_int(id),
            "type" : "video" if 'type="video' in page else "photo",
            "thumbnail": text.extr(page, 'poster="', '"'),
        }
        url = text.extr(page, 'src="', '"').replace(
            ".md", "").replace(".th", "")
        yield Message.Directory, "", data
        yield Message.Url, url, text.nameext_from_url(url, data)


class FapelloModelExtractor(FapelloExtractor):
    """Extractor for all posts from a fapello model"""
    subcategory = "model"
    pattern = (BASE_PATTERN + r"/(?!top-(?:likes|followers)|popular_videos"
               r"|videos|trending|search/?$)"
               r"([^/?#]+)/?$")
    example = "https://fapello.com/MODEL/"

    def items(self):
        model = self.groups[0]

        url = f"{self.root}/{model}/"
        page = self.request(url).text
        name, pos = text.extract(page, "<h2", "<")
        alias, pos = text.extract(page, '<p class="flex', "<", pos)

        data = {
            "_extractor": FapelloPostExtractor,
            "model_name": text.unescape(name[name.rfind(">")+1:]),
            "aliases": (text.unescape(alias[alias.rfind(">")+1:]).split(", ")
                        if alias else ()),
        }

        num = 1
        base = f"{self.root}/ajax/model/{model}/page-"
        while True:
            page = self.request(f"{base}{num}/").text
            if not page:
                break

            url = None
            for url in text.extract_iter(page, '<a href="', '"'):
                if url != "javascript:void(0);":
                    yield Message.Queue, url, data
            if url is None:
                break
            num += 1


class FapelloPathExtractor(FapelloExtractor):
    """Extractor for models and posts from fapello.com paths"""
    subcategory = "path"
    pattern = (BASE_PATTERN +
               r"/(?!search/?$)(top-(?:likes|followers)|videos|trending"
               r"|popular_videos/[^/?#]+)/?$")
    example = "https://fapello.com/trending/"

    def items(self):
        path = self.groups[0]
        if path in {"top-likes", "top-followers"}:
            data = {"_extractor": FapelloModelExtractor}
        else:
            data = {"_extractor": FapelloPostExtractor}

        num = 1
        base = f"{self.root}/ajax/{path}/page-"
        while True:
            page = self.request(f"{base}{num}/").text
            if not page:
                return

            for item in text.extract_iter(
                    page, 'uk-transition-toggle">', "</a>"):
                yield Message.Queue, text.extr(item, '<a href="', '"'), data
            num += 1
