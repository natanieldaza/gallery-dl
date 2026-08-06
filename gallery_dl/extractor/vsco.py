# -*- coding: utf-8 -*-

# Copyright 2019-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://vsco.co/"""

from .common import Extractor, Message, Dispatch
from .. import text, util
import http.cookiejar

# Try to import curl_cffi for Cloudflare bypass
try:
    from curl_cffi import requests as cffi_requests
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False

BASE_PATTERN = r"(?:https?://)?(?:www\.)?vsco\.co"
USER_PATTERN = BASE_PATTERN + r"/([^/?#]+)"


class VscoExtractor(Extractor):
    """Base class for vsco extractors"""
    category = "vsco"
    root = "https://vsco.co"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{id}.{extension}"
    archive_fmt = "{id}"
    browser = "firefox"
    tls12 = False

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match[1].lower()

    def request(self, url, **kwargs):
        """Override request method to use curl_cffi for Cloudflare bypass"""
        if not HAS_CURL_CFFI:
            # Fall back to standard request method
            return Extractor.request(self, url, **kwargs)
        
        # Use curl_cffi with browser impersonation to bypass Cloudflare
        try:
            # Load cookies if configured
            cookie_file = self.config("cookies")
            cookies_dict = {}
            
            if cookie_file:
                try:
                    jar = http.cookiejar.MozillaCookieJar(cookie_file)
                    jar.load(ignore_discard=True, ignore_expires=True)
                    cookies_dict = {cookie.name: cookie.value for cookie in jar}
                    self.log.debug(f"Loaded {len(cookies_dict)} cookies from {cookie_file}")
                except Exception as e:
                    self.log.warning(f"Failed to load cookies: {e}")
            
            # Get headers from kwargs
            headers = kwargs.get('headers', {})
            
            # Make request with Firefox TLS impersonation
            self.log.debug(f"Using curl_cffi (Firefox 135) for URL: {url}")
            response = cffi_requests.get(
                url,
                cookies=cookies_dict,
                headers=headers,
                impersonate="firefox135",  # Bypass Cloudflare TLS fingerprinting
                timeout=kwargs.get('timeout', 30),
                allow_redirects=kwargs.get('allow_redirects', True)
            )
            
            # Fix VSCO's JavaScript undefined values → null for valid JSON
            response_text = response.text.replace(':undefined', ':null')
            
            # Create response wrapper compatible with gallery-dl
            class ResponseWrapper:
                def __init__(self, cffi_resp, fixed_text):
                    self._response = cffi_resp
                    self.status_code = cffi_resp.status_code
                    self.headers = cffi_resp.headers
                    self.text = fixed_text
                    self.content = cffi_resp.content
                    self.url = cffi_resp.url
                    
                def json(self):
                    return self._response.json()
            
            return ResponseWrapper(response, response_text)
            
        except Exception as e:
            self.log.warning(f"curl_cffi request failed: {e}, falling back to standard request")
            # Fall back to standard request on error
            return Extractor.request(self, url, **kwargs)

    def request_json(self, url, **kwargs):
        """Override request_json to use curl_cffi for API calls"""
        if not HAS_CURL_CFFI:
            return Extractor.request(self, url, **kwargs).json()
        
        try:
            # Load cookies
            cookie_file = self.config("cookies")
            cookies_dict = {}
            
            if cookie_file:
                try:
                    jar = http.cookiejar.MozillaCookieJar(cookie_file)
                    jar.load(ignore_discard=True, ignore_expires=True)
                    cookies_dict = {cookie.name: cookie.value for cookie in jar}
                except Exception:
                    pass
            
            # Get headers and params from kwargs
            headers = kwargs.get('headers', {})
            params = kwargs.get('params', {})
            
            # Make JSON request with Firefox TLS impersonation
            self.log.debug(f"Using curl_cffi (Firefox 135) for JSON API: {url}")
            response = cffi_requests.get(
                url,
                cookies=cookies_dict,
                headers=headers,
                params=params,
                impersonate="firefox135",
                timeout=kwargs.get('timeout', 30)
            )
            
            return response.json()
            
        except Exception as e:
            self.log.warning(f"curl_cffi JSON request failed: {e}, falling back")
            return Extractor.request(self, url, **kwargs).json()

    def items(self):
        videos = self.config("videos", True)
        yield Message.Directory, "", {"user": self.user}
        for img in self.images():

            if not img:
                continue
            elif "playback_url" in img:
                img = self._transform_video(img)
            elif "responsive_url" not in img:
                continue

            if img["is_video"]:
                if not videos:
                    continue
                url = text.ensure_http_scheme(img["video_url"])
            else:
                base = img["responsive_url"].partition("/")[2]
                cdn, _, path = base.partition("/")
                if cdn.startswith("aws"):
                    url = f"https://image-{cdn}.vsco.co/{path}"
                elif cdn.isdecimal():
                    url = "https://image.vsco.co/" + base
                elif img["responsive_url"].startswith("http"):
                    url = img["responsive_url"]
                else:
                    url = "https://" + img["responsive_url"]

            data = text.nameext_from_url(url, {
                "id"    : img["_id"],
                "user"  : self.user,
                "grid"  : img["grid_name"],
                "meta"  : img.get("image_meta") or {},
                "tags"  : [tag["text"] for tag in img.get("tags") or ()],
                "date"  : self.parse_timestamp(img["upload_date"] / 1000),
                "video" : img["is_video"],
                "width" : img["width"],
                "height": img["height"],
                "description": img.get("description") or "",
            })
            if data["extension"] == "m3u8":
                url = "ytdl:" + url
                data["_ytdl_manifest"] = "hls"
                data["extension"] = "mp4"
            yield Message.Url, url, data

    def images(self):
        """Return an iterable with all relevant image objects"""

    def _extract_preload_state(self, url):
        # immich patch: browser-like headers to reduce VSCO gating
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
        }
        page = self.request(url, headers=headers, notfound=self.subcategory).text
        data = util.json_loads(text.extr(page, "__PRELOADED_STATE__ = ", "<")
                               .replace('":undefined', '":null'))
        self._tkn = data["users"]["currentUser"]["tkn"]
        return data

    def _extract_site(self, data):
        site = data["sites"]["siteByUsername"][self.user]["site"]
        self.kwdict["site_id"] = site["id"]
        self.kwdict["user_id"] = site["userId"]
        return site

    def _pagination(self, url, params, key, extra=None):
        headers = {
            "Referer"          : f"{self.root}/{self.user}",
            "Authorization"    : "Bearer " + self._tkn,
            "X-Client-Platform": "web",
            "X-Client-Build"   : "1",
        }

        if extra:
            yield from map(self._transform_media, extra)

        while True:
            data = self.request_json(url, params=params, headers=headers)
            medias = data.get(key)
            if not medias:
                return

            if "cursor" in params:
                for media in medias:
                    yield media[media["type"]]
                cursor = data.get("next_cursor")
                if not cursor:
                    return
                params["cursor"] = cursor
            else:
                yield from medias
                params["page"] += 1

    def _transform_media(self, media):
        if "responsiveUrl" not in media:
            return None
        media["_id"] = media["id"]
        media["is_video"] = media["isVideo"]
        media["grid_name"] = media["gridName"]
        media["upload_date"] = media["uploadDate"]
        media["responsive_url"] = media["responsiveUrl"]
        media["video_url"] = media.get("videoUrl")
        media["image_meta"] = media.get("imageMeta")
        return media

    def _transform_video(self, media):
        media["is_video"] = True
        media["grid_name"] = ""
        media["video_url"] = media["playback_url"]
        media["responsive_url"] = media["poster_url"]
        media["upload_date"] = media["created_date"]
        return media


