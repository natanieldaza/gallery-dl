# -*- coding: utf-8 -*-

# Copyright 2018-2020 Leonardo Taccari
# Copyright 2018-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.instagram.com/"""

from .common import Extractor, Message, Dispatch
from .. import text, util
import itertools

BASE_PATTERN = r"(?:https?://)?(?:www\.)?instagram\.com"
USER_PATTERN = BASE_PATTERN + r"/(?!(?:p|tv|reel|explore|stories)/)([^/?#]+)"


class InstagramExtractor(Extractor):
    """Base class for instagram extractors"""
    category = "instagram"
    directory_fmt = ("{category}", "{username}")
    filename_fmt = "{sidecar_media_id:?/_/}{media_id}.{extension}"
    archive_fmt = "{media_id}"
    root = "https://www.instagram.com"
    cookies_domain = ".instagram.com"
    cookies_names = ("sessionid",)
    browser = "chrome"
    useragent = util.USERAGENT_CHROME
    request_interval = (6.0, 12.0)

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.item = match[1]

    def _init(self):
        self.www_claim = "0"
        self.csrf_token = util.generate_token()
        self._find_tags = text.re(r"#\w+").findall
        self._logged_in = True
        self._cursor = None
        self._user = None
        # Discovered lazily on the first single-post fallback and reused for the
        # whole run. None = not looked up yet, "" = looked up and not found.
        self._post_doc_id = None

        self.cookies.set(
            "csrftoken", self.csrf_token, domain=self.cookies_domain)

        if not (wd := self.config("wd", False)):
            self.cookies.set("wd", None, domain=self.cookies_domain)
        elif isinstance(wd, str):
            self.cookies.set("wd", wd, domain=self.cookies_domain)

        self.api = InstagramAPI(self)

        self._static_video = \
            True if self.config("static-videos", True) else False
        self._warn_video = \
            True if self.config("warn-videos", True) else False
        self._warn_image = (
            9 if not (wi := self.config("warn-images", True)) else
            1 if wi in {"all", "both"} else
            0)

    def items(self):
        self.login()
        data = self.metadata()

        if videos := self.config("videos", True):
            self.videos_dash = videos_dash = (videos != "merged")
        else:
            self.videos_dash = False

        if audio := self.config("audio", False):
            audio_dash = (audio != "merged")
        else:
            audio_dash = False

        if previews := self.config("previews", False):
            if isinstance(previews, str):
                previews = previews.split(",")
            elif not isinstance(previews, (list, tuple)):
                previews = {"video", "audio"}
            previews_video = ("video" in previews)
            previews_audio = ("audio" in previews)
        else:
            previews_video = previews_audio = False
        del previews

        pinned = self.config("pinned", True)
        max_posts = self.config("max-posts")
        order = self.config("order-files")
        reverse = order[0] in {"r", "d"} if order else False
        videos_headers = {"User-Agent": "Mozilla/5.0"}

        posts = self.posts()
        if max_posts:
            posts = itertools.islice(posts, max_posts)

        for post in posts:
            # immich patch: upstream deleted this branch along with
            # _parse_post_graphql. Our media() keeps a last-resort doc_id
            # fallback that can still answer with the GraphQL 'shortcode_media'
            # shape, which _parse_post cannot read. Do NOT route on
            # '__typename': the new user_feed connection nodes carry it too and
            # are REST-shaped (that is why upstream dropped the test). Only
            # media() knows it produced the legacy shape, so it says so.
            if post.pop("_immich_graphql_shape", False):
                post = self._parse_post_graphql(post)
            else:
                post = self._parse_post(post)

            if not pinned and post.get("pinned"):
                self.log.debug("%s: Skipping pinned post", post.get("post_id"))
                continue

            if self._user:
                post["user"] = self._user
            post.update(data)
            files = post.pop("_files")

            post["count"] = len(files)
            yield Message.Directory, "", post

            if reverse:
                files.reverse()

            for file in files:
                file = {**post, **file}

                if url := file.get("audio_url"):
                    if audio:
                        file["_http_headers"] = videos_headers
                        text.nameext_from_url(url, file)
                        if audio_dash and "_ytdl_manifest_data" in file:
                            file["_fallback"] = (url,)
                            file["_ytdl_manifest"] = "dash"
                            url = f"ytdl:{post['post_url']}{file['num']}.m4a"
                        yield Message.Url, url, file
                    if previews_audio and file.get("display_url"):
                        file["media_id"] = f"{file['media_id']}p"
                    else:
                        continue
                elif url := file.get("video_url"):
                    if videos:
                        file["_http_headers"] = videos_headers
                        text.nameext_from_url(url, file)
                        if videos_dash and "_ytdl_manifest_data" in file:
                            file["_fallback"] = (url,)
                            file["_ytdl_manifest"] = "dash"
                            url = f"ytdl:{post['post_url']}{file['num']}.mp4"
                        yield Message.Url, url, file
                    if previews_video:
                        file["media_id"] = f"{file['media_id']}p"
                    else:
                        continue

                url = file["display_url"]
                text.nameext_from_url(url, file)
                if file["extension"] == "webp" and "stp=dst-jpg" in url:
                    file["extension"] = "jpg"
                yield Message.Url, url, file

    def metadata(self):
        return ()

    def posts(self):
        return ()

    def finalize(self, status):
        if status and self._cursor:
            self.log.info("Use '-o cursor=%s' to continue downloading "
                          "from the current position", self._cursor)

    def request(self, url, **kwargs):
        response = Extractor.request(self, url, **kwargs)

        if response.history:

            url = response.url
            if "/accounts/login/" in url:
                page = "login"
            elif "/challenge/" in url:
                page = "challenge"
            elif 24 < len(url) < 28 and url[-1] == "/":
                page = "home"
            else:
                page = None

            if page is not None:
                raise self.exc.AbortExtraction(
                    f"HTTP redirect to {page} page ({url.partition('?')[0]})")

        www_claim = response.headers.get("x-ig-set-www-claim")
        if www_claim is not None:
            self.www_claim = www_claim

        if csrf_token := response.cookies.get("csrftoken"):
            self.csrf_token = csrf_token

        return response

    def login(self):
        if self.cookies_check(self.cookies_names):
            return

        username, password = self._get_auth_info()
        if username:
            return self.cookies_update(self.cache(
                self._login_impl, username, password,
                _exp=90*86400, _mem=False))

        self._logged_in = False

    def _login_impl(self, username, password):
        self.log.error("Login with username & password is no longer "
                       "supported. Use browser cookies instead.")
        return {}

    def _parse_post(self, post):
        if "items" in post:  # story or highlight
            items = post["items"]
            reel_type, _, reel_id = str(post["id"]).rpartition(":")
            if reel_type or post.get("reel_type") == "highlight_reel":
                post_url = f"{self.root}/stories/highlights/{reel_id}/"
                expires = None
                reel_type = "highlight"
            else:
                post_url = f"{self.root}/stories/{post['user']['username']}/"
                expires = post["seen"] + 86400
                reel_type = "story"
            data = {
                "user"   : post.get("user"),
                "expires": self.parse_timestamp(expires),
                "post_id": reel_id,
                "post_shortcode": shortcode_from_id(reel_id),
                "post_url": post_url,
                "type": reel_type,
            }
            if title := post.get("title"):
                data["highlight_title"] = title
            if not post.get("seen"):
                post["seen"] = post.get("latest_reel_media")

        else:  # regular image/video post
            data = {
                "post_id" : post["pk"],
                "post_shortcode": post["code"],
                "likes": post.get("like_count", 0),
                "liked": post.get("has_liked", False),
                "pinned": self._extract_pinned(post),
            }

            caption = post["caption"]
            data["description"] = caption["text"] if caption else ""

            if tags := self._find_tags(data["description"]):
                data["tags"] = sorted(set(tags))

            if location := post.get("location"):
                data["location_id"] = location_id = (
                    location.get("pk") or location.get("id"))
                data["location_name"] = name = (
                    location.get("name") or "")
                data["location_slug"] = slug = (
                    location.get("short_name") or name).replace(
                    " ", "-").lower()
                data["location_url"] = (
                    f"{self.root}/explore/locations/{location_id}/{slug}/")
                # immich patch: GPS + street address. Upstream keeps only
                # id/name/slug/url; these ride along when IG includes them.
                if "lat" in location and "lng" in location:
                    data["location_latitude"] = location["lat"]
                    data["location_longitude"] = location["lng"]
                if "address" in location:
                    data["location_address"] = location["address"]

            if coauthors := post.get("coauthor_producers"):
                data["coauthors"] = [
                    {"id"       : user["pk"],
                     "username" : user["username"],
                     "full_name": user["full_name"]}
                    for user in coauthors
                ]

            # --- immich patch: enrichment parity with _parse_post_graphql ---
            # The REST '/v1/media/{id}/info/' payload is richer per-media than the
            # doc_id post query, but its user block has NO follower/post counts
            # (those are profile-level — rolled into social_media via the profile
            # path instead). Capture what IS here so REST-path sidecars match the
            # GraphQL-path field shape.
            u = post.get("user") or {}
            if pic := (u.get("profile_pic_url") or
                       (u.get("hd_profile_pic_url_info") or {}).get("url")):
                data["owner_profile_pic"] = pic
            if (fc := u.get("follower_count")) is not None:
                data["owner_followers"] = fc
            if (mc := u.get("media_count")) is not None:
                data["owner_post_count"] = mc
            data["is_paid_partnership"] = post.get("is_paid_partnership", False)
            data["is_ad"] = post.get("is_ad", False)
            data["is_affiliate"] = post.get("is_affiliate", False)
            if (cc := post.get("comment_count")) is not None:
                data["comment_count"] = cc
            if alt := post.get("accessibility_caption"):
                data["accessibility_caption"] = alt
            # Comment bodies aren't reliably embedded in media-info (IG returns
            # only `comment_count` + an often-empty `preview_comments`; full
            # comments need a separate /comments/ call). Capture preview ones if
            # present. NOTE: commenter ids/usernames are OTHER accounts — never
            # auto-link them downstream.
            comments = []
            for node in (post.get("preview_comments") or ()):
                cu = node.get("user") or {}
                comments.append({
                    "text"      : node.get("text"),
                    "created_at": node.get("created_at"),
                    "owner": {
                        "id"      : cu.get("pk") or cu.get("id"),
                        "username": cu.get("username"),
                    },
                })
            if comments:
                data["comments"] = comments

            if items := post.get("carousel_media"):
                data["sidecar_media_id"] = data["post_id"]
                data["sidecar_shortcode"] = data["post_shortcode"]
            else:
                items = (post,)

        owner = post["user"]
        data["owner_id"] = owner["pk"]
        data["username"] = owner.get("username")
        data["fullname"] = owner.get("full_name")
        data["post_date"] = data["date"] = self.parse_timestamp(
            post.get("taken_at") or post.get("created_at") or post.get("seen"))
        data["_files"] = files = []
        for num, item in enumerate(items, 1):

            try:
                image = item["image_versions2"]["candidates"][0]
            except Exception:
                self.log.warning("Missing media in post %s",
                                 data["post_shortcode"])
                continue

            if not self._static_video and \
                    (type_orig := item.get("original_media_type")) and \
                    type_orig == 1 and type_orig != item.get("media_type"):
                if item.pop("video_versions", None):
                    item["original_width"] = image["width"]
                    item["original_height"] = image["height"]

            width_orig = item.get("original_width", 0)
            height_orig = item.get("original_height", 0)

            if video_versions := item.get("video_versions"):
                media = video = video_versions[-1]
                if (manifest := item.get("video_dash_manifest")) and \
                        self.videos_dash:
                    width = width_orig
                    height = height_orig
                else:
                    width = video["width"]
                    height = video["height"]

                if self._warn_video:
                    self._warn_video = False
                    pattern = text.re(
                        r"Chrome/\d{3,}\.\d+\.\d+\.\d+(?!\d* Mobile)")
                    if not pattern.search(self.session.headers["User-Agent"]):
                        self.log.warning("Potentially lowered video quality "
                                         "due to non-Chrome User-Agent")
            else:
                video = manifest = None
                media = image
                width = image["width"]
                height = image["height"]

                if self._warn_image < ((width * 1.1 < width_orig) +
                                       (height * 1.1 < height_orig)):
                    self.log.warning(
                        "%s: Available image resolutions lower than the "
                        "original (%sx%s < %sx%s). "
                        "Consider refreshing your cookies.",
                        data["post_shortcode"],
                        width, height, width_orig, height_orig)

            media = {
                "num"        : num,
                "date"       : self.parse_timestamp(item.get("taken_at") or
                                                    media.get("taken_at") or
                                                    post.get("taken_at")),
                "media_id"   : item["pk"],
                "shortcode"  : (item.get("code") or
                                shortcode_from_id(item["pk"])),
                "display_url": image["url"],
                "video_url"  : video["url"] if video else None,
                "width"          : width,
                "width_original" : width_orig,
                "height"         : height,
                "height_original": height_orig,
            }

            # immich patch: per-slide alt-text + per-video view count (parity
            # with the GraphQL parser). REST videos expose play_count/view_count.
            if (alt := item.get("accessibility_caption")) is not None:
                media["accessibility_caption"] = alt
            if (vvc := item.get("play_count")) is not None or \
                    (vvc := item.get("view_count")) is not None:
                media["video_view_count"] = vvc

            if manifest is not None:
                media["_ytdl_manifest_data"] = manifest
            # immich patch: keep a SLIM owner ref only. Upstream dumped the entire
            # raw IG user dict (account_badges, fan_club_info, hd_profile_pic_versions,
            # friendship_status, …) into every sidecar — ~80% noise that duplicated
            # the post-level owner_id/username/fullname/owner_profile_pic. Trim to
            # {id, username, full_name}, matching coauthors/tagged_users shape.
            if owner_src := (item.get("owner") or post.get("user")):
                media["owner"] = {
                    "id"       : owner_src.get("pk") or owner_src.get("id"),
                    "username" : owner_src.get("username"),
                    "full_name": owner_src.get("full_name"),
                }
            if "reshared_story_media_author" in item:
                media["author"] = item["reshared_story_media_author"]
            if "expiring_at" in item:
                media["expires"] = self.parse_timestamp(item["expiring_at"])
            if "subscription_media_visibility" in item:
                media["subscription"] = item["subscription_media_visibility"]
            if "audience" in item:
                media["audience"] = item["audience"]

            self._extract_tagged_users(item, media)
            files.append(media)

            if stickers := item.get("story_music_stickers"):
                try:
                    if audio := self._extract_audio(item, media, stickers[0]):
                        audio["num"] = num
                        files.append(audio)
                except Exception as exc:
                    self.log.traceback(exc)

        if metadata := post.get("music_metadata"):
            try:
                if audio := self._extract_audio(
                        post, data, metadata.get("music_info")):
                    num += 1
                    audio["num"] = num
                    files.append(audio)
            except Exception as exc:
                self.log.traceback(exc)

        if clips := post.get("clips_metadata"):
            try:
                if audio := self._extract_audio(post, data, clips):
                    num += 1
                    audio["num"] = num
                    files.append(audio)
            except Exception as exc:
                self.log.traceback(exc)

        if "subscription_media_visibility" in post:
            data["subscription"] = post["subscription_media_visibility"]
        if "type" not in data:
            if len(files) == 1 and files[0]["video_url"]:
                data["type"] = "reel"
                data["post_url"] = f"{self.root}/reel/{post['code']}/"
            else:
                data["type"] = "post"
                data["post_url"] = f"{self.root}/p/{post['code']}/"

        return data

    def _parse_post_graphql(self, post):
        typename = post["__typename"]

        if self._logged_in:
            if post.get("is_video") and "video_url" not in post:
                post = self.api.media(post["id"])[0]
            elif typename == "GraphSidecar" and \
                    "edge_sidecar_to_children" not in post:
                post = self.api.media(post["id"])[0]

        if pinned := post.get("pinned_for_users", ()):
            for index, user in enumerate(pinned):
                pinned[index] = int(user["id"])

        owner = post["owner"]
        data = {
            "typename"   : typename,
            "likes"      : post["edge_media_preview_like"]["count"],
            "liked"      : post.get("viewer_has_liked", False),
            "pinned"     : pinned,
            "owner_id"   : owner["id"],
            "username"   : owner.get("username"),
            "fullname"   : owner.get("full_name"),
            "post_id"    : post["id"],
            "post_shortcode": post["shortcode"],
            "post_url"   : f"{self.root}/p/{post['shortcode']}/",
            "post_date"  : self.parse_timestamp(post["taken_at_timestamp"]),
            "description": text.parse_unicode_escapes("\n".join(
                edge["node"]["text"]
                for edge in post["edge_media_to_caption"]["edges"]
            )),
        }
        data["date"] = data["post_date"]

        # --- immich patch: owner stats snapshot (followers / post count / avatar) ---
        # Present in every post's owner block; gallery-dl normally drops them. Lets the
        # backfill roll live follower/post counts into social_media with no extra call.
        if followed := owner.get("edge_followed_by"):
            data["owner_followers"] = followed.get("count")
        if timeline := owner.get("edge_owner_to_timeline_media"):
            data["owner_post_count"] = timeline.get("count")
        if pic := owner.get("profile_pic_url"):
            data["owner_profile_pic"] = pic

        # --- immich patch: sponsorship / ad flags ---
        data["is_paid_partnership"] = post.get("is_paid_partnership", False)
        data["is_ad"] = post.get("is_ad", False)
        data["is_affiliate"] = post.get("is_affiliate", False)

        if tags := self._find_tags(data["description"]):
            data["tags"] = sorted(set(tags))

        if location := post.get("location"):
            data["location_id"] = location["id"]
            data["location_slug"] = location["slug"]
            data["location_url"] = (f"{self.root}/explore/locations/"
                                    f"{location['id']}/{location['slug']}/")
            
            # Extract GPS coordinates if available
            if "lat" in location and "lng" in location:
                data["location_latitude"] = location["lat"]
                data["location_longitude"] = location["lng"]
            
            # Extract additional location details
            if "name" in location:
                data["location_name"] = location["name"]
            # immich patch: the real field is `address_json` (a JSON *string*), not
            # `address`. Parse it for street/zip/city. Coordinates are NOT present in
            # the post payload — they're resolved on-demand from location_id elsewhere.
            if address := (location.get("address_json") or location.get("address")):
                if isinstance(address, str):
                    try:
                        address = util.json.loads(address)
                    except Exception:
                        address = None
                if address:
                    data["location_address"] = address

        if coauthors := post.get("coauthor_producers"):
            data["coauthors"] = [
                {"id"      : user["id"],
                 "username": user["username"]}
                for user in coauthors
            ]

        # --- immich patch: comments (already embedded in the post response) ---
        # Keep a trimmed set: text + when + who. The response embeds only the first
        # ~N (IG paginates the rest), so also store the true total `comment_count`.
        # NOTE downstream: commenter ids/usernames are OTHER accounts — never auto-link.
        if parent_comments := post.get("edge_media_to_parent_comment"):
            data["comment_count"] = parent_comments.get("count")
            comments = []
            for edge in parent_comments.get("edges", ()):
                node = edge.get("node") or {}
                cowner = node.get("owner") or {}
                comments.append({
                    "text"      : node.get("text"),
                    "created_at": node.get("created_at"),
                    "owner": {
                        "id"      : cowner.get("id"),
                        "username": cowner.get("username"),
                    },
                })
            if comments:
                data["comments"] = comments

        data["_files"] = files = []
        if "edge_sidecar_to_children" in post:
            for num, edge in enumerate(
                    post["edge_sidecar_to_children"]["edges"], 1):
                node = edge["node"]
                dimensions = node["dimensions"]
                media = {
                    "num": num,
                    "media_id"   : node["id"],
                    "date"       : data["date"],
                    "shortcode"  : (node.get("shortcode") or
                                    shortcode_from_id(node["id"])),
                    "display_url": node["display_url"],
                    "video_url"  : node.get("video_url"),
                    "width"      : dimensions["width"],
                    "height"     : dimensions["height"],
                    "sidecar_media_id" : post["id"],
                    "sidecar_shortcode": post["shortcode"],
                    # immich patch: per-slide alt-text + per-video view count
                    "accessibility_caption": node.get("accessibility_caption"),
                    "video_view_count": node.get("video_view_count"),
                }
                self._extract_tagged_users(node, media)
                files.append(media)
        else:
            dimensions = post["dimensions"]
            media = {
                "num"        : 1,
                "media_id"   : post["id"],
                "date"       : data["date"],
                "shortcode"  : post["shortcode"],
                "display_url": post["display_url"],
                "video_url"  : post.get("video_url"),
                "width"      : dimensions["width"],
                "height"     : dimensions["height"],
                # immich patch: alt-text + per-video view count
                "accessibility_caption": post.get("accessibility_caption"),
                "video_view_count": post.get("video_view_count"),
            }
            self._extract_tagged_users(post, media)
            files.append(media)

        return data

    def _extract_tagged_users(self, src, dest):
        """Extract tagged users with their position coordinates on the image.
        
        Position coordinates are normalized (0.0 to 1.0) where:
        - x=0.0 is left edge, x=1.0 is right edge
        - y=0.0 is top edge, y=1.0 is bottom edge
        
        Args:
            src: Source data containing tag information
            dest: Destination dictionary to store tagged user data
        """
        dest["tagged_users"] = tagged_users = []
        extract_positions = self.config("tagged-user-positions", True)

        if edges := src.get("edge_media_to_tagged_user"):
            for edge in edges["edges"]:
                user = edge["node"]["user"]
                tagged_user = {
                    "id"       : user["id"],
                    "username" : user["username"],
                    "full_name": user["full_name"]
                }
                
                # Extract coordinates if available and enabled (GraphQL API)
                if extract_positions and "x" in edge["node"] and "y" in edge["node"]:
                    tagged_user["position"] = {
                        "x": edge["node"]["x"],
                        "y": edge["node"]["y"]
                    }
                
                tagged_users.append(tagged_user)

        if usertags := src.get("usertags"):
            for tag in usertags["in"]:
                user = tag["user"]
                tagged_user = {
                    "id"       : user["pk"],
                    "username" : user["username"],
                    "full_name": user["full_name"]
                }
                
                # Extract coordinates from position data (REST API)
                if extract_positions and "position" in tag and tag["position"]:
                    tagged_user["position"] = {
                        "x": tag["position"][0],  # x coordinate (0.0 to 1.0)
                        "y": tag["position"][1]   # y coordinate (0.0 to 1.0)
                    }
                
                tagged_users.append(tagged_user)

        if mentions := src.get("reel_mentions"):
            for mention in mentions:
                user = mention["user"]
                tagged_user = {
                    "id"       : user.get("pk"),
                    "username" : user["username"],
                    "full_name": user["full_name"]
                }
                
                # Extract mention position for stories/reels
                if extract_positions and "x" in mention and "y" in mention:
                    tagged_user["position"] = {
                        "x": mention["x"],
                        "y": mention["y"]
                    }
                    
                    # Extract additional mention metadata
                    if "width" in mention and "height" in mention:
                        tagged_user["dimensions"] = {
                            "width": mention["width"],
                            "height": mention["height"]
                        }
                        
                    if "rotation" in mention:
                        tagged_user["rotation"] = mention["rotation"]
                    
                tagged_users.append(tagged_user)

        if stickers := src.get("story_bloks_stickers"):
            for sticker in stickers:
                # immich patch: keep the sticker GEOMETRY (position, size,
                # rotation) that upstream's rewrite dropped, but adopt the guard
                # and the .get() calls it added — a malformed sticker should
                # cost one mention, not the whole story.
                try:
                    sticker = sticker["bloks_sticker"]
                    if sticker["bloks_sticker_type"] == "mention":
                        user = sticker["sticker_data"]["ig_mention"]
                        tagged_user = {
                            "id"       : user.get("account_id"),
                            "username" : user.get("username"),
                            "full_name": user.get("full_name"),
                        }

                        if extract_positions and "x" in sticker and "y" in sticker:
                            tagged_user["position"] = {
                                "x": sticker["x"],
                                "y": sticker["y"],
                            }

                            if "width" in sticker and "height" in sticker:
                                tagged_user["dimensions"] = {
                                    "width": sticker["width"],
                                    "height": sticker["height"],
                                }

                            if "rotation" in sticker:
                                tagged_user["rotation"] = sticker["rotation"]

                        tagged_users.append(tagged_user)
                except Exception:
                    pass

    def _is_reel(self, post):
        product_type = post.get("product_type") or post.get(
            "media_product_type")
        return (
            product_type == "clips" or
            post.get("subtype_name_for_REST__") == "XDTClipsMedia" or
            "clips_metadata" in post
        )

    def _extract_pinned(self, post):
        return (post.get("timeline_pinned_user_ids") or
                post.get("clips_tab_pinned_user_ids") or ())

    def _extract_audio(self, src, dest, info):
        if not info or not (audio := info.get("music_asset_info") or
                            info.get("original_sound_info")):
            return None
        cinfo = info.get("music_consumption_info") or audio

        dest["audio_title"] = title = audio.get("title") or audio.get(
            "original_audio_title")
        dest["audio_duration"] = duration = audio.get(
            "duration_in_ms", 0) / 1000
        dest["audio_user"] = user = audio.get(
            "ig_artist") or cinfo.get("ig_artist")

        if parts := audio.get("audio_parts"):
            artist = [a for p in parts if (a := p.get("display_artist"))]
            timestamps = [p.get("parent_start_time_in_ms") for p in parts]
        else:
            artist = audio.get("display_artist") or cinfo.get("display_artist")
            timestamps = audio.get("highlight_start_times_in_ms")
        dest["audio_artist"] = artist
        dest["audio_timestamps"] = timestamps

        if not (url := audio.get("progressive_download_url")):
            return None
        audio_id = audio.get("id") or audio.get("audio_asset_id") or 0

        file = {
            "date"       : self.parse_timestamp(src.get("taken_at")),
            "media_id"   : audio_id,
            "shortcode"  : shortcode_from_id(audio_id),
            "display_url": audio.get("cover_artwork_uri"),
            "audio_url"  : url,
            "width"           : 0,
            "width_original"  : 0,
            "height"          : 0,
            "height_original" : 0,
            "audio_user"      : user,
            "audio_title"     : title,
            "audio_artist"    : artist,
            "audio_duration"  : duration,
            "audio_timestamps": timestamps,
        }

        if manifest := audio.get("dash_manifest"):
            file["_ytdl_manifest_data"] = manifest
        return file

    def _init_cursor(self):
        cursor = self.config("cursor", True)
        if cursor is True:
            return None
        elif not cursor:
            self._update_cursor = util.identity
        return cursor

    def _update_cursor(self, cursor):
        if cursor:
            self.log.debug("Cursor: %s", cursor)
        self._cursor = cursor
        return cursor

    def _assign_user(self, user):
        self._user = user

        for key, old in (
                ("count_media"     , "edge_owner_to_timeline_media"),
                ("count_video"     , "edge_felix_video_timeline"),
                ("count_saved"     , "edge_saved_media"),
                ("count_mutual"    , "edge_mutual_followed_by"),
                ("count_follow"    , "edge_follow"),
                ("count_followed"  , "edge_followed_by"),
                ("count_collection", "edge_media_collections")):
            try:
                user[key] = user.pop(old)["count"]
            except Exception:
                user[key] = 0


