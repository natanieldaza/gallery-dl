# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.facebook.com/"""

from .common import Extractor, Message, Dispatch
from .. import text, util

BASE_PATTERN = r"(?:https?://)?(?:[\w-]+\.)?facebook\.com"
USER_PATTERN = (BASE_PATTERN +
                r"/(?!media/|photo/|photo.php|watch/|permalink.php)"
                r"(?:profile\.php\?id=|people/[^/?#]+/)?([^/?&#]+)")


class FacebookExtractor(Extractor):
    """Base class for Facebook extractors"""
    category = "facebook"
    root = "https://www.facebook.com"
    directory_fmt = ("{category}", "{username}",
                     "{title[:220]}{set_id:? (/)/}")
    filename_fmt = "{id}.{extension}"
    archive_fmt = "{id}.{extension}"

    def _init(self):
        headers = self.session.headers
        headers["Accept"] = (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8"
        )
        headers["Sec-Fetch-Dest"] = "empty"
        headers["Sec-Fetch-Mode"] = "navigate"
        headers["Sec-Fetch-Site"] = "same-origin"

        self.fallback_retries = self.config("fallback-retries", 2)
        if self.fallback_retries < 0:
            self.fallback_retries = float("inf")
        self.videos = self.config("videos", True)
        self.author_followups = self.config("author-followups", False)
        self._detect_jump = True

    def decode_all(self, txt):
        return text.unescape(
            txt.encode().decode("unicode_escape")
            .encode("utf_16", "surrogatepass").decode("utf_16")
        ).replace("\\/", "/")

    def parse_set_page(self, set_page):
        directory = {
            "set_id": text.extr(
                set_page, '"mediaSetToken":"', '"'
            ) or text.extr(
                set_page, '"mediasetToken":"', '"'
            ),
            "username": self.decode_all(
                text.extr(
                    set_page, '"user":{"__isProfile":"User","name":"', '","'
                ) or text.extr(
                    set_page, '"actors":[{"__typename":"User","name":"', '","'
                )
            ),
            "user_id": text.extr(
                set_page, '"owner":{"__typename":"User","id":"', '"'
            ),
            "user_pfbid": "",
            "title": text.extr(set_page, '"title":{"', '}'),
            "first_photo_id": text.extr(
                set_page,
                '{"__typename":"Photo","__isMedia":"Photo","',
                '","creation_story"'
            ).rsplit('"id":"', 1)[-1] or
            text.extr(
                set_page, '{"__typename":"Photo","id":"', '"'
            )
        }

        if t := directory["title"]:
            try:
                directory["title"] = util.json_loads(f'{{"{t}}}').get("text")
            except Exception as exc:
                self.log.debug("Failed to extract 'title' metadata")
                self.log.traceback(exc)
        if directory["user_id"].startswith("pfbid"):
            directory["user_pfbid"] = directory["user_id"]
            directory["user_id"] = (
                text.extr(
                    set_page, '"actors":[{"__typename":"User","id":"', '"') or
                text.extr(
                    set_page, '"userID":"', '"') or
                directory["set_id"].split(".")[1])

        return directory

    def parse_photo_page(self, photo_page):
        photo = {
            "id": text.extr(
                photo_page, '"__isNode":"Photo","id":"', '"'
            ),
            "set_id": text.extr(
                photo_page,
                '"url":"https:\\/\\/www.facebook.com\\/photo\\/?fbid=',
                '"'
            ).rsplit("&set=", 1)[-1],
            "username": self.decode_all(text.extr(
                photo_page, '"owner":{"__typename":"User","name":"', '"'
            )),
            "user_id": text.extr(
                photo_page, '"owner":{"__typename":"User","id":"', '"'
            ),
            "user_pfbid": "",
            "caption": self.decode_all(text.extr(
                photo_page,
                '"message":{"delight_ranges"',
                '"},"message_preferred_body"'
            ).rsplit('],"text":"', 1)[-1]),
            "date": self.parse_timestamp(
                text.extr(photo_page, '\\"publish_time\\":', ',') or
                text.extr(photo_page, '"created_time":', ',')
            ),
            "url": self.decode_all(text.extr(
                photo_page, ',"image":{"uri":"', '","'
            )),
            "next_photo_id": text.extr(
                photo_page,
                '"nextMediaAfterNodeId":{"__typename":"Photo","id":"',
                '"'
            ) or text.extr(
                photo_page,
                '"nextMedia":{"edges":[{"node":{"__typename":"Photo","id":"',
                '"'
            ),
        }

        if photo["user_id"].startswith("pfbid"):
            photo["user_pfbid"] = photo["user_id"]
            photo["user_id"] = text.extr(
                photo_page, r'\"content_owner_id_new\":\"', r'\"')

        if not photo["next_photo_id"]:
            photo["_next_video"] = True
            photo["next_photo_id"] = text.extr(
                photo_page,
                '"nextMedia":{"edges":[{"node":{"__typename":"Video","id":"',
                '"')

        text.nameext_from_url(photo["url"], photo)

        photo["followups_ids"] = []
        for comment_raw in text.extract_iter(
            photo_page, '{"node":{"id"', '"cursor":null}'
        ):
            if ('"is_author_original_poster":true' in comment_raw and
                    '{"__typename":"Photo","id":"' in comment_raw):
                photo["followups_ids"].append(text.extr(
                    comment_raw,
                    '{"__typename":"Photo","id":"',
                    '"'
                ))

        return photo

    def parse_post_page(self, post_page):
        first_photo_url = text.extr(
            text.extr(
                post_page, '"__isMedia":"Photo"', '"target_group"'
            ), '"url":"', ','
        ).replace("\\/", "/").rstrip('"}')

        if post_page.count('"__isMedia":"Photo"') > 2:
            post = {
                "set_id": text.extr(post_page, '{"mediaset_token":"', '"') or
                text.extr(first_photo_url, 'set=', '"').rsplit("&", 1)[0]
            }
        else:
            post = {"set_id": None}

        txt = text.extr(post_page, ',"text":"', '"},')
        post["post_text"] = util.json_loads(f'"{txt}"')
        post["post_photo"] = first_photo_url
        return post

    def parse_video_page(self, video_page):
        video = {
            "id": text.extr(
                video_page, '\\"video_id\\":\\"', '\\"'
            ),
            "username": self.decode_all(text.extr(
                video_page, '"actors":[{"__typename":"User","name":"', '","'
            )),
            "user_id": text.extr(
                video_page, '"owner":{"__typename":"User","id":"', '"'
            ),
            "date": self.parse_timestamp(text.extr(
                video_page, '\\"publish_time\\":', ','
            )),
            "type": "video"
        }

        if not video["username"]:
            video["username"] = self.decode_all(text.extr(
                video_page,
                '"__typename":"User","id":"' + video["user_id"] + '","name":"',
                '","'
            ))

        first_video_raw = text.extr(
            video_page, '"permalink_url"', '\\/Period>\\u003C\\/MPD>'
        )

        audio = {
            **video,
            "url": self.decode_all(text.extr(
                text.extr(
                    first_video_raw,
                    "AudioChannelConfiguration",
                    "BaseURL>\\u003C"
                ),
                "BaseURL>", "\\u003C\\/"
            )),
            "type": "audio"
        }

        video["urls"] = {}

        for raw_url in text.extract_iter(
            first_video_raw, 'FBQualityLabel=\\"', '\\u003C\\/BaseURL>'
        ):
            resolution = raw_url.split('\\"', 1)[0]
            video["urls"][resolution] = self.decode_all(
                raw_url.split('BaseURL>', 1)[1]
            )

        if video["urls"]:
            video["url"] = max(
                video["urls"].items(),
                key=lambda x: text.parse_int(x[0][:-1])
            )[1]

            text.nameext_from_url(video["url"], video)
            audio["filename"] = video["filename"]
            audio["extension"] = "m4a"
        elif url := text.extr(video_page, '"browser_native_hd_url":"', '"'):
            video["url"] = util.json_loads(f'"{url}"')
            text.nameext_from_url(video["url"], video)

        return video, audio

    def photo_page_request_wrapper(self, url, **kwargs):
        LEFT_OFF_TXT = "" if url.endswith("&set=") else (
            "\nYou can use this URL to continue from "
            "where you left off (added \"&setextract\"): "
            "\n" + url + "&setextract"
        )

        res = self.request(url, **kwargs)

        if res.url.startswith(self.root + "/login"):
            raise self.exc.AuthRequired(
                message=("You must be logged in to continue viewing images." +
                         LEFT_OFF_TXT))

        if b'{"__dr":"CometErrorRoot.react"}' in res.content:
            raise self.exc.AbortExtraction(
                "You've been temporarily blocked from viewing images.\n"
                "Please try using a different account, "
                "using a VPN or waiting before you retry." + LEFT_OFF_TXT)

        return res

    def extract_set(self, set_data):
        set_id = set_data["set_id"]
        all_photo_ids = [set_data["first_photo_id"]]
        videos = set()

        retries = 0
        i = 0

        while i < len(all_photo_ids):
            photo_id = all_photo_ids[i]
            if photo_id in videos:
                photo_url = (f"{self.root}/{set_data['user_id']}/videos/"
                             f"{set_id}/{photo_id}")
            else:
                photo_url = f"{self.root}/photo/?fbid={photo_id}&set={set_id}"
            photo_page = self.photo_page_request_wrapper(photo_url).text

            photo = self.parse_photo_page(photo_page)
            photo["num"] = i + 1

            if self.author_followups:
                for followup_id in photo["followups_ids"]:
                    if followup_id not in all_photo_ids:
                        self.log.debug(
                            "Found a followup in comments: %s", followup_id
                        )
                        all_photo_ids.append(followup_id)

            if photo["url"]:
                retries = 0
                photo.update(set_data)
                yield Message.Directory, "", photo
                yield Message.Url, photo["url"], photo
            elif photo_id not in videos:
                if retries < self.fallback_retries and self._interval_429:
                    seconds = self._interval_429(retries + 1)
                    self.log.warning(
                        "Failed to find photo download URL for %s. "
                        "Retrying in %s seconds.", photo_url, seconds,
                    )
                    self.wait(seconds=seconds, reason="429 Too Many Requests")
                    retries += 1
                    continue
                else:
                    self.log.error(
                        "Failed to find photo download URL for " + photo_url +
                        ". Skipping."
                    )
                    retries = 0

            if not photo["next_photo_id"]:
                self.log.debug(
                    "Can't find next image in the set. "
                    "Extraction is over."
                )
            elif photo["next_photo_id"] in all_photo_ids:
                if photo["next_photo_id"] != photo["id"]:
                    self.log.debug(
                        "Detected a loop in the set, it's likely finished. "
                        "Extraction is over."
                    )
            elif self._detect_jump and not set_id.startswith('pcb.') and \
                    photo_id not in videos and photo["id"] and \
                    (int(photo["next_photo_id"]) >> 1) > int(photo["id"]) :
                self.log.info(
                    "Detected possible jump to the beginning of the set. "
                    "(%s -> %s)", photo["id"], photo["next_photo_id"])
                if self.config("loop", True):
                    all_photo_ids.append(photo["next_photo_id"])
            else:
                all_photo_ids.append(photo["next_photo_id"])
                if photo.get("_next_video"):
                    videos.add(photo["next_photo_id"])

            i += 1

    def _extract_profile(self, profile, set_id=False):
        if set_id:
            url = f"{self.root}/{profile}/photos_by"
        else:
            url = f"{self.root}/{profile}"
        return self._extract_profile_page(url)

    def _extract_profile_page(self, url):
        for _ in range(self.fallback_retries + 1):
            page = self.request(url).text

            if page.find('>Page Not Found</title>', 0, 3000) > 0:
                break
            if ('"props":{"title":"This content isn\'t available right now"' in
                    page):
                raise self.exc.AuthRequired(
                    "authenticated cookies", "profile",
                    "This content isn't available right now")

            set_id = self._extract_profile_set_id(page)
            user = self._extract_profile_user(page)
            if set_id or user:
                user["set_id"] = set_id
                return user

            self.log.debug("Got empty profile photos page, retrying...")
        return {}

    def _extract_profile_set_id(self, profile_photos_page):
        set_ids_raw = text.extr(
            profile_photos_page, '"pageItems"', '"page_info"'
        )

        set_id = text.extr(
            set_ids_raw, 'set=', '"'
        ).rsplit("&", 1)[0] or text.extr(
            set_ids_raw, '\\/photos\\/', '\\/'
        )

        return set_id

    def _extract_profile_user(self, page):
        data = text.extr(page, '","user":{"', '},"viewer":{')

        user = None
        try:
            user = util.json_loads(f'{{"{data}}}')
            if user["id"].startswith("pfbid"):
                user["user_pfbid"] = user["id"]
                user["id"] = text.extr(page, '"userID":"', '"')
            user["username"] = (text.extr(page, '"userVanity":"', '"') or
                                text.extr(page, '"vanity":"', '"'))
            user["profile_tabs"] = [
                edge["node"]
                for edge in (user["profile_tabs"]["profile_user"]
                             ["timeline_nav_app_sections"]["edges"])
            ]

            if bio := text.extr(page, '"best_description":{"text":"', '"'):
                user["biography"] = self.decode_all(bio)
            elif (pos := page.find(
                    '"__module_operation_ProfileCometTileView_profileT')) >= 0:
                user["biography"] = self.decode_all(text.rextr(
                    page, '"text":"', '"', pos))
            else:
                user["biography"] = text.unescape(text.remove_html(text.extr(
                    page, "</span></span></h2>", "<ul>")))
        except Exception:
            if user is None:
                self.log.debug("Failed to extract user data: %s", data)
                user = {}
        return user


