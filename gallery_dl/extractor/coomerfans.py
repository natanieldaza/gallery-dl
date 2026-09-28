# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://coomerfans.com/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?coomerfans\.com"


class CoomerfansExtractor(Extractor):
    """Base class for coomerfans extractors"""
    category = "coomerfans"
    root = "https://coomerfans.com"
    directory_fmt = ("{category}", "{service}", "{username} ({user})")
    filename_fmt = "{id}_{num}.{extension}"
    archive_fmt = "{service}_{user}_{id}_{num}"


class CoomerfansPostExtractor(CoomerfansExtractor):
    """Extractor for individual posts on coomerfans.com"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/p/(\d+)/(\d+)/(\w+)"
    example = "https://coomerfans.com/p/12345/67890/SERVICE"

    def items(self):
        post_id, creator_id, service = self.groups
        url = f"{self.root}/p/{post_id}/{creator_id}/{service}"
        page = self.request(url).text
        extr = text.extract_from(page)

        post = {
            "id"      : text.parse_int(post_id),
            "user"    : text.parse_int(creator_id),
            "service" : service,
            "username": text.unescape(extr('class="model-name">', '<')),
            "title"   : text.unescape(extr('<h1>', '<')),
            "date"    : self.parse_datetime_iso(extr(
                'class="post-date">Added ', ' &#43;')),
            "content" : extr("<p>", "</p>"),
            "post_url": url,
            "_http_headers": {"Referer": url},
        }

        pattern = text.re(r'<(?:img|sourc(e)) src="([^"]+)')
        body = extr('class="post-body"', '\n                </div>')
        files = {}
        for video, url in pattern.findall(body):
            url = text.unescape(url)
            file = text.nameext_from_url(url)
            if file["filename"] in files:
                continue
            file["hash"] = hash = file["filename"]
            file["type"] = "video" if video else "image"
            file["url"] = url
            files[hash] = file

        post["count"] = len(files)
        yield Message.Directory, "", post
        for post["num"], file in enumerate(files.values(), 1):
            post.update(file)
            yield Message.Url, file["url"], post


class CoomerfansCreatorExtractor(CoomerfansExtractor):
    """Extractor for all posts from a coomerfans creator"""
    subcategory = "creator"
    pattern = BASE_PATTERN + r"/u/(\w+)/(\d+)/([^/?#]+)(?:\?page=(\d+))?"
    example = "https://coomerfans.com/u/onlyfans/12345/USERNAME"

    def items(self):
        service, creator_id, username, page_num = self.groups
        url = f"{self.root}/u/{service}/{creator_id}/{username}"
        data = {"_extractor": CoomerfansPostExtractor}

        params = {"page": text.parse_int(page_num, 1)}
        while True:
            page = self.request(url, params=params).text

            path = None
            for path in text.extract_iter(page, '<h3><a href="', '"'):
                yield Message.Queue, self.root + path, data

            if path is None or ">Next</a>" not in page:
                break
            params["page"] += 1