class InstagramPostExtractor(InstagramExtractor):
    """Extractor for an Instagram post"""
    subcategory = "post"
    pattern = (r"(?:https?://)?(?:www\.)?instagram\.com"
               r"/(?:share()(?:/(?:p|tv|reels?()))?"
               r"|(?:[^/?#]+/)?(?:p|tv|reels?()))"
               r"/([^/?#]+)")
    example = "https://www.instagram.com/p/abcdefg/"

    def __init__(self, match):
        if match[2] is not None or match[3] is not None:
            self.subcategory = "reel"
        InstagramExtractor.__init__(self, match)

    def posts(self):
        share, _, _, shortcode = self.groups
        if share is not None:
            url = text.ensure_http_scheme(self.url)
            headers = {
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
            }
            location = self.request_location(url, headers=headers)
            shortcode = location.split("/")[-2]
        return self.api.media(shortcode)


class InstagramUserExtractor(Dispatch, InstagramExtractor):
    """Extractor for an Instagram user profile"""
    pattern = USER_PATTERN + r"/?(?:$|[?#])"
    example = "https://www.instagram.com/USER/"

    def items(self):
        base = f"{self.root}/{self.item}/"
        stories = f"{self.root}/stories/{self.item}/"
        return self._dispatch_extractors((
            (InstagramInfoExtractor      , base + "info/"),
            (InstagramAvatarExtractor    , base + "avatar/"),
            (InstagramStoriesExtractor   , stories),
            (InstagramHighlightsExtractor, base + "highlights/"),
            (InstagramPostsExtractor     , base + "posts/"),
            (InstagramPhotosExtractor    , base + "photos/"),
            (InstagramReelsExtractor     , base + "reels/"),
            (InstagramTaggedExtractor    , base + "tagged/"),
        ), ("posts",))