class FacebookPhotoExtractor(FacebookExtractor):
    """Base class for Facebook Photo extractors"""
    subcategory = "photo"
    pattern = (BASE_PATTERN +
               r"/(?:[^/?#]+/photos/[^/?#]+/|photo(?:.php)?/?\?"
               r"(?:[^&#]+&)*fbid=)([^/?&#]+)[^/?#]*(?<!&setextract)$")
    example = "https://www.facebook.com/photo/?fbid=PHOTO_ID"

    def items(self):
        photo_id = self.groups[0]
        photo_url = f"{self.root}/photo/?fbid={photo_id}&set="
        photo_page = self.photo_page_request_wrapper(photo_url).text

        i = 1
        photo = self.parse_photo_page(photo_page)
        photo["num"] = i

        set_url = f"{self.root}/media/set/?set={photo['set_id']}"
        set_page = self.request(set_url).text

        directory = self.parse_set_page(set_page)

        for key in ("set_id", "title", "user_id", "user_pfbid", "username"):
            if not directory.get(key):
                directory[key] = photo.get(key)
            elif not photo.get(key):
                photo[key] = directory.get(key)

        yield Message.Directory, "", directory
        yield Message.Url, photo["url"], photo

        if self.author_followups:
            for comment_photo_id in photo["followups_ids"]:
                comment_photo = self.parse_photo_page(
                    self.photo_page_request_wrapper(
                        f"{self.root}/photo/?fbid={comment_photo_id}&set="
                    ).text
                )
                i += 1
                comment_photo["num"] = i
                yield Message.Url, comment_photo["url"], comment_photo


