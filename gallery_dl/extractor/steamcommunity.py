# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://steamcommunity.com/"""

from ..extractor.common import Extractor, Message
from .. import text, util, dt

BASE_PATTERN = r"(?:https?://)?(?:www\.)?steamcommunity.com"

SECTION_IDS = {
    "screenshots": 2,
    "artwork"    : 4,
    "images"     : 4,
}
SECTION_MAP = {
    "images"     : "artwork",
}


class SteamcommunityExtractor(Extractor):
    """Base class for steamcommunity extractors"""
    category = "steamcommunity"
    root = "https://steamcommunity.com"
    directory_fmt = ("{category}", "{game}", "{section!c}")
    filename_fmt = "{file_id}{title:? //}{description:? //X180/…/}.{extension}"
    archive_fmt = "{game_appid}_{file_id}_{ugc_id}"
    request_interval = (0.5, 1.5)

    def items_children(self, per_page=10):
        data = {"_extractor": SteamcommunitySharedfileExtractor}
        base = "https://steamcommunity.com/sharedfiles/filedetails/?id="
        find = SteamcommunitySharedfileExtractor.pattern.findall

        for page in self._pagination(per_page):
            post_ids = find(page)
            for pid in post_ids:
                yield Message.Queue, base + pid, data
            if len(post_ids) < per_page:
                break

    def items_wall(self, separator, per_page=10):
        for page in self._pagination(per_page):
            items = page.split(separator)
            del items[0]
            for item in items:
                data = self._extract_item(item)

                src = text.unescape(data.pop("url"))
                if (pos := src.find("?")) >= 0:
                    src = src[:pos]
                data["ugc_id"] = src[src.find("/ugc/")+5:-1]

                yield Message.Directory, "", data
                yield Message.Url, src, data
            if len(items) < per_page:
                break

    def _extract_game(self, appid):
        if appid == "767":
            return "Steam Artwork"
        url = f"{self.root}/app/{appid}/"
        page = self.request(url).text
        name = text.extr(page, 'class="apphub_AppName', '<')
        return text.unescape(name[name.rfind(">")+1:])


class SteamcommunitySharedfileExtractor(SteamcommunityExtractor):
    """Extractor for steamcommunity shared files"""
    subcategory = "sharedfile"
    pattern = BASE_PATTERN + r"/sharedfiles/filedetails/\?id=(\d+)"
    example = "https://steamcommunity.com/sharedfiles/filedetails/?id=12345"

    def items(self):
        fid = self.groups[0]
        url = f"{self.root}/sharedfiles/filedetails/?id={fid}"
        cookies = {"wants_mature_content_item_" + fid: "1"}
        page = self.request(url, cookies=cookies).text

        section = text.extr(
            page, 'class="apphub_sectionTab active "><span>', '<').lower()
        if not section and ">Steam Artwork<" in page:
            section = "artwork"
        if section not in SECTION_IDS:
            raise self.exc.AbortExtraction(f"Unsupported section '{section}'")

        meta = {
            "section": section,
            "file_id": fid,
            "url"    : url,
        }

        return self.items_image(page, meta)

    def items_image(self, page, meta):
        extr = text.extract_from(page)

        data = {
            **meta,
            "title"     : text.unescape(extr(
                'class="workshopItemTitle">', "<")),
            "game_appid": extr('class="screenshotAppName', "") or extr(
                "/app/", "/"),
            "game"      : text.unescape(extr(">", "<")),
            "creator_id": extr('class="friendBlockLinkOverlay" '
                               'href="https://steamcommunity.com/', '"',
                               ).rpartition("/")[2],
            "creator"   : text.unescape(extr(
                'class="friendBlockContent">', "<").strip()),
            "size"      : text.parse_bytes(extr(
                'class="detailsStatRight">', "<")[:-1]),
            "date"      : extr('class="detailsStatRight">', "<"),
            "width"     : text.parse_int(extr(
                'class="detailsStatRight">', " x ")),
            "height"    : text.parse_int(extr("", "<")),
            "views"     : text.parse_int(extr("<td>", "<").replace(",", "")),
            "likes"     : text.parse_int(text.remove_html(extr(
                "<tr>", "</")).replace(",", "")),
            "description": text.unescape(extr(
                'id="description"', "") or extr(">", "</textarea>")),
            "extension" : "jpg",  # Guess 'jpg' - Rely on extension fixing
        }

        if "," in (date := data["date"]):
            data["date"] = dt.parse(date, "%d %b, %Y @ %I:%M%p")
        else:
            data["date"] = (dt.parse(date, "%d %b @ %I:%M%p")
                            .replace(year=dt.datetime.now().year))

        img = text.extr(page, '<img id="ActualMedia"', '>')
        src = text.unescape(text.extr(img, 'src="', '"'))
        if (pos := src.find("?")) >= 0:
            src = src[:pos]
        data["ugc_id"] = src[src.find("/ugc/")+5:-1]

        yield Message.Directory, "", data
        yield Message.Url, src, data


