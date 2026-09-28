# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://steamcommunity.com/"""

from ..extractor.common import Extractor, Message
from .. import text, dt

BASE_PATTERN = r"(?:https?://)?(?:www\.)?steamcommunity.com"
CONTENT_TYPES = {"screenshots", "artwork"}


class SteamcommunitySharedfileExtractor(Extractor):
    """Extractor for steamcommunity shared files"""
    category = "steamcommunity"
    subcategory = "sharedfile"
    root = "https://steamcommunity.com"
    directory_fmt = ("{category}", "{game}", "{content_type!c}")
    filename_fmt = "{file_id} {title}.{extension}"
    archive_fmt = "{game}_{file_id}_{ugc_id}"
    pattern = BASE_PATTERN + r"/sharedfiles/filedetails/\?id=(\d+)"
    example = "https://steamcommunity.com/sharedfiles/filedetails/?id=12345"

    def items(self):
        fid = self.groups[0]
        url = f"{self.root}/sharedfiles/filedetails/?id={fid}"
        page = self.request(url).text
        content_type = self._extract_content_type(page)

        meta = {
            "content_type": content_type,
            "file_id"     : fid,
            "url"         : url,
        }

        return self.basic_image_items(page, meta)

    def _extract_content_type(self, page):
        tab = text.extr(
            page, 'class="apphub_sectionTab active "><span>', '<').lower()
        if tab in CONTENT_TYPES:
            return tab
        raise self.exc.AbortExtraction(f"Unsupported content type '{tab}'")

    def basic_image_items(self, page, meta):
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
            data["date"] = self.parse_datetime(date, "%d %b, %Y @ %I:%M%p")
        else:
            data["date"] = self.parse_datetime(
                date, "%d %b @ %I:%M%p").replace(year=dt.datetime.now().year)

        img = text.extr(page, '<img id="ActualMedia"', '>')
        src = text.unescape(text.extr(img, 'src="', '"'))
        if (pos := src.find("?")) >= 0:
            src = src[:pos]
        data["ugc_id"] = src[src.find("/ugc/")+5:-1]

        yield Message.Directory, "", data
        yield Message.Url, src, data