class FacebookSetExtractor(FacebookExtractor):
    """Base class for Facebook Set extractors"""
    subcategory = "set"
    pattern = (
        BASE_PATTERN +
        r"/(?:(?:media/set|photo)/?\?(?:[^&#]+&)*set=([^&#]+)"
        r"[^/?#]*(?<!&setextract)$"  # set_id
        r"|([^/?#]+/posts/[^?#]+)"   # path aka '/USER/posts/SLUG/ID'
        r"|photo/?\?(?:[^&#]+&)*fbid=([^/?&#]+)&set=([^/?&#]+)&setextract"
        r"|(?:groups/)?(?:[^/?#]+/)?(?:permalink|posts)(?:\.php)?"
        r"(?:/(\d+)|\?\w+=([^/?#]+))"
        r"|events/[^/?#]+/\??post_id=(\d+))"
    )
    example = "https://www.facebook.com/media/set/?set=SET_ID"

    def items(self):
        set_id, path, first_pid, set_id2, pcb1, pcb2, pcb3 = self.groups
        if not set_id:
            set_id = set_id2

        post = None
        if path:
            post_url = f"{self.root}/{path}"
            post_page = self.request(post_url).text
            post = self.parse_post_page(post_page)

            set_id = post["set_id"]
            if not set_id:
                self.kwdict.update(post)
                params = text.parse_query(post["post_photo"].partition("?")[2])
                self.groups = (params["fbid"],)
                return FacebookPhotoExtractor.items(self)
            self._detect_jump = False
        elif not set_id:
            set_id = "pcb." + (pcb1 or pcb2 or pcb3)

        set_url = f"{self.root}/media/set/?set={set_id}"
        set_page = self.request(set_url).text
        set_data = self.parse_set_page(set_page)
        if first_pid:
            set_data["first_photo_id"] = first_pid
        if post:
            set_data.update(post)

        return self.extract_set(set_data)