class InstagramPostsExtractor(InstagramExtractor):
    """Extractor for an Instagram user's posts"""
    subcategory = "posts"
    pattern = USER_PATTERN + r"/posts"
    example = "https://www.instagram.com/USER/posts/"

    def posts(self):
        return self.api.user_feed(self.item)

    def _extract_pinned(self, post):
        try:
            return post["timeline_pinned_user_ids"]
        except KeyError:
            return ()


class InstagramPhotosExtractor(InstagramExtractor):
    """Extractor for an Instagram user's photos"""
    subcategory = "photos"
    pattern = USER_PATTERN + r"/photos"
    example = "https://www.instagram.com/USER/photos/"

    def posts(self):
        for post in self.api.user_feed(self.item):
            if not self._is_reel(post):
                yield post


class InstagramReelsExtractor(InstagramExtractor):
    """Extractor for an Instagram user's reels"""
    subcategory = "reels"
    pattern = USER_PATTERN + r"/reels"
    example = "https://www.instagram.com/USER/reels/"

    def posts(self):
        for reel in self.api.user_reels(self.item):
            yield from self.api.media(reel["media"]["code"])

    def _extract_pinned(self, post):
        try:
            return post["clips_tab_pinned_user_ids"]
        except KeyError:
            return ()


class InstagramTaggedExtractor(InstagramExtractor):
    """Extractor for an Instagram user's tagged posts"""
    subcategory = "tagged"
    pattern = USER_PATTERN + r"/tagged"
    example = "https://www.instagram.com/USER/tagged/"

    def metadata(self):
        user = self.api.user(self.item)
        return {
            "tagged_owner_id" : user["id"],
            "tagged_username" : user["username"],
            "tagged_full_name": user.get("full_name"),
        }

    def posts(self):
        for post in self.api.user_tagged(self.item):
            yield from self.api.media(post["code"])