class VscoUserExtractor(Dispatch, VscoExtractor):
    """Extractor for a vsco user profile"""
    pattern = USER_PATTERN + r"/?$"
    example = "https://vsco.co/USER"

    def items(self):
        base = f"{self.root}/{self.user}/"
        return self._dispatch_extractors((
            (VscoAvatarExtractor    , base + "avatar"),
            (VscoGalleryExtractor   , base + "gallery"),
            (VscoSpacesExtractor    , base + "spaces"),
            (VscoCollectionExtractor, base + "collection"),
        ), ("gallery",))


class VscoGalleryExtractor(VscoExtractor):
    """Extractor for a vsco user's gallery"""
    subcategory = "gallery"
    pattern = USER_PATTERN + r"/(?:gallery|images)"
    example = "https://vsco.co/USER/gallery"

    def images(self):
        if self.user.startswith("id:"):
            url = self.root + "/vsco/gallery"
            data = self._extract_preload_state(url)
            self.kwdict["site_id"] = sid = self.user[3:]
        else:
            url = f"{self.root}/{self.user}/gallery"
            data = self._extract_preload_state(url)
            sid = self._extract_site(data)["id"]

        url = self.root + "/api/3.0/medias/profile"
        params = {
            "site_id"  : sid,
            "limit"    : "14",
            "cursor"   : None,
        }

        return self._pagination(url, params, "media")


class VscoCollectionExtractor(VscoExtractor):
    """Extractor for images from a collection on vsco.co"""
    subcategory = "collection"
    directory_fmt = ("{category}", "{user}", "collection")
    archive_fmt = "c_{user}_{id}"
    pattern = USER_PATTERN + r"/collection"
    example = "https://vsco.co/USER/collection/1"

    def images(self):
        url = f"{self.root}/{self.user}/collection/1"
        data = self._extract_preload_state(url)
        cid = self._extract_site(data)["siteCollectionId"]
        collection = data["collections"]["byId"][cid]["1"]["collection"]

        url = f"{self.root}/api/2.0/collections/{cid}/medias"
        params = {"page": 2, "size": "20"}
        return self._pagination(url, params, "medias", (
            data["medias"]["byId"][mid["id"]]["media"]
            for mid in collection
        ))