class FacebookVideoExtractor(FacebookExtractor):
    """Base class for Facebook Video extractors"""
    subcategory = "video"
    directory_fmt = ("{category}", "{username}", "{subcategory}")
    pattern = BASE_PATTERN + r"/([^/?#]+/videos/|watch/?\?v=)([^/?&#]+)"
    example = "https://www.facebook.com/watch/?v=VIDEO_ID"

    def items(self):
        path, video_id = self.groups
        video_url = f"{self.root}/{path}{video_id}"
        video_page = self.request(video_url).text

        video, audio = self.parse_video_page(video_page)

        if "url" not in video:
            return

        yield Message.Directory, "", video

        if self.videos == "ytdl":
            yield Message.Url, "ytdl:" + video_url, video
        elif self.videos:
            yield Message.Url, video["url"], video
            if audio["url"]:
                yield Message.Url, audio["url"], audio


class FacebookReelExtractor(FacebookExtractor):
    """Extractor for Facebook Reels"""
    subcategory = "reel"
    directory_fmt = ("{category}", "{username}", "{subcategory}")
    pattern = BASE_PATTERN + r"/reel/([^/?&#]+)"
    example = "https://www.facebook.com/reel/1508490703517921"

    def items(self):
        reel_id = self.groups[0]
        # Try to convert reel URL to video URL format
        video_url = self.root + "/watch/?v=" + reel_id
        
        try:
            video_page = self.request(video_url).text
            video, audio = self.parse_video_page(video_page)

            if "url" not in video:
                # If video format doesn't work, try reel-specific parsing
                reel_url = self.root + "/reel/" + reel_id
                reel_page = self.request(reel_url).text
                video, audio = self.parse_reel_page(reel_page, reel_id)

            if "url" not in video:
                return

            yield Message.Directory, video

            if self.videos == "ytdl":
                yield Message.Url, "ytdl:" + self.root + "/reel/" + reel_id, video
            elif self.videos:
                yield Message.Url, video["url"], video
                if audio and audio.get("url"):
                    yield Message.Url, audio["url"], audio
                    
        except Exception as e:
            self.log.warning("Failed to extract reel %s: %s", reel_id, e)
            return

    def parse_reel_page(self, reel_page, reel_id):
        """Parse Facebook reel page to extract video information"""
        video = {
            "id": reel_id,
            "username": self.decode_all(text.extr(
                reel_page, '"actors":[{"__typename":"User","name":"', '","'
            )) or self.decode_all(text.extr(
                reel_page, '"owner":{"__typename":"User","name":"', '"'
            )),
            "user_id": text.extr(
                reel_page, '"owner":{"__typename":"User","id":"', '"'
            ),
            "date": text.parse_timestamp(text.extr(
                reel_page, '"publish_time":', ','
            ) or text.extr(
                reel_page, '"created_time":', ','
            )),
            "type": "reel"
        }

        # Try to extract video URL from reel page
        video_url = None
        
        # Look for video URLs in various formats found in reels
        for pattern in [
            r'"playable_url":"([^"]+)"',
            r'"src":"([^"]+\.mp4[^"]*)"',
            r'"video_url":"([^"]+)"',
            r'"url":"([^"]+\.mp4[^"]*)"'
        ]:
            import re
            match = re.search(pattern, reel_page)
            if match:
                video_url = self.decode_all(match.group(1))
                break

        if video_url:
            video["url"] = video_url
            text.nameext_from_url(video["url"], video)
        
        # Basic audio extraction (may not always be available for reels)
        audio = {
            **video,
            "type": "audio",
            "extension": "m4a"
        }
        
        return video, audio