class InstagramSavedExtractor(InstagramExtractor):
    """Extractor for an Instagram user's saved media"""
    subcategory = "saved"
    pattern = USER_PATTERN + r"/saved(?:/all-posts)?/?$"
    example = "https://www.instagram.com/USER/saved/"

    def posts(self):
        return self.api.user_saved()


class InstagramCollectionExtractor(InstagramExtractor):
    """Extractor for Instagram collection"""
    subcategory = "collection"
    pattern = USER_PATTERN + r"/saved/([^/?#]+)/([^/?#]+)"
    example = "https://www.instagram.com/USER/saved/COLLECTION/12345"

    def __init__(self, match):
        InstagramExtractor.__init__(self, match)
        self.user, self.collection_name, self.collection_id = match.groups()

    def metadata(self):
        return {
            "collection_id"  : self.collection_id,
            "collection_name": text.unescape(self.collection_name),
        }

    def posts(self):
        return self.api.user_collection(self.collection_id)


class InstagramStoriesTrayExtractor(InstagramExtractor):
    """Extractor for your Instagram account's stories tray"""
    subcategory = "stories-tray"
    pattern = BASE_PATTERN + r"/stories/me/?$()"
    example = "https://www.instagram.com/stories/me/"

    def items(self):
        base = self.root + "/stories/id:"
        for story in self.api.reels_tray():
            story["date"] = self.parse_timestamp(story["latest_reel_media"])
            story["_extractor"] = InstagramStoriesExtractor
            yield Message.Queue, f"{base}{story['id']}/", story


class InstagramStoriesExtractor(InstagramExtractor):
    """Extractor for Instagram stories"""
    subcategory = "stories"
    pattern = (r"(?:https?://)?(?:www\.)?instagram\.com"
               r"/s(?:tories/(?:highlights/(\d+)|([^/?#]+)(?:/(\d+))?)"
               r"|/(aGlnaGxpZ2h0[^?#]+)(?:\?story_media_id=(\d+))?)")
    example = "https://www.instagram.com/stories/USER/"

    def __init__(self, match):
        h1, self.user, m1, h2, m2 = match.groups()

        if self.user:
            self.highlight_id = None
        else:
            self.subcategory = InstagramHighlightsExtractor.subcategory
            self.highlight_id = "highlight:" + h1 if h1 else util.b64decode(h2)

        self.media_id = m1 or m2
        InstagramExtractor.__init__(self, match)

    def posts(self):
        reel_id = self.highlight_id or self.api.user(self.user)["id"]
        reels = list(self.api.reels_media((reel_id,)))

        if not reels:
            return ()

        if self.media_id:
            reel = reels[0]
            for item in reel["items"]:
                if item["pk"] == self.media_id:
                    reel["items"] = (item,)
                    break
            else:
                raise self.exc.NotFoundError("story")

        elif self.config("split"):
            reel = reels[0]
            reels = []
            for item in reel["items"]:
                item.pop("user", None)
                copy = reel.copy()
                copy.update(item)
                copy["items"] = (item,)
                reels.append(copy)

        return reels


class InstagramHighlightsExtractor(InstagramExtractor):
    """Extractor for an Instagram user's story highlights"""
    subcategory = "highlights"
    pattern = USER_PATTERN + r"/highlights"
    example = "https://www.instagram.com/USER/highlights/"

    def posts(self):
        return self.api.highlights_media(self.item)


class InstagramFollowersExtractor(InstagramExtractor):
    """Extractor for an Instagram user's followers"""
    subcategory = "followers"
    pattern = USER_PATTERN + r"/followers"
    example = "https://www.instagram.com/USER/followers/"

    def items(self):
        uid = self.api.user(self.item)["id"]
        for user in self.api.user_followers(uid):
            user["_extractor"] = InstagramUserExtractor
            url = f"{self.root}/{user['username']}"
            yield Message.Queue, url, user


class InstagramFollowingExtractor(InstagramExtractor):
    """Extractor for an Instagram user's followed users"""
    subcategory = "following"
    pattern = USER_PATTERN + r"/following"
    example = "https://www.instagram.com/USER/following/"

    def items(self):
        uid = self.api.user(self.item)["id"]
        for user in self.api.user_following(uid):
            user["_extractor"] = InstagramUserExtractor
            url = f"{self.root}/{user['username']}"
            yield Message.Queue, url, user


class InstagramTagExtractor(InstagramExtractor):
    """Extractor for Instagram tags"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{subcategory}", "{tag}")
    pattern = BASE_PATTERN + r"/explore/tags/([^/?#]+)"
    example = "https://www.instagram.com/explore/tags/TAG/"

    def metadata(self):
        return {"tag": text.unquote(self.item)}

    def posts(self):
        return self.api.tags_media(self.item)


class InstagramLocationExtractor(InstagramExtractor):
    """Extractor for Instagram location pages"""
    subcategory = "location"
    directory_fmt = ("{category}", "{subcategory}", "{location_name|location_id}")
    pattern = BASE_PATTERN + r"/explore/locations/(\d+)/([^/?#]+)"
    example = "https://www.instagram.com/explore/locations/1987805821318734/varadero-beach/"

    def __init__(self, match):
        InstagramExtractor.__init__(self, match)
        self.location_id = match[1]
        self.location_slug = match[2]

    def metadata(self):
        return {
            "location_id": self.location_id,
            "location_slug": self.location_slug,
            "location_name": self.location_slug.replace("-", " ").title(),
        }

    def posts(self):
        return self.api.location_media(self.location_id)


class InstagramInfoExtractor(InstagramExtractor):
    """Extractor for an Instagram user's profile data"""
    subcategory = "info"
    pattern = USER_PATTERN + r"/info"
    example = "https://www.instagram.com/USER/info/"

    def items(self):
        user = self.api.user(self.item, check_private=False)
        return iter(((Message.Directory, "", user.copy()),))


