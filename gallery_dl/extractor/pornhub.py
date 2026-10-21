# -*- coding: utf-8 -*-

# Copyright 2019-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.pornhub.com/"""

from .common import Extractor, Message, Dispatch
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:[\w-]+\.)?pornhub\.com"
USER_PATTERN = BASE_PATTERN + r"/((?:channels|users|model|pornstar)/[^/?#]+)"


class PornhubExtractor(Extractor):
    """Base class for pornhub extractors"""
    category = "pornhub"
    root = "https://www.pornhub.com"

    def _init(self):
        self.cookies.set(
            "accessAgeDisclaimerPH", "1", domain=".pornhub.com")

    def _pagination(self, user, path):
        if "/" not in path:
            path += "/public"

        url = f"{self.root}/{user}/{path}/ajax"
        params = {"page": 1}
        headers = {
            "Referer": url[:-5],
            "X-Requested-With": "XMLHttpRequest",
        }

        while True:
            response = self.request(
                url, method="POST", headers=headers, params=params,
                allow_redirects=False)

            if 300 <= response.status_code < 400:
                url = f"{self.root}{response.headers['location']}/{path}/ajax"
                continue

            yield response.text

            params["page"] += 1


class PornhubGalleryExtractor(PornhubExtractor):
    """Extractor for image galleries on pornhub.com"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{user}", "{gallery[id]} {gallery[title]}")
    filename_fmt = "{num:>03}_{id}.{extension}"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/album/(\d+)"
    example = "https://www.pornhub.com/album/12345"

    def items(self):
        data = self.metadata()
        yield Message.Directory, "", data
        for num, img in enumerate(self.images(), 1):

            image = {
                "url"    : img["img_large"],
                "caption": img["caption"],
                "id"     : text.parse_int(img["id"]),
                "views"  : text.parse_int(img["times_viewed"]),
                "score"  : text.parse_int(img["vote_percent"]),
                "num"    : num,
            }

            url = image["url"]
            image.update(data)
            yield Message.Url, url, text.nameext_from_url(url, image)

    def metadata(self):
        gid = self.groups[0]
        url = f"{self.root}/album/{gid}"
        extr = text.extract_from(self.request(url).text)

        title = extr("<title>", "</title>")
        self._token = extr('data-token="', '"')
        score = extr('<div id="albumGreenBar" style="width:', '"')
        views = extr('<div id="viewsPhotAlbumCounter">', '<')
        tags = extr('<div id="photoTagsBox"', '<script')
        self._first = extr('<a href="/photo/', '"')
        title, _, user = title.rpartition(" - ")

        return {
            "user" : text.unescape(user[:-14]),
            "gallery": {
                "id"   : text.parse_int(gid),
                "title": text.unescape(title),
                "score": text.parse_int(score.partition("%")[0]),
                "views": text.parse_int(views.partition(" ")[0]),
                "tags" : text.split_html(tags)[2:],
            },
        }

    def images(self):
        gid = self.groups[0]
        url = f"{self.root}/api/v1/album/{gid}/show_album_json"
        params = {"token": self._token}
        data = self.request_json(url, params=params)

        if not (images := data.get("photos")):
            raise self.exc.AuthorizationError()
        key = end = self._first

        results = []
        try:
            while True:
                img = images[key]
                results.append(img)
                key = str(img["next"])
                if key == end:
                    break
        except KeyError:
            self.log.warning("%s: Unable to ensure correct file order", gid)
            return images.values()

        return results


class PornhubGifExtractor(PornhubExtractor):
    """Extractor for pornhub.com gifs"""
    subcategory = "gif"
    directory_fmt = ("{category}", "{user}", "gifs")
    filename_fmt = "{id} {title}.{extension}"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/gif/(\d+)"
    example = "https://www.pornhub.com/gif/12345"

    def items(self):
        gid = self.groups[0]
        url = f"{self.root}/gif/{gid}"
        extr = text.extract_from(self.request(url).text)

        gif = {
            "id"   : gid,
            "tags" : extr("data-context-tag='", "'").split(","),
            "title": extr('"name": "', '"'),
            "url"  : extr('"contentUrl": "', '"'),
            "date" : self.parse_datetime_iso(extr('"uploadDate": "', '"')),
            "viewkey"  : extr('From this video: '
                              '<a href="/view_video.php?viewkey=', '"'),
            "timestamp": extr('lass="directLink tstamp" rel="nofollow">', '<'),
            "user" : text.remove_html(extr("Created by:", "</div>")),
        }

        yield Message.Directory, "", gif
        yield Message.Url, gif["url"], text.nameext_from_url(gif["url"], gif)


class PornhubUserExtractor(Dispatch, PornhubExtractor):
    """Extractor for a pornhub user"""
    pattern = USER_PATTERN + r"/?$"
    example = "https://www.pornhub.com/model/USER"

    def items(self):
        base = f"{self.root}/{self.groups[0]}/"
        return self._dispatch_extractors({
            "avatar"    : (PornhubAssetExtractor , base + "avatar"),
            "background": (PornhubAssetExtractor , base + "background"),
            "photos"    : (PornhubPhotosExtractor, base + "photos"),
            "gifs"      : (PornhubGifsExtractor  , base + "gifs"),
        }, ("photos",))


class PornhubPhotosExtractor(PornhubExtractor):
    """Extractor for all galleries of a pornhub user"""
    subcategory = "photos"
    pattern = USER_PATTERN + r"/(photos(?:/[^/?#]+)?)"
    example = "https://www.pornhub.com/model/USER/photos"

    def items(self):
        data = {"_extractor": PornhubGalleryExtractor}
        base = self.root + "/album/"
        for page in self._pagination(*self.groups):
            gid = None
            for gid in text.extract_iter(page, 'id="albumphoto', '"'):
                yield Message.Queue, base + gid, data
            if gid is None:
                return


class PornhubGifsExtractor(PornhubExtractor):
    """Extractor for a pornhub user's gifs"""
    subcategory = "gifs"
    pattern = USER_PATTERN + r"/(gifs(?:/[^/?#]+)?)"
    example = "https://www.pornhub.com/model/USER/gifs"

    def items(self):
        data = {"_extractor": PornhubGifExtractor}
        base = self.root + "/gif/"
        for page in self._pagination(*self.groups):
            gid = None
            for gid in text.extract_iter(page, 'id="gif', '"'):
                yield Message.Queue, base + gid, data
            if gid is None:
                return


class PornhubAssetExtractor(PornhubExtractor):
    """Extractor for a pornhub user's avatar & banner"""
    subcategory = "asset"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{type} {id}.{extension}"
    archive_fmt = "{user}/{type}/{id}"
    pattern = USER_PATTERN + r"/(?:avatar|ba(nner|ckground))"
    example = "https://www.pornhub.com/model/USER/avatar"

    def __init__(self, match):
        self.subcategory = "background" if match[2] else "avatar"
        PornhubExtractor.__init__(self, match)

    def items(self):
        url = f"{self.root}/{self.groups[0]}"
        page = self.request(url).text

        if self.groups[1]:
            offset = 5
            needle = "coverPictureDefault"
        else:
            offset = 6
            needle = "getAvatar"

        if src := text.extr(page, f'id="{needle}" src="', '"'):
            src = text.unescape(src)
            if src.count("/") >= 8:
                id = src.rsplit("/", 2)[1][offset:]
            else:
                id = src[src.rfind(")")+1:src.rfind(".")]
            data = text.nameext_from_url(src, {
                "id"  : id,
                "type": self.subcategory,
                "user": text.extr(page, "<h1", "<").partition(">")[2].strip(),
            })
            yield Message.Directory, "", data
            yield Message.Url, src, data