class FacebookInfoExtractor(FacebookExtractor):
    """Extractor for Facebook Profile data"""
    subcategory = "info"
    directory_fmt = ("{category}", "{username}")
    pattern = USER_PATTERN + r"/info"
    example = "https://www.facebook.com/USERNAME/info"

    def items(self):
        user = self.cache(self._extract_profile, self.groups[0])
        return iter(((Message.Directory, "", user.copy()),))


class FacebookAlbumsExtractor(FacebookExtractor):
    """Extractor for Facebook Profile albums"""
    subcategory = "albums"
    pattern = USER_PATTERN + r"/photos_albums(?:/([^/?#]+))?"
    example = "https://www.facebook.com/USERNAME/photos_albums"

    def items(self):
        profile, name = self.groups
        url = f"{self.root}/{profile}/photos_albums"
        page = self.request(url).text

        pos = page.find(
            '"TimelineAppCollectionAlbumsRenderer","collection":{"id":"')
        if pos < 0:
            return
        if name is not None:
            name = name.lower()

        items = text.extract(page, '},"pageItems":', '}}},', pos)[0]
        edges = util.json_loads(items + "}}")["edges"]

        # TODO: use /graphql API endpoint
        for edge in edges:
            node = edge["node"]
            album = node["node"]
            album["title"] = title = node["title"]["text"]
            if name is not None and name != title.lower():
                continue
            album["_extractor"] = FacebookSetExtractor
            album["thumbnail"] = (img := node["image"]) and img["uri"]
            yield Message.Queue, album["url"], album