class InstagramAvatarExtractor(InstagramExtractor):
    """Extractor for an Instagram user's avatar"""
    subcategory = "avatar"
    pattern = USER_PATTERN + r"/avatar"
    example = "https://www.instagram.com/USER/avatar/"

    def posts(self):
        if self._logged_in:
            # immich patch: take the avatar from the user block `user()` has
            # ALREADY built. It used to resolve the handle, throw the result
            # away and spend a second request on /v1/users/<id>/info/ for the
            # same profile — an endpoint Instagram has refused since late
            # September 2026 (see _PROFILE_DOC_ID), which is what broke this
            # extractor. PolarisProfilePageContentQuery carries
            # `hd_profile_pic_url_info` and `profile_pic_url`, so the first
            # lookup is now sufficient and the second is pure cost.
            user = self.api.user(self.item, check_private=False)
            if "hd_profile_pic_url_info" not in user and \
                    "hd_profile_pic_versions" not in user:
                # A thin block — topsearch answered and the upgrade failed.
                # Worth one attempt at the old endpoint before giving up.
                user = self.api.user_by_id(user["id"])
            avatar = (user.get("hd_profile_pic_url_info") or
                      (user.get("hd_profile_pic_versions") or [None])[-1] or
                      {"url": user["profile_pic_url"]})
            # The GraphQL profile gives {"url": ...} and nothing else, where
            # the REST one carried width/height. Default them rather than
            # KeyError, exactly as the logged-out branch below already does.
            avatar = {"url"   : avatar["url"],
                      "width" : avatar.get("width", 0),
                      "height": avatar.get("height", 0)}
        else:
            user = self.item
            if user.startswith("id:"):
                user = self.api.user_by_id(user[3:])
            else:
                user = self.api.user_by_screen_name(user)
                user["pk"] = user["id"]
            url = user.get("profile_pic_url_hd") or user["profile_pic_url"]
            avatar = {"url": url, "width": 0, "height": 0}

        if pk := user.get("profile_pic_id"):
            pk = pk.partition("_")[0]
            code = shortcode_from_id(pk)
        else:
            pk = code = "avatar:" + str(user.get("pk") or user["id"])

        return ({
            "pk"        : pk,
            "code"      : code,
            "user"      : user,
            "caption"   : None,
            "like_count": 0,
            "image_versions2": {"candidates": (avatar,)},
        },)


