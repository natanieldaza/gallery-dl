# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.postype.com/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?postype\.com(?:/[a-z]{2})?"


class PostypeExtractor(Extractor):
    """Base class for postype extractors"""
    category = "postype"
    root = "https://www.postype.com"
    root_api = "https://api.postype.com/api"
    directory_fmt = ("{category}", "{channel[name]}")
    filename_fmt = "{post_id}_{num:>03}.{extension}"
    archive_fmt = "{post_id}_{num}"
    request_interval = (1.0, 2.0)

    def items(self):
        for post in self.posts():
            post = self._prepare(post)
            files = self._extract_files(post)
            post["count"] = len(files)

            yield Message.Directory, "", post
            for post["num"], file in enumerate(files, 1):
                post.update(file)
                url = file["url"]
                yield Message.Url, url, text.nameext_from_url(url, post)

    def request_api(self, endpoint, params=None):
        return self.request_json(self.root_api + endpoint, params=params)

    def _prepare(self, post):
        post["date"] = self.parse_timestamp(post["publishedAt"])
        post["views"] = post.pop("viewCount", None)
        post["views"] = post.pop("viewCount", None)
        post["likes"] = post.pop("likeCount", None)
        post["post_id"] = post.pop("postId", 0)
        post["comments"] = post.pop("commentCount", None)
        post.pop("likeProfileAvatars", None)
        post.pop("prevPost", None)
        post.pop("nextPost", None)

        if "channelName" in post["channel"]:
            post["channel"]["name"] = post["channel"].pop("channelName")

        return post

    def _extract_files(self, post):
        """Extract file URLs from post HTML content"""
        data = self.request_api("/v1/post/content/" + str(post["post_id"]))
        html = data["data"]["html"]

        files = []
        seen = set()

        for ele, dl in text.re(
            r'<([^>]+(?:data-full-path=|class="inner file-downloa(d))[^>]+)>'
        ).findall(html):
            if dl:
                url = text.unescape(text.extr(ele, 'href="', '"'))
                base, _, query = url.partition("?")
                if base in seen:
                    continue
                seen.add(base)

                if name := text.parse_query(query).get("filename"):
                    files.append(text.nameext_from_name(name, {"url": url}))
                else:
                    files.append(text.nameext_from_url(url, {"url": url}))
            else:
                url = text.unescape(text.extr(
                    ele, 'data-full-path="', '"').partition("?")[0])
                if url in seen:
                    continue
                seen.add(url)

                files.append(text.nameext_from_url(url, {
                    "url"   : url,
                    "width" : text.parse_int(text.extr(
                        ele, 'data-width="', '"')),
                    "height": text.parse_int(text.extr(
                        ele, 'data-height="', '"')),
                }))

        return files


class PostypePostExtractor(PostypeExtractor):
    """Extractor for a single postype post"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/@[^/?#]+/post/(\d+)"
    example = "https://www.postype.com/@USER/post/12345"

    def posts(self):
        return (self.request_api("/v1/posts/" + self.groups[0]),)


class PostypeChannelExtractor(PostypeExtractor):
    """Extractor for all posts of a postype channel"""
    subcategory = "channel"
    pattern = BASE_PATTERN + r"/@([^/?#]+)/?$"
    example = "https://www.postype.com/@USER"

    def posts(self):
        channel = self.request_api(
            "/v1/channels/by/channel-name/" + self.groups[0])
        return self._pagination(channel["channelId"])

    def _pagination(self, channel_id):
        endpoint = f"/v2/channel/{channel_id}/activity/all"
        params = {"page": 0}

        while True:
            data = self.request_api(endpoint, params)

            for item in data["content"]:
                if item["type"] == "POST":
                    yield item["feedItem"]

            if data.get("last", True):
                break
            params["page"] += 1