class VscoSpaceExtractor(VscoExtractor):
    """Extractor for a vsco.co space"""
    subcategory = "space"
    directory_fmt = ("{category}", "space", "{user}")
    archive_fmt = "s_{user}_{id}"
    pattern = BASE_PATTERN + r"/spaces/([^/?#]+)"
    example = "https://vsco.co/spaces/a1b2c3d4e5f"

    def images(self):
        url = f"{self.root}/spaces/{self.user}"
        data = self._extract_preload_state(url)

        posts = data["entities"]["posts"]
        images = data["entities"]["postImages"]
        for post in posts.values():
            post["image"] = images[post["image"]]

        space = data["spaces"]["byId"][self.user]
        space["postsList"] = [posts[pid] for pid in space["postsList"]]

        url = f"{self.root}/grpc/spaces/{self.user}/posts"
        params = {}
        return self._pagination(url, params, space)

    def _pagination(self, url, params, data):
        headers = {
            "Accept"       : "application/json",
            "Referer"      : f"{self.root}/spaces/{self.user}",
            "Content-Type" : "application/json",
            "Authorization": "Bearer " + self._tkn,
        }

        while True:
            for post in data["postsList"]:
                post = self._transform_media(post["image"])
                post["upload_date"] = post["upload_date"]["sec"] * 1000
                yield post

            cursor = data["cursor"]
            if cursor.get("atEnd"):
                return
            params["cursor"] = cursor["postcursorcontext"]["postId"]

            data = self.request_json(url, params=params, headers=headers)


class VscoSpacesExtractor(VscoExtractor):
    """Extractor for a vsco.co user's spaces"""
    subcategory = "spaces"
    pattern = USER_PATTERN + r"/spaces"
    example = "https://vsco.co/USER/spaces"

    def items(self):
        url = f"{self.root}/{self.user}/spaces"
        data = self._extract_preload_state(url)
        uid = self._extract_site(data)["userId"]

        headers = {
            "Accept"       : "application/json",
            "Referer"      : url,
            "Content-Type" : "application/json",
            "Authorization": "Bearer " + self._tkn,
        }
        # this would theoretically need to be paginated
        url = f"{self.root}/grpc/spaces/user/{uid}"
        data = self.request_json(url, headers=headers)

        for space in data["spacesWithRoleList"]:
            space = space["space"]
            url = f"{self.root}/spaces/{space['id']}"
            space["_extractor"] = VscoSpaceExtractor
            yield Message.Queue, url, space


class VscoAvatarExtractor(VscoExtractor):
    """Extractor for vsco.co user avatars"""
    subcategory = "avatar"
    pattern = USER_PATTERN + r"/avatar"
    example = "https://vsco.co/USER/avatar"

    def images(self):
        url = f"{self.root}/{self.user}/gallery"
        data = self._extract_preload_state(url)
        piid = self._extract_site(data)["profileImageId"]

        url = "https://im.vsco.co/" + piid
        # needs GET request, since HEAD does not redirect to full URL
        response = self.request(url, allow_redirects=False)

        return ({
            "_id"           : piid,
            "is_video"      : False,
            "grid_name"     : "",
            "upload_date"   : 0,
            "responsive_url": response.headers["Location"],
            "video_url"     : "",
            "image_meta"    : None,
            "width"         : 0,
            "height"        : 0,
        },)


class VscoImageExtractor(VscoExtractor):
    """Extractor for individual images on vsco.co"""
    subcategory = "image"
    pattern = USER_PATTERN + r"/media/([0-9a-fA-F]+)"
    example = "https://vsco.co/USER/media/0123456789abcdef"

    def images(self):
        url = f"{self.root}/{self.user}/media/{self.groups[1]}"
        data = self._extract_preload_state(url)
        media = data["medias"]["byId"].popitem()[1]["media"]
        return (self._transform_media(media),)


class VscoVideoExtractor(VscoExtractor):
    """Extractor for vsco.co videos links"""
    subcategory = "video"
    pattern = USER_PATTERN + r"/video/([^/?#]+)"
    example = "https://vsco.co/USER/video/012345678-9abc-def0"

    def images(self):
        url = f"{self.root}/{self.user}/video/{self.groups[1]}"
        data = self._extract_preload_state(url)
        media = data["medias"]["byId"].popitem()[1]["media"]

        return ({
            "_id"           : media["id"],
            "is_video"      : True,
            "grid_name"     : "",
            "upload_date"   : media["createdDate"],
            "responsive_url": media["posterUrl"],
            "video_url"     : media.get("playbackUrl"),
            "image_meta"    : None,
            "width"         : media["width"],
            "height"        : media["height"],
            "description"   : media["description"],
        },)