class InstagramAPI():

    def __init__(self, extractor):
        self.extractor = extractor
        self.exc = extractor.exc

        _cache = self.extractor.config("user-cache", True)
        if not _cache or _cache == "memory":
            self._user_cache_mem = True
            self._user_cache_exp = 0
        else:
            self._user_cache_mem = False
            self._user_cache_exp = (text.parse_int(_cache.partition(":")[2])
                                    if isinstance(_cache, str) else 0)

        if strategy := self.extractor.config("user-strategy"):
            if isinstance(strategy, str):
                strategy = strategy.split(",")
            self._strategy_uid = strategy
        else:
            self._strategy_uid = ("search", "web")

    def highlights_media(self, handle, chunk_size=5):
        reel_ids = [hl["id"] for hl in self.highlights_tray(handle)]

        if order := self.extractor.config("order-posts"):
            if order in {"desc", "reverse"}:
                reel_ids.reverse()
            elif order in {"id", "id_asc"}:
                reel_ids.sort(key=lambda r: int(r[10:]))
            elif order == "id_desc":
                reel_ids.sort(key=lambda r: int(r[10:]), reverse=True)
            elif order != "asc":
                self.extractor.log.warning("Unknown posts order '%s'", order)

        for offset in range(0, len(reel_ids), chunk_size):
            yield from self.reels_media(
                reel_ids[offset : offset+chunk_size])

    def highlights_tray(self, handle):
        user = self.user(handle)
        variables = {"user_id": str(user["id"])}

        return self._pagination_graphql(
            "PolarisProfileStoryHighlightsTrayContentQuery",
            "highlights",
            "",
            "26970053832668570",
            variables)

    def highlights_tray_legacy(self, user_id):
        endpoint = f"/v1/highlights/{user_id}/highlights_tray/"
        return self._call(endpoint)["tray"]

    def media(self, shortcode):
        # PRIMARY: REST '/v1/media/{id}/info/'. This endpoint was briefly gated
        # (302 -> logged-out home), which is why the doc_id GraphQL query was
        # used instead; that doc_id has since rotated and now returns throttled
        # empty responses ('execution error' / data:null, HTTP 200, ~90 bytes),
        # so single-post downloads broke. REST works again, so it is primary;
        # the doc_id query is kept as a fallback (refresh _POST_DOC_ID to
        # re-enable the richer GraphQL parse). The per-post parser is chosen by
        # payload shape ('__typename'), so REST items route to _parse_post_rest
        # and a doc_id result routes to _parse_post_graphql automatically.
        #
        # Gating is an account/IP-wide state, not a per-post one, so once a
        # 302-to-home is seen there is nothing to gain from asking again for
        # every remaining post: each attempt is a wasted round-trip that also
        # counts against whatever budget produced the gate. The verdict is
        # therefore remembered in gallery-dl's persistent cache (see
        # _rest_media_gated) — every download runs in its own process, so an
        # in-memory flag would be forgotten between posts.
        if shortcode.isdigit():
            # Re-fetch path (e.g. video/sidecar) passes a numeric media id.
            media_id = shortcode
        else:
            sc = shortcode[:-28] if len(shortcode) > 28 else shortcode
            media_id = id_from_shortcode(sc)
        if self._rest_media_gated():
            self.extractor.log.debug(
                "instagram REST media() skipped for %s (gate remembered from "
                "an earlier run); going straight to doc_id GraphQL", shortcode)
        else:
            try:
                items = list(self._pagination(f"/v1/media/{media_id}/info/"))
                if items:
                    return items
            except Exception as exc:
                # Only the gate signature latches. A 404 on a deleted post or a
                # transient network error must not disable REST for a day.
                if _REST_GATED_RE(str(exc)):
                    self._mark_rest_media_gated()
                self.extractor.log.debug(
                    "instagram REST media() failed for %s (%s); "
                    "falling back to doc_id GraphQL", shortcode, exc)

        # FALLBACK: the same GraphQL query the web client itself runs for a post
        # page, PolarisPostRootQuery. Its doc_id is discovered from the post's
        # own HTML rather than hardcoded, so it cannot go stale (see
        # _discover_post_doc_id); _POST_DOC_ID is only the last-resort pin.
        sc = shortcode_from_id(shortcode) if shortcode.isdigit() else (
            shortcode[:-28] if len(shortcode) > 28 else shortcode)
        doc_id = self._discover_post_doc_id(sc) or _POST_DOC_ID
        data = {
            "doc_id"   : doc_id,
            # The relay provider flags are not optional padding: omit them and
            # the query is rejected outright ('execution error').
            "variables": util.json_dumps({
                "shortcode": sc,
                "__relay_internal__pv__PolarisShortDramaEnabledrelayprovider"
                : False,
                "__relay_internal__pv__PolarisMultiCaptionCarouselEnabled"
                "relayprovider": False,
            }),
        }
        response = self._call(
            "https://www.instagram.com/graphql/query", method="POST", data=data)
        payload = response.get("data") or {}

        # PolarisPostRootQuery answers with the REST payload shape — an 'items'
        # list identical to /v1/media/{id}/info/ — so these route straight to
        # _parse_post_rest, no typename juggling needed.
        web_info = payload.get("xdt_api__v1__media__shortcode__web_info")
        if web_info:
            items = web_info.get("items")
            if items:
                return items

        # Older doc_ids answered with the GraphQL 'shortcode_media' shape, which
        # the GraphQL parser handles once 'XDT' typename prefixes are stripped.
        post = payload.get("xdt_shortcode_media")
        if not post:
            return ()
        post = _strip_xdt_typenames(post)
        # Flag the legacy shape for items(); see the routing note there.
        post["_immich_graphql_shape"] = True
        return (post,)

    def _rest_media_gated(self):
        # Persisted in gallery-dl's cache database (_mem=False), so the verdict
        # survives the process and the whole queue stops re-probing a dead
        # endpoint. A miss or an expired entry calls _rest_media_ungated(),
        # which answers False — i.e. the gate lapses on its own and REST gets
        # another chance, no manual reset needed. To clear it early:
        # `gallery-dl --clear-cache instagram`.
        return bool(self.extractor.cache(
            _rest_media_ungated, _key=None,
            _exp=self._rest_gate_ttl(), _mem=False))

    def _mark_rest_media_gated(self):
        ttl = self._rest_gate_ttl()
        self.extractor.cache_update(
            _rest_media_ungated, value=True, _exp=ttl, _mem=False)
        self.extractor.log.debug(
            "instagram REST media/info is gated; skipping it for %.1f h and "
            "using doc_id GraphQL", ttl / 3600)

    def _rest_gate_ttl(self):
        ttl = self.extractor.config("rest-gate-ttl")
        return _REST_GATE_TTL if ttl is None else int(ttl)

    def _discover_post_doc_id(self, shortcode):
        # A post's HTML embeds Relay's preloader manifest, which lists every
        # query the page is about to run together with its CURRENT id:
        #   {"queryID":"27852811784380813","variables":{"shortcode":"..."},
        #    "queryName":"PolarisPostRootQuery"}
        # Reading it there is what stops this from breaking every time Instagram
        # rotates the id — the previous hardcoded doc_id died exactly that way,
        # and its only documented fix was a manual DevTools capture.
        #
        # Browser-ish headers are REQUIRED. Requested as an API client, the same
        # URL returns a ~630 kB generic app shell with no manifest and no post
        # data at all; as a document it returns ~1 MB containing both.
        doc_id = self.extractor._post_doc_id
        if doc_id is not None:
            return doc_id or None

        try:
            response = self.extractor.request(
                f"https://www.instagram.com/p/{shortcode}/", headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;"
                              "q=0.9,*/*;q=0.8",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1",
                })
            match = _POST_DOC_ID_RE(response.text)
            doc_id = match[1] if match else ""
        except Exception as exc:
            self.extractor.log.debug(
                "instagram doc_id discovery failed for %s (%s)", shortcode, exc)
            doc_id = ""

        if doc_id:
            self.extractor.log.debug(
                "instagram discovered PolarisPostRootQuery doc_id %s", doc_id)
        # Cached either way, including the empty miss: one failed lookup per run
        # is diagnostic, one per post is a stampede.
        self.extractor._post_doc_id = doc_id
        return doc_id or None

    def reels_media(self, reel_ids):
        variables = {
            "initial_reel_id": reel_ids[0],
            "reel_ids"       : reel_ids,
            "first": 3,
            "last" : 2,
            "__relay_internal__pv__"
            "PolarisCommunityNoteStoriesLabelEnabledrelayprovider": True,
        }

        return self._pagination_graphql(
            "PolarisStoriesV3HighlightsPageQuery",
            "xdt_api__v1__feed__reels_media__connection",
            "",
            "28325328583775973",
            variables)

    def reels_media_legacy(self, reel_ids):
        endpoint = "/v1/feed/reels_media/"
        params = {"reel_ids": reel_ids}
        try:
            return self._call(endpoint, params=params)["reels_media"]
        except KeyError:
            raise self.exc.AuthRequired("authenticated cookies")

    def reels_tray(self):
        endpoint = "/v1/feed/reels_tray/"
        return self._call(endpoint)["tray"]

    def tags_media(self, tag):
        for section in self.tags_sections(tag):
            for media in section["layout_content"]["medias"]:
                yield media["media"]

    def tags_sections(self, tag):
        endpoint = f"/v1/tags/{tag}/sections/"
        data = {
            "include_persistent": "0",
            "max_id" : None,
            "page"   : None,
            "surface": "grid",
            "tab"    : "recent",
        }
        return self._pagination_sections(endpoint, data)

    def location_media(self, location_id):
        """Fetch media from a specific location"""
        for section in self.location_sections(location_id):
            for media in section["layout_content"]["medias"]:
                yield media["media"]

    def location_sections(self, location_id):
        """Fetch location sections data"""
        endpoint = f"/v1/locations/{location_id}/sections/"
        data = {
            "include_persistent": "0",
            "max_id" : None,
            "page"   : None,
            "surface": "grid",
            "tab"    : "recent",
        }
        return self._pagination_sections(endpoint, data)

    def user_by_id(self, user_id):
        return self.extractor.cache(
            self._user_by_id_impl, user_id,
            _exp=self._user_cache_exp, _mem=self._user_cache_mem)

    def _user_by_id_impl(self, user_id):
        endpoint = f"/v1/users/{user_id}/info/"
        try:
            # immich patch: ONE attempt, not the usual five.
            #
            # Instagram decommissioned this endpoint in late September 2026 —
            # it answers 429 with an empty body, no Retry-After and a
            # text/html content type, for any account, on a fresh session,
            # after hours of idling (its sibling /v1/media/<id>/info/ still
            # answers 400 + JSON to a bogus id, so the handler is simply gone
            # rather than throttled). Retrying that costs five minutes of a
            # download lane to learn nothing.
            #
            # Every caller now reaches this only after the GraphQL profile
            # query has already failed, so a fast "no" is the useful answer.
            return self._call(endpoint, notfound="user", retries=0)["user"]
        except self.extractor.exc.ControlException:
            raise
        except Exception:
            raise self.exc.NotFoundError("user")

    def user_by_name(self, username):
        return self.extractor.cache(
            self._user_by_name_impl, username,
            _exp=self._user_cache_exp, _mem=self._user_cache_mem)

    def _user_by_name_impl(self, username):
        endpoint = "/v1/users/web_profile_info/"
        params = {"username": username}
        try:
            return self._call(
                endpoint, params=params, notfound="user")["data"]["user"]
        except self.extractor.exc.ControlException:
            raise
        except Exception:
            raise self.exc.NotFoundError("user")

    def user_by_search(self, username):
        return self.extractor.cache(
            self._user_by_search_impl, username,
            _exp=self._user_cache_exp, _mem=self._user_cache_mem)

    def _user_by_search_impl(self, username):
        url = "https://www.instagram.com/web/search/topsearch/"
        params = {"query": username}

        name = username.lower()
        try:
            for result in self._call(url, params=params)["users"]:
                user = result["user"]
                if user["username"].lower() == name:
                    return user
        except self.extractor.exc.ControlException:
            raise
        except Exception:
            pass
        raise self.exc.NotFoundError("user")

    def user_by_web(self, username):
        return self.extractor.cache(
            self._user_by_web_impl, username,
            _exp=self._user_cache_exp, _mem=self._user_cache_mem)

    def _user_by_web_impl(self, username):
        url = "https://www.instagram.com/" + username

        try:
            headers = {
                "Accept": "text/html,application/xhtml+xml,"
                          "application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Alt-Used": "www.instagram.com",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Priority": "u=0, i",
            }
            page = self.extractor.request(url, headers=headers).text
            user = {}
            if user_id := text.extr(page, '"profile_id":"', '"'):
                user["id"] = user_id
            if username := text.extr(page, '"username":"', '"'):
                user["username"] = username
        except Exception:
            pass
        if user:
            return user
        raise self.exc.NotFoundError("user")

    def user_by_screen_name(self, screen_name):
        for strategy in self._strategy_uid:
            try:
                if strategy in {"search", "topsearch"}:
                    return self.user_by_search(screen_name)
                elif strategy in {"info", "web_profile_info", "api"}:
                    return self.user_by_name(screen_name)
                elif strategy in {"web", "webpage"}:
                    return self.user_by_web(screen_name)
                else:
                    self.extractor.log.warning("Invalid strategy %r", strategy)
            except Exception:
                self.extractor.log.debug("Failed to get user via %r", strategy)
        raise self.exc.NotFoundError("user")

    def user(self, screen_name, check_private=True):
        if screen_name.startswith("id:"):
            uid = screen_name[3:]
            # immich patch: GraphQL first here too. This branch used to go
            # STRAIGHT to /v1/users/<id>/info/, the endpoint Instagram
            # decommissioned in late September 2026 (see _PROFILE_DOC_ID), so
            # every `instagram.com/id:<uid>/` url spent five retries a minute
            # apart on a 429 with an empty body and then died with a bogus
            # "Requested user could not be found" — for accounts that are
            # perfectly alive.
            #
            # PolarisProfilePageContentQuery is keyed by the numeric id: the
            # username it is normally called with is only the page the lsd /
            # fb_dtsg / doc_id are scraped from, and the site root serves those
            # just as well. So a uid on its own is enough, which is exactly
            # what this branch has.
            user = None
            for source, fetch in (
                (_PROFILE_OPNAME, lambda: self.user_by_graphql("", uid)),
                (f"id:{uid}", lambda: self.user_by_id(uid)),
            ):
                try:
                    user = fetch()
                except Exception as exc:
                    self.extractor.log.debug(
                        "Could not resolve id:%s via %s: %s: %s",
                        uid, source, exc.__class__.__name__, exc)
                else:
                    break
            if user is None:
                raise self.exc.NotFoundError("user")
            self.extractor._user = user
            return user

        user = self.user_by_screen_name(screen_name)
        if check_private and user.get("is_private") and (
                not user.get("followed_by_viewer", True) or
                not user.get("friendship_status", {}).get("following", True)):
            name = user["username"]
            s = "" if name.endswith("s") else "s"
            self.extractor.log.warning("%s'%s posts are private", name, s)

        # --- immich patch: upgrade a thin user block to the real profile ---
        # Since 1.32.7 the default uid strategy is `topsearch`, and its user object carries
        # no biography and no counts (all the `edge_*` keys are absent, so _assign_user
        # zeroes count_media/count_followed/...). `web_profile_info` would have them but
        # 429s on the first call AND on all 5 retries, a minute apart, so it is unusable as
        # a first strategy. The app endpoint used by user_by_id (/v1/users/<id>/info/) is
        # NOT throttled and returns the full 220-key profile — and topsearch has just handed
        # us the numeric id. So spend one extra (disk-cached) request and stamp the real
        # profile into every post's `user` block, exactly as the `id:<uid>` branch above
        # does. Without this a first-time download of a handle can never carry a bio: the
        # id:-form rewrite on our side needs a uid that only a previous download provides.
        uid = user["id"]
        if self.extractor.config("metadata") and "biography" not in user:
            # GraphQL FIRST. The REST profile endpoint has been throttled since
            # late September 2026 (see _PROFILE_DOC_ID), so asking it first
            # spends the whole retry budget — five attempts a minute apart — on
            # a refusal before anything else is tried. It stays as the fallback
            # because it is still the richer answer on the occasions it lands.
            upgraded = None
            for source, fetch in (
                (_PROFILE_OPNAME, lambda: self.user_by_graphql(
                    screen_name, uid)),
                (f"id:{uid}", lambda: self.user_by_id(uid)),
            ):
                try:
                    upgraded = fetch()
                except Exception as exc:
                    # The REASON, not just the fact. A 429, a redirect and a
                    # challenge page all used to arrive here as one
                    # indistinguishable line, because _user_by_id_impl converts
                    # every exception into NotFoundError.
                    self.extractor.log.debug(
                        "Could not upgrade user block for %s via %s: %s: %s",
                        screen_name, source, exc.__class__.__name__, exc)
                else:
                    break
            if upgraded is not None:
                # Upstream renamed user_id() -> user(): callers now want the
                # user OBJECT, not the uid (user_feed does user(h)["username"]).
                self.extractor._user = user = upgraded
                return user

        self.extractor._assign_user(user)
        return user

    def user_collection(self, collection_id):
        endpoint = f"/v1/feed/collection/{collection_id}/posts/"
        params = {"count": 50}
        return self._pagination(endpoint, params, media=True)

    def user_feed(self, handle):
        username = self.user(handle)["username"]

        variables = {
            "after" : None,
            "before": None,
            "data": {
                "count": 12,
                "include_reel_media_seen_timestamp": True,
                "include_relationship_info": True,
                "latest_besties_reel_media": True,
                "latest_reel_media": True,
            },
            "first": 12,
            "include_multi_captions": True,
            "last": None,
            "username": username,
            "__relay_internal__pv__"
            "PolarisMultiCaptionCarouselEnabledrelayprovider": True,
            "__relay_internal__pv__"
            "PolarisShortDramaEnabledrelayprovider": False,
            "__relay_internal__pv__"
            "PolarisReelsRecoDebugOverlayEnabledrelayprovider": False,
        }

        return self._pagination_graphql(
            "PolarisProfilePostsTabContentQuery_connection",
            "xdt_api__v1__feed__user_timeline_graphql_connection",
            "",
            "28975909992013618",
            variables)

    def user_reels(self, handle):
        user = self.user(handle)
        user_id = str(user["id"])

        variables = {
            "after": "",
            "data" : {
                "include_feed_video": True,
                "page_size": 12,
                "target_user_id": user_id,
            },
            "first": 12,
            "id": user_id,
            "__relay_internal__pv__"
            "PolarisShortDramaEnabledrelayprovider": False,
        }

        return self._pagination_graphql(
            "PolarisProfileReelsTabContentQuery_connection",
            "fetch__XDTUserDict",
            "reels",
            "28647575511547745",
            variables)

    def user_followers(self, user_id):
        endpoint = f"/v1/friendships/{user_id}/followers/"
        params = {"count": 12}
        return self._pagination_following(endpoint, params)

    def user_following(self, user_id):
        endpoint = f"/v1/friendships/{user_id}/following/"
        params = {"count": 12}
        return self._pagination_following(endpoint, params)

    def user_saved(self):
        endpoint = "/v1/feed/saved/posts/"
        params = {"count": 50}
        return self._pagination(endpoint, params, media=True)

    def user_tagged(self, handle):
        variables = {
            "after"  : None,
            "before" : None,
            "count"  : 12,
            "first"  : 12,
            "last"   : None,
            "user_id": str(self.user(handle)["id"]),
            "__relay_internal__pv__"
            "PolarisShortDramaEnabledrelayprovider": True,
        }

        return self._pagination_graphql(
            "PolarisProfileTaggedTabContentQuery_connection",
            "xdt_api__v1__usertags__user_id__feed_connection",
            "tagged",
            "28412176455057653",
            variables)

    def user_tagged_legacy(self, user_id):
        endpoint = f"/v1/usertags/{user_id}/feed/"
        params = {"count": 20}
        return self._pagination(endpoint, params)

    def _extract_fb_tokens(self, path):
        extr = self.extractor
        lsd = extr.config("lsd")
        dtsg = extr.config("fb-dtsg")
        if lsd and dtsg:
            extr.log.debug("Using 'config' GraphQL tokens")
            return lsd, dtsg

        extr.log.debug("Extracting GraphQL tokens")
        page = extr.cache(self._webpage, path)
        pos = page.find(' id="__eqmc"')
        eqmc = util.json_loads(
            page[page.find(">", pos)+1:page.find("</script>", pos)])
        if not lsd:
            lsd = (eqmc.get("l") or
                   text.extr(page, '"lsd":"', '"') or
                   text.extr(page, '"LSD",[],{"token":"', '"'))
        if not dtsg:
            dtsg = (eqmc.get("f") or
                    text.extr(page, '"dtsg":{"token":"', '"'))
        extr.log.debug("Found 'lsd=%s' & 'fb_dtsg=%s'", lsd, dtsg)
        return lsd, dtsg

    def _extract_docid(self, path, opname):
        extr = self.extractor
        if doc_id := extr.config("doc-id"):
            extr.log.debug("Using 'config' doc_id value")
            return doc_id

        extr.log.debug("Extracting '%s' doc_id value", opname)
        needle = opname + "_instagramRelayOperation"
        doc_id = ""
        for path in util.unique(text.extract_iter(
                extr.cache(self._webpage, path),
                'href="https://static.cdninstagram.com/rsrc.php/', '"')):
            if not path.endswith(".js"):
                continue
            url = "https://static.cdninstagram.com/rsrc.php/" + path
            script = extr.request(url, interval=False).text
            if (pos := script.find(needle)) < 0:
                continue
            if match := text.re(
                    r'exports\s*=\s*["\']?(\d{10,20})').search(
                    script, pos, pos+1000):
                doc_id = match[1]
                break
        extr.log.debug("Found 'doc_id=%s'", doc_id)
        return doc_id

    def _webpage(self, path):
        extr = self.extractor
        return extr.request(f"{extr.root}{path}/", interval=False).text

    def _call(self, endpoint, **kwargs):
        extr = self.extractor

        if endpoint[0] == "/":
            url = "https://www.instagram.com/api" + endpoint
        else:
            url = endpoint
        kwargs["headers"] = {
            "Accept"          : "*/*",
            "X-CSRFToken"     : extr.csrf_token,
            "X-IG-App-ID"     : "936619743392459",
            "X-ASBD-ID"       : "359341",
            "X-IG-WWW-Claim"  : extr.www_claim,
            "X-IG-Max-Touch-Points": "0",
            "X-Requested-With": "XMLHttpRequest",
        }
        return extr.request_json(url, **kwargs)

    def _pagination(self, endpoint, params=None, media=False):
        if params is None:
            params = {}
        extr = self.extractor
        params["max_id"] = extr._init_cursor()

        while True:
            data = self._call(endpoint, params=params)

            if media:
                for item in data["items"]:
                    yield item["media"]
            else:
                yield from data["items"]

            if not data.get("more_available"):
                return extr._update_cursor(None)
            params["max_id"] = extr._update_cursor(data["next_max_id"])

    def _pagination_post(self, endpoint, params):
        extr = self.extractor
        params["max_id"] = extr._init_cursor()

        while True:
            data = self._call(endpoint, method="POST", data=params)

            for item in data["items"]:
                yield item["media"]

            info = data["paging_info"]
            if not info.get("more_available"):
                return extr._update_cursor(None)
            params["max_id"] = extr._update_cursor(info["max_id"])

    def _pagination_sections(self, endpoint, params):
        extr = self.extractor
        params["max_id"] = extr._init_cursor()

        while True:
            info = self._call(endpoint, method="POST", data=params)

            yield from info["sections"]

            if not info.get("more_available"):
                return extr._update_cursor(None)
            params["page"] = info["next_page"]
            params["max_id"] = extr._update_cursor(info["next_max_id"])

    def _pagination_following(self, endpoint, params):
        extr = self.extractor
        params["max_id"] = text.parse_int(extr._init_cursor())

        while True:
            data = self._call(endpoint, params=params)

            yield from data["users"]

            next_max_id = data.get("next_max_id")
            if not next_max_id:
                return extr._update_cursor(None)
            params["max_id"] = extr._update_cursor(next_max_id)

    def user_by_graphql(self, username, user_id):
        """The profile /v1/users/<id>/info/ used to return, via the web query."""
        # `_key=1` — cache under the USER ID, args[1], not the default args[0].
        # The username is only the page the tokens are scraped from, and the
        # `id:<uid>` branch of user() passes "" for it, so keying on args[0]
        # would file every numeric-id lookup under one shared empty key and
        # hand the second account the first account's profile. The uid is the
        # identity anyway, so this also stops the same profile being cached
        # twice when it is reached once by handle and once by id.
        return self.extractor.cache(
            self._user_by_graphql_impl, username, user_id, _key=1,
            _exp=self._user_cache_exp, _mem=self._user_cache_mem)

    def _user_by_graphql_impl(self, username, user_id):
        variables = {"id": user_id, "enable_integrity_filters": False}
        variables.update(_PROFILE_PROVIDERS)
        # A PATH, not a username: upstream's _webpage does f"{root}{path}/",
        # so the leading slash is load-bearing (without it the host becomes
        # "www.instagram.comchanelb4byyy2.0_" and DNS fails). And an EMPTY
        # username must stay empty rather than becoming "/", which would ask
        # for "https://www.instagram.com//" — a page that carries no __eqmc
        # block and so no tokens. "" gives the site root, which does.
        path = "/" + username if username else ""
        data = self._call_graphql(
            path, _PROFILE_OPNAME, _PROFILE_FIELD, _PROFILE_DOC_ID,
            variables).get("data") or {}
        # The query ALIASES its root field to "user"; the raw field name is the
        # fallback in case a future revision drops the alias.
        user = data.get("user") or data.get(_PROFILE_FIELD)
        if not user or "biography" not in user:
            # A thin or empty answer is the failure this exists to avoid. Say so
            # rather than returning something the caller will cache and stamp
            # into every sidecar.
            raise self.exc.NotFoundError("user")
        return user

    def _call_graphql(self, path, opname, fieldname, doc_id, variables):
        """One GraphQL query, no cursor. Sibling of _pagination_graphql.

        Deliberately not folded into that method: it is the working path for
        every post, reel and highlight listing, and a profile lookup is not
        worth the risk of touching it.
        """
        extr = self.extractor
        url = extr.root + "/graphql/query"
        fb_lsd, fb_dtsg = self._extract_fb_tokens(path)

        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-FB-Friendly-Name": opname,
            "X-CSRFToken": extr.csrf_token,
            "X-IG-App-ID": "936619743392459",
            "X-IG-Max-Touch-Points": "0",
            "X-BLOKS-VERSION-ID": "62077fc559de123afe03ebeb18194a88"
                                  "ba5d4e6874d9a07873752f3792adb8a0",
            "X-Root-Field-Name": fieldname,
            "X-FB-LSD": fb_lsd,
            "X-ASBD-ID": "359341",
            "Origin": extr.root,
            "Alt-Used": extr.root[8:],
            "Connection": "keep-alive",
            "Referer": f"{extr.root}{path}/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
        }
        body = {
            "av"    : "17841415137994167",
            "__d"   : "www",
            "__user": "0",
            "__a"   : "1",
            "__req" : "0",
            "__hs"  : "20706.HYP%3Ainstagram_web_pkg.2.1...0",
            "dpr"   : "1",
            "__ccg" : "EXCELLENT",
            "__rev" : "1047183312",
            "__hsi" : "7683797502103314933",
            "__comet_req": "7",
            "fb_dtsg"  : fb_dtsg,
            "jazoest"  : "26461",
            "lsd"      : fb_lsd,
            "__crn"    : "comet.igweb.PolarisProfilePostsTabRoute",
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": opname,
            "server_timestamps": "true",
            "variables": util.json_dumps(variables),
            "doc_id"   : extr.cache(self._extract_docid, path, opname,
                                    _key=1, _exp=86400, _mem=False) or doc_id,
        }

        response = extr.request(url, method="POST", headers=headers, data=body)
        return util.json_loads(response.text)

    def _pagination_graphql(self, opname, fieldname, path, doc_id, variables):
        extr = self.extractor
        root = extr.root
        url = root + "/graphql/query"

        if extr._user:
            name = extr._user["username"]
            path = f"/{name}/{path}" if path else ("/" + name)

        fb_lsd, fb_dtsg = self._extract_fb_tokens(path)
        doc_id = extr.cache(self._extract_docid, path, opname,
                            _key=1, _exp=86400, _mem=False) or doc_id

        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-FB-Friendly-Name": opname,
            "X-CSRFToken": None,
            "X-IG-App-ID": "936619743392459",
            "X-IG-Max-Touch-Points": "0",
            "X-BLOKS-VERSION-ID": "62077fc559de123afe03ebeb18194a88"
                                  "ba5d4e6874d9a07873752f3792adb8a0",
            "X-Root-Field-Name": fieldname,
            "X-FB-LSD": fb_lsd,
            "X-ASBD-ID": "359341",
            "Origin" : root,
            "Alt-Used": root[8:],
            "Connection": "keep-alive",
            "Referer": f"{root}{path}/",
            "Cookie": None,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
        }
        body = {
            "av"    : "17841415137994167",
            "__d"   : "www",
            "__user": "0",
            "__a"   : "1",
            "__req" : "0",
            "__hs"  : "20706.HYP%3Ainstagram_web_pkg.2.1...0",
            "dpr"   : "1",
            "__ccg" : "EXCELLENT",
            "__rev" : "1047183312",
            #  "__s"   : "...",
            "__hsi" : "7683797502103314933",
            #  "__dyn" : "...",
            #  "__csr" : "...",
            #  "__hsdp": "...",
            #  "__hblp": "...",
            #  "__sjsp": "...",
            "__comet_req": "7",
            "fb_dtsg"  : fb_dtsg,
            "jazoest"  : "26461",
            "lsd"      : fb_lsd,
            #  "__spin_r" : "1047183312",
            #  "__spin_b" : "trunk",
            #  "__spin_t" : "1789023518",
            "__crn"    : "comet.igweb.PolarisProfilePostsTabRoute",
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": opname,
            "server_timestamps": "true",
            "variables": None,
            "doc_id"   : doc_id,
        }

        variables["after"] = extr._init_cursor()
        while True:
            headers["X-CSRFToken"] = extr.csrf_token
            body["variables"] = util.json_dumps(variables)
            response = extr.request(
                url, method="POST", headers=headers, data=body)

            try:
                data = util.json_loads(response.text)["data"][fieldname]
            except (ValueError, KeyError):
                break

            if "edges" not in data:
                for value in data.values():
                    if isinstance(value, dict) and "edges" in value:
                        data = value
                        break
                else:
                    break

            for edge in data["edges"]:
                yield edge["node"]

            info = data.get("page_info")
            if not info or not info.get("has_next_page"):
                break
            variables["after"] = extr._update_cursor(info["end_cursor"])