class FacebookPhotosExtractor(FacebookExtractor):
    """Extractor for Facebook Profile Photos"""
    subcategory = "photos"
    pattern = USER_PATTERN + r"/photos(?:_by)?"
    example = "https://www.facebook.com/USERNAME/photos"

    def items(self):
        profile = self.cache(self._extract_profile, self.groups[0], True)
        set_id = profile["set_id"]
        if not set_id:
            return iter(())

        set_url = f"{self.root}/media/set/?set={set_id}"
        set_page = self.request(set_url).text
        set_data = self.parse_set_page(set_page)
        # Prefer the profile's vanity handle (e.g. "gladys.taquitos") over the set
        # page's display name ("Gladys Taquitos") so files land in a handle-named
        # folder, matching immich's social_media handle / folder lookup.
        vanity = profile.get("username")
        if vanity:
            set_data["username"] = vanity
        return self.extract_set(set_data)


class FacebookAvatarExtractor(FacebookExtractor):
    """Extractor for Facebook Profile Avatars"""
    subcategory = "avatar"
    pattern = USER_PATTERN + r"/avatar"
    example = "https://www.facebook.com/USERNAME/avatar"

    def items(self):
        user = self.cache(self._extract_profile, self.groups[0])

        if avatar_page := user.get("profilePhoto"):
            avatar_page_url = avatar_page["url"]
            avatar_page = self.photo_page_request_wrapper(avatar_page_url).text

            avatar = self.parse_photo_page(avatar_page)
            avatar["count"] = avatar["num"] = 1
            avatar["type"] = "avatar"

            set_url = f"{self.root}/media/set/?set={avatar['set_id']}"
            set_page = self.request(set_url).text
            directory = self.parse_set_page(set_page)
        else:
            for key in ("profilePicLarge",
                        "profilePicMedium",
                        "profilePicSmall"):
                if url := user.get(key):
                    url = url["uri"]
                    break
            else:
                return

            directory = {
                "set_id"    : "",
                "username"  : user.get("username"),
                "user_id"   : user.get("id"),
                "user_pfbid": user.get("user_pfbid"),
                "title"     : "Profile pictures",
            }
            avatar = text.nameext_from_url(url, {
                **directory,
                "id"   : (a := user.get("user_avatar")) and a.get("id"),
                "url"  : url,
                "count": 1,
                "type" : "avatar",
            })

        yield Message.Directory, "", directory
        yield Message.Url, avatar["url"], avatar


class FacebookUserExtractor(Dispatch, FacebookExtractor):
    """Extractor for Facebook Profiles"""
    pattern = USER_PATTERN + r"/?(?:$|\?|#)"
    example = "https://www.facebook.com/USERNAME"

    def items(self):
        base = f"{self.root}/{self.groups[0]}/"
        return self._dispatch_extractors((
            (FacebookInfoExtractor  , base + "info"),
            (FacebookAvatarExtractor, base + "avatar"),
            (FacebookPhotosExtractor, base + "photos"),
            (FacebookAlbumsExtractor, base + "photos_albums"),
        ), ("photos",))
