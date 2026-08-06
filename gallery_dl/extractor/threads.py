# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.threads.com/

Threads (Meta) runs on the Instagram account identity and the same private
web GraphQL backend. A profile's media is loaded by the Relay query
'BarcelonaProfileMediaTabRefetchableDirectQuery' against
'https://www.threads.com/graphql/query' (NOT '/api/graphql'), paginated by an
'end_cursor'. Authentication is the logged-in '.threads.com' browser cookies
(the httpOnly 'sessionid' in particular) — export them via a DevTools HAR /
"copy as cURL" capture, because cookies.txt extensions cannot read httpOnly
cookies and will produce a stale/guest session.
"""

from .common import Extractor, Message
from .. import text, util
import itertools

BASE_PATTERN = r"(?:https?://)?(?:www\.)?threads\.(?:net|com)"
USER_PATTERN = BASE_PATTERN + r"/@([^/?#]+)"

# friendly-name / doc_id for a profile's Media tab (own posts with media).
# Meta rotates 'doc_id' with deploys; if the feed stops returning posts, open a
# profile in a logged-in browser, scroll, and grab the current 'doc_id' for the
# 'BarcelonaProfileMediaTabRefetchableDirectQuery' request from the
# '/graphql/query' call in DevTools. It can be refreshed WITHOUT editing this
# file via the 'doc-id' option in the 'threads' config block.
_MEDIA_DOC_ID = "26800538352981660"
_MEDIA_FRIENDLY = "BarcelonaProfileMediaTabRefetchableDirectQuery"
_MEDIA_ROOT_FIELD = \
    "xdt_api__v1__text_feed__user_id__profile__media__connection"
_APP_ID = "238260118697367"
_ASBD_ID = "359341"

# IG-style typename per media_type (1=image, 2=video, 8=carousel) so the sidecar
# matches the Instagram extractor's 'typename'/PostType field
_TYPENAMES = {1: "GraphImage", 2: "GraphVideo", 8: "GraphSidecar"}

# the '__relay_internal__pv__*' provider flags the web client sends with the
# media query (verbatim from a live request; 'userID'/'after'/'first'/... are
# filled in per request)
_RELAY_FLAGS = {
    "allow_page_info_for_lox_user": False,
    "__relay_internal__pv__BarcelonaIsLoggedInrelayprovider": True,
    "__relay_internal__pv__BarcelonaHasProfileSelfReplyContextrelayprovider":
        True,
    "__relay_internal__pv__BarcelonaHasDearAlgoConsumptionrelayprovider": True,
    "__relay_internal__pv__BarcelonaHasEventBadgerelayprovider": False,
    "__relay_internal__pv__BarcelonaGenAIRepliesEnabledrelayprovider": False,
    "__relay_internal__pv__BarcelonaIsSearchDiscoveryEnabledrelayprovider":
        False,
    "__relay_internal__pv__BarcelonaHasCommunitiesrelayprovider": True,
    "__relay_internal__pv__BarcelonaHasGameScoreSharerelayprovider": True,
    "__relay_internal__pv__BarcelonaHasPublicViewCountCardrelayprovider": True,
    "__relay_internal__pv__BarcelonaHasCommunityEntityCardrelayprovider": True,
    "__relay_internal__pv__BarcelonaHasScorecardCommunityrelayprovider": True,
    "__relay_internal__pv__BarcelonaHasSportTeamAllegianceCardrelayprovider":
        True,
    "__relay_internal__pv__BarcelonaHasMusicrelayprovider": True,
    "__relay_internal__pv__BarcelonaHasNewspaperLinkStylerelayprovider": False,
    "__relay_internal__pv__BarcelonaMessagingHasGroupChatsrelayprovider":
        False,
    "__relay_internal__pv__BarcelonaHasPodcastGuestCardrelayprovider": False,
    "__relay_internal__pv__BarcelonaShouldFulfillLightboxQueryrelayprovider":
        False,
    "__relay_internal__pv__BarcelonaHasMessagingrelayprovider": True,
    "__relay_internal__pv__BarcelonaHasViewerRepliedrelayprovider": True,
    "__relay_internal__pv__BarcelonaHasPrivateRepliesDeprecationrelayprovider":
        True,
    "__relay_internal__pv__BarcelonaHasGhostPostEmojiActivationrelayprovider":
        False,
    "__relay_internal__pv__BarcelonaOptionalCookiesEnabledrelayprovider": True,
    "__relay_internal__pv__BarcelonaHasDearAlgoWebProductionrelayprovider":
        False,
    "__relay_internal__pv__BarcelonaHasWebFaviconsrelayprovider": False,
    "__relay_internal__pv__BarcelonaIsCrawlerrelayprovider": False,
    "__relay_internal__pv__BarcelonaHasCommunityTopContributorsrelayprovider":
        False,
    "__relay_internal__pv__BarcelonaCanSeeSponsoredContentrelayprovider":
        False,
    "__relay_internal__pv__BarcelonaShouldShowFediverseM075Featuresrelayprovider":  # noqa: E501
        True,
    "__relay_internal__pv__BarcelonaIsInternalUserrelayprovider": False,
}


class ThreadsExtractor(Extractor):
    """Base class for Threads extractors"""
    category = "threads"
    directory_fmt = ("{category}", "{username}")
    filename_fmt = "{username}_{shortcode}_{num}.{extension}"
    archive_fmt = "{media_id}"
    root = "https://www.threads.com"
    cookies_domain = ".threads.com"
    cookies_names = ("sessionid",)
    # user-agent inherits Extractor's default (USERAGENT_FIREFOX) and is
    # overridable via the 'user-agent' config option; not pinned here.
    # request_interval is the per-request spacing default — Threads/Meta
    # throttle aggressively, so keep it polite (override via 'sleep-request').
    request_interval = (4.0, 8.0)

    def _init(self):
        self._cursor = self.config("cursor", None)
        self._tokens = None
        # Volatile API params — overridable in the 'threads' config block so the
        # rotating doc_id (and app/asbd ids) can be refreshed without editing
        # this vendored file (which a gallery-dl 'git pull' overwrites).
        self._doc_id = str(self.config("doc-id", _MEDIA_DOC_ID))
        self._app_id = str(self.config("app-id", _APP_ID))
        self._asbd_id = str(self.config("asbd-id", _ASBD_ID))
        self._page_size = self.config("page-size", 10)

    def items(self):
        self.login()
        username, user_id = self._resolve_user()
        metadata = {"username": username, "owner_id": user_id}

        own_only = not self.config("reposts", False)
        posts = self.posts(user_id)
        if max_posts := self.config("max-posts"):
            posts = itertools.islice(posts, max_posts)

        for post in posts:
            owner = str((post.get("user") or {}).get("pk") or "")
            if own_only and owner and owner != str(user_id):
                continue

            data = self._parse_post(post)
            files = data.pop("_files")
            if not files:
                continue
            data.update(metadata)
            data["count"] = len(files)

            yield Message.Directory, "", data
            for file in files:
                file = {**data, **file}
                url = file["url"]
                text.nameext_from_url(url, file)
                yield Message.Url, url, file

    def posts(self, user_id):
        return ()

    def finalize(self, status=0):
        if status and self._cursor:
            self.log.info("Use '-o cursor=%s' to continue downloading "
                          "from the current position", self._cursor)

    # -- auth -------------------------------------------------------------

    def login(self):
        if self.cookies_check(self.cookies_names):
            return
        self.log.error(
            "Threads requires logged-in '.threads.com' browser cookies "
            "(the httpOnly 'sessionid'). Export them via a DevTools HAR / "
            "'copy as cURL' capture — a cookies.txt extension cannot read the "
            "httpOnly sessionid and yields a logged-out session.")
        raise self.exc.AuthRequired("'sessionid' cookie")

    # -- profile / tokens -------------------------------------------------

    def _resolve_user(self):
        url = f"{self.root}/@{self.user}"
        page = self.request(url, headers={
            "Accept": "text/html,application/xhtml+xml,*/*",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Upgrade-Insecure-Requests": "1",
        }).text

        fb_dtsg = self._search(
            r'"DTSGInitialData",\[\],\{"token":"([^"]+)"', page)
        self._tokens = {
            "lsd"    : self._search(r'"LSD",\[\],\{"token":"([^"]+)"', page),
            "fb_dtsg": fb_dtsg,
            "av"     : self._search(r'"actorID":"(\d+)"', page),
            "csrf"   : self._cookie_value("csrftoken"),
            "jazoest": ("2" + str(sum(ord(c) for c in fb_dtsg))
                        if fb_dtsg else None),
        }

        user_id = self._search(r'"user_id":"(\d+)"', page)
        if not user_id:
            raise self.exc.NotFoundError("user")
        return self.user, user_id

    # -- GraphQL ----------------------------------------------------------

    def _graphql(self, doc_id, friendly, root_field, variables):
        tokens = self._tokens
        data = {
            "av"                     : tokens["av"],
            "__user"                 : "0",
            "__a"                    : "1",
            "__comet_req"            : "29",
            "fb_dtsg"                : tokens["fb_dtsg"],
            "jazoest"                : tokens["jazoest"],
            "lsd"                    : tokens["lsd"],
            "fb_api_caller_class"    : "RelayModern",
            "fb_api_req_friendly_name": friendly,
            "server_timestamps"      : "true",
            "doc_id"                 : doc_id,
            "variables"              : util.json_dumps(variables),
        }
        headers = {
            "Accept"          : "*/*",
            "X-FB-Friendly-Name": friendly,
            "X-FB-LSD"        : tokens["lsd"],
            "X-CSRFToken"     : tokens["csrf"],
            "X-IG-App-ID"     : self._app_id,
            "X-ASBD-ID"       : self._asbd_id,
            "X-Root-Field-Name": root_field,
            "Origin"          : self.root,
            "Referer"         : self.root + "/",
            "Sec-Fetch-Dest"  : "empty",
            "Sec-Fetch-Mode"  : "cors",
            "Sec-Fetch-Site"  : "same-origin",
        }
        # base request() already retries/backs off on HTTP 429
        # (request_interval_429); Meta ALSO soft-throttles with HTTP 200 + an
        # empty/error body — that is detected by the caller (page-0 guard).
        return self.request_json(
            self.root + "/graphql/query",
            method="POST", data=data, headers=headers)

    def _media_pagination(self, user_id):
        variables = dict(_RELAY_FLAGS)
        variables["userID"] = str(user_id)
        variables["first"] = self._page_size
        variables["before"] = None
        variables["last"] = None
        after = self._cursor
        page = 0

        while True:
            variables["after"] = after
            data = self._graphql(
                self._doc_id, _MEDIA_FRIENDLY, _MEDIA_ROOT_FIELD, variables)

            media_data = (data.get("data") or {}).get("mediaData")
            if not media_data:
                # No usable feed. On the FIRST request this is NOT end-of-feed:
                # Meta soft-throttles with an empty HTTP-200 body, and a
                # logged-out/blocked session returns mediaData:null. Surface it
                # instead of finishing silently as if the profile were empty.
                if page == 0:
                    raise self.exc.AbortExtraction(
                        "Threads returned no media. This is almost always a "
                        "rate-limit (Meta soft-throttles with an empty 200 "
                        "response) or an expired/blocked session — wait a few "
                        "minutes and/or raise 'sleep-request' in the 'threads' "
                        "config; re-export cookies if it persists.")
                return self._update_cursor(None)

            page += 1
            for edge in media_data.get("edges") or ():
                node = edge.get("node") or {}
                for item in node.get("thread_items") or ():
                    if post := item.get("post"):
                        yield post

            page_info = media_data.get("page_info") or {}
            if not page_info.get("has_next_page"):
                return self._update_cursor(None)
            after = self._update_cursor(page_info.get("end_cursor"))
            if not after:
                return

    # -- post parsing -----------------------------------------------------

    def _parse_post(self, post):
        user = post.get("user") or {}
        code = post.get("code")
        data = {
            "post_id"    : post.get("pk") or post.get("id"),
            "shortcode"  : code,
            "post_url"   : f"{self.root}/@{user.get('username')}/post/{code}",
            "date"       : self.parse_timestamp(post.get("taken_at")),
            "taken_at"   : post.get("taken_at"),
            "description": (post.get("caption") or {}).get("text") or "",
            "accessibility_caption": post.get("accessibility_caption"),
            "likes"      : post.get("like_count"),
            "fullname"   : user.get("full_name"),
            "owner_id"   : user.get("pk") or user.get("id"),
            "typename"   : _TYPENAMES.get(post.get("media_type")),
        }

        if tagged := self._people(
                (post.get("usertags") or {}).get("in"), key="user"):
            data["tagged_users"] = tagged
        if coauthors := self._people(post.get("coauthor_producers")):
            data["coauthors"] = coauthors
        self._extract_location(post, data)

        # lossless: embed the full raw post for archival / future enrichment
        # (sidecar mode is "curated + embedded raw"). NOT underscore-prefixed —
        # gallery-dl's metadata postprocessor strips '_'-keys (util.filter_dict).
        data["raw"] = post

        files = []
        for num, media in enumerate(post.get("carousel_media") or (post,), 1):
            url, is_video = self._best_media(media)
            if not url:
                continue
            files.append({
                "num"       : num,
                "media_id"  : media.get("pk") or media.get("id"),
                "url"       : url,
                "type"      : "video" if is_video else "image",
                "video_url" : url if is_video else None,
                "width"     : media.get("original_width"),
                "height"    : media.get("original_height"),
            })
        data["_files"] = files
        return data

    def _best_media(self, media):
        if versions := media.get("video_versions"):
            # video_versions[0] is the highest-quality rendition
            return versions[0].get("url"), True
        candidates = (media.get("image_versions2") or {}).get("candidates")
        if candidates:
            # candidates[0] is the largest available image
            return candidates[0].get("url"), False
        return None, False

    def _people(self, entries, key=None):
        """Normalize a list of user-ish dicts to IG-style {id,username,...}"""
        result = []
        for entry in entries or ():
            u = (entry.get(key) or {}) if key else entry
            if not isinstance(u, dict):
                continue
            uid = u.get("pk") or u.get("id")
            if not uid:
                continue
            result.append({
                "id"       : uid,
                "username" : u.get("username"),
                "full_name": u.get("full_name"),
            })
        return result

    def _extract_location(self, post, data):
        """Map Threads location → IG-style location_* fields (GPS → map).

        The exact 'meta_place' shape is not fully pinned, so probe defensively:
        the location object may be nested under 'location' or be flat. The full
        raw post is also embedded (_raw) as a lossless fallback.
        """
        place = post.get("meta_place") or post.get("metaPlace")
        if not isinstance(place, dict):
            return
        loc = place.get("location")
        if not isinstance(loc, dict):
            loc = place
        lat, lng = loc.get("lat"), loc.get("lng")
        if lat is not None and lng is not None:
            data["location_latitude"] = lat
            data["location_longitude"] = lng
        if loc_id := (loc.get("pk") or loc.get("id")):
            data["location_id"] = loc_id
        if name := (loc.get("name") or loc.get("short_name")):
            data["location_name"] = name

    # -- helpers ----------------------------------------------------------

    def _search(self, pattern, page):
        match = text.re(pattern).search(page)
        return match[1] if match else None

    def _cookie_value(self, name):
        for cookie in self.cookies:
            if cookie.name == name and \
                    "threads.com" in (cookie.domain or ""):
                return cookie.value
        return ""

    def _update_cursor(self, cursor):
        if cursor:
            self.log.debug("Cursor: %s", cursor)
        self._cursor = cursor
        return cursor


class ThreadsUserExtractor(ThreadsExtractor):
    """Extractor for a Threads user's profile media"""
    # 'posts' (matching Instagram's profile extractor) so the immich sidecar's
    # `subcategory` drives the IG person-resolution branch (owner handle + id)
    subcategory = "posts"
    pattern = USER_PATTERN + r"(?:/media)?/?(?:$|[?#])"
    example = "https://www.threads.com/@USER"

    def __init__(self, match):
        ThreadsExtractor.__init__(self, match)
        self.user = match[1]

    def posts(self, user_id):
        return self._media_pagination(user_id)