def id_from_shortcode(shortcode):
    return util.bdecode(shortcode, _ALPHABET)


def shortcode_from_id(post_id):
    return util.bencode(int(post_id), _ALPHABET)


# Pulls the CURRENT doc_id out of the Relay preloader manifest embedded in a
# post's HTML. Keyed on the query NAME, not position: the manifest lists a dozen
# queries (feed prefetch, stories tray, comments, related grid) and their order
# is not stable.
_POST_DOC_ID_RE = text.re(
    r'"queryID":"(\d+)"[^{}]*"variables":\{"shortcode":'
    r'[^{}]*\},"queryName":"PolarisPostRootQuery"').search

# Last-resort pin for PolarisPostRootQuery, used only if discovery fails.
# Instagram rotates these, so it WILL go stale — that is expected and no longer
# fatal, because _discover_post_doc_id reads the live one from the post page.
#
# The previously pinned id (8845758582119845, believed to be
# PolarisPostActionLoadPostQuery) had rotated and returned
# {"errors":[{"message":"execution error"}]} — HTTP 200, ~90 bytes — which is
# what silently broke single-post downloads once REST started answering 302.
_POST_DOC_ID = "27830990013244856"

# Signature of the REST media/info gate: the endpoint 302s single-post requests
# to the logged-out home page even with valid cookies (see Extractor.request,
# which turns that redirect into an AbortExtraction). Matched on the message
# rather than the exception class so an AbortExtraction raised for any other
# reason does not latch the gate.
_REST_GATED_RE = text.re(r"redirect to (?:home|login) page").search