class SteamcommunityGameExtractor(SteamcommunityExtractor):
    subcategory = "game"
    pattern = (BASE_PATTERN + r"/app/(\d+)/"
               r"((?:screenshot|image)s)(?:/?\?([^#]+))?")
    example = "https://steamcommunity.com/app/12345/screenshots/"

    def items(self):
        if self.config("metadata"):
            return self.items_children()
        return self.items_wall("<div data-panel=")

    def _extract_item(self, item):
        extr = text.extract_from(item)
        data = {
            "post_url"   : extr('data-modal-content-url="', '"'),
            "game_appid" : extr('data-appid="', '"'),
            "file_id"    : extr('data-publishedfileid="', '"'),
            "section"    : extr('class="apphub_CardContentType">', '<'),
            "url"        : extr('src="', '"'),
            "comments"   : extr('class="apphub_CardCommentCount">', '<'),
            "description": text.unescape(extr(
                'class="apphub_CardContentTitle ellipsis">', '<')).strip(),
            "creator_id" : extr('data-miniprofile="', '"'),
            "extension"  : "jpg",
        }

        creator = extr('class="apphub_CardContentAuthorName', "</")
        data["creator"] = text.unescape(creator[creator.rfind(">")+1:])
        data["game"] = self.cache(
            self._extract_game, data["game_appid"], _mem=False)

        return data

    def _pagination(self, per_page=10):
        appid, type, qs = self.groups
        url = f"{self.root}/app/{appid}/homecontent/"
        params = text.parse_query(qs)
        pnum = text.parse_int(params.get("p"), 1)

        params = {
            "userreviewsoffset"  : "0",
            "p"                  : None,
            "workshopitemspage"  : None,
            "readytouseitemspage": None,
            "mtxitemspage"       : None,
            "itemspage"          : None,
            "screenshotspage"    : None,
            "videospage"         : None,
            "artpage"            : None,
            "allguidepage"       : None,
            "webguidepage"       : None,
            "integratedguidepage": None,
            "discussionspage"    : None,
            "numperpage"         : str(per_page),
            "browsefilter"       : "trend",
            "appid"              : appid,
            "appHubSubSection"   : str(SECTION_IDS[type]),
            "l"                  : "english",
            "filterLanguage"     : "default",
            "searchText"         : "",
            "maxInappropriateScore": "100",
            "forceanon"          : "1",
            **params,
        }
        headers = {
            "Accept": "text/javascript, text/html, application/xml, "
                      "text/xml, */*",
            "X-Requested-With": "XMLHttpRequest",
            "X-Prototype-Version": "1.7",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

        while True:
            params["p"] = \
                params["workshopitemspage"] = \
                params["readytouseitemspage"] = \
                params["mtxitemspage"] = \
                params["itemspage"] = \
                params["screenshotspage"] = \
                params["videospage"] = \
                params["artpage"] = \
                params["allguidepage"] = \
                params["webguidepage"] = \
                params["integratedguidepage"] = \
                params["discussionspage"] = str(pnum)
            yield self.request(url, params=params, headers=headers).text
            pnum += 1


class SteamcommunityUserExtractor(SteamcommunityExtractor):
    subcategory = "user"
    directory_fmt = ("{category}", "{creator} ({creator_sid})", "{section!c}")
    pattern = (BASE_PATTERN + r"/(id/[^/?#]+|profiles/\d+)/"
               r"((?:screenshot|image)s)(?:/?\?([^#]+))?")
    example = "https://steamcommunity.com/id/USER/screenshots/"

    def items(self):
        if self.config("metadata"):
            return self.items_children()

        uid, type, qs = self.groups
        url = f"{self.root}/{uid}/"

        try:
            page = self.request(url).text
            data = text.extr(page, "g_rgProfileData = {", "};")
            profile = util.json_loads(f"{{{data}}}")
        except Exception as exc:
            self.log.warning("Failed to extract data of user '%s' (%s: %s)",
                             uid, exc.__class__.__name__, exc)
            profile = {}
        if type in SECTION_MAP:
            type = SECTION_MAP[type]

        kw = self.kwdict
        kw["section"] = type
        kw["creator"] = profile.get("personaname")
        kw["creator_id"] = uid[uid.find("/")+1:]
        kw["creator_sid"] = profile.get("steamid")

        return self.items_wall('href="https://steamcommunity.com', 12)

    def _extract_item(self, item):
        extr = text.extract_from(item)
        data = {
            "post_url"   : self.root + item[:item.find('"')],
            "game_appid" : extr('data-appid="', '"'),
            "file_id"    : extr('data-publishedfileid="', '"'),
            "url"        : extr("url('", "'"),
            "description": text.unescape(extr(
                '<q class="ellipsis">', '<')).strip(),
            "extension"  : "jpg",
        }

        if not data["url"]:
            data["url"] = text.unescape(extr(' src="', '"'))
        data["game"] = self.cache(
            self._extract_game, data["game_appid"], _mem=False)
        return data

    def _pagination(self, per_page=12):
        uid, type, qs = self.groups
        url = f"{self.root}/{uid}/{type}/screenshots"
        params = text.parse_query(qs)
        pnum = text.parse_int(params.get("p"), 1)

        data = {
            "appid"  : "0",
            "p"      : None,
            "privacy": "30",
            "content": "1",
            "browsefilter": "myfiles",
            "sort"   : "newestfirst",
            "view"   : "imagewall",
            **params,
        }
        headers = {
            "Accept": "text/javascript, text/html, application/xml, "
                      "text/xml, */*",
            "X-Requested-With": "XMLHttpRequest",
            "X-Prototype-Version": "1.7",
            "Origin" : self.root,
            "Referer": text.ensure_http_scheme(self.url),
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

        data["p"] = pnum
        while True:
            yield self.request(
                url, method="POST", headers=headers, data=data).text
            data["p"] += 1