# How long InstagramRestAPI.media() keeps skipping REST after seeing the gate.
# A day: long enough that a queue of hundreds of posts probes it once instead of
# once per post, short enough that an un-gating is picked up without a manual
# cache flush. Override per-run with '-o rest-gate-ttl=<seconds>' (0 disables
# expiry entirely, so prefer a small number over 0 when testing).
_REST_GATE_TTL = 86400

# --- immich patch: the query that replaced /v1/users/<id>/info/ ---
#
# Instagram began throttling the REST profile endpoint between 19 and 23 Sep
# 2026. Measured: 11 of 11 calls succeeded up to the 19th, then 27 x 429 against
# 12 x 200 — while its SIBLING /v1/media/<id>/info/ answered 11 of 11 on the
# same session, IP and minute, and two different accounts behaved identically.
# So it is the endpoint that is throttled, not the account, session, IP or UA.
#
# The web app does not use it either. A profile page loads
# PolarisProfilePageContentQuery, whose root field fetch__XDTUserDict returns a
# 65-key XDTUserDict carrying biography, biography_with_entities, bio_links,
# follower_count, following_count, media_count, category and pronouns. Fewer
# keys than the 220-key REST profile, but the count fields keep their REST
# names, so json-sidecar.service reads this shape unchanged.
#
# Verified against a live session: HTTP 200 with a populated biography in the
# same minute that /v1/users/<id>/info/ returned 429 for the same uid.
#
# The id is discovered per run by _extract_docid — the same mechanism the post
# query uses — so this pin is only the fallback for when discovery fails.
_PROFILE_OPNAME = "PolarisProfilePageContentQuery"
_PROFILE_FIELD = "fetch__XDTUserDict"
_PROFILE_DOC_ID = "28036671149327607"

# Relay provider flags the query declares. They must be present or the request
# is rejected; their VALUES only select experiments we do not want, so all off.
_PROFILE_PROVIDERS = {
    "__relay_internal__pv__PolarisCannesGuardianExperienceEnabledrelayprovider": False,
    "__relay_internal__pv__PolarisCASB976ProfileEnabledrelayprovider": False,
    "__relay_internal__pv__PolarisRepostsConsumptionEnabledrelayprovider": False,
    "__relay_internal__pv__PolarisShortDramaEnabledrelayprovider": False,
    "__relay_internal__pv__PolarisWebSchoolsEnabledrelayprovider": False,
}


def _rest_media_ungated():
    """Cache seed for the REST media/info gate: not known to be gated.

    Only exists to give Extractor.cache()/cache_update() a stable key
    (``gallery_dl.extractor.instagram._rest_media_ungated``); the value is
    written by InstagramRestAPI._mark_rest_media_gated().
    """
    return False


def _strip_xdt_typenames(media):
    # The doc_id GraphQL response prefixes media typenames with 'XDT'
    # (XDTGraphImage / XDTGraphSidecar / XDTGraphVideo). The existing GraphQL
    # post parser keys off the legacy names (GraphSidecar, etc.), so normalize
    # the top-level node and any sidecar children back to those.
    typename = media.get("__typename")
    if typename and typename.startswith("XDT"):
        media["__typename"] = typename[3:]
    children = media.get("edge_sidecar_to_children")
    if children:
        for edge in children.get("edges", ()):
            node = edge.get("node") or {}
            child_typename = node.get("__typename")
            if child_typename and child_typename.startswith("XDT"):
                node["__typename"] = child_typename[3:]
    return media


_ALPHABET = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
             "abcdefghijklmnopqrstuvwxyz"
             "0123456789-_")
