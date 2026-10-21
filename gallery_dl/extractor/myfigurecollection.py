# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://myfigurecollection.net/"""

from .common import Extractor, Message, Dispatch
from .. import text, util
import itertools

BASE_PATTERN = r"(?:https?://)?(?:www\.)?myfigurecollection\.net"
USER_PATTERN = BASE_PATTERN + r"/profile/([^/?#]+)"


class MyfigurecollectionExtractor(Extractor):
    """Base class for myfigurecollection extractors"""
    category = "myfigurecollection"
    root = "https://myfigurecollection.net"
    parent = True

    def _pagination(self, params):
        url = self.root + "/"
        params["page"] = text.parse_int(params.get("page"), 1)

        find_ids = text.re(r'<a href="/\w+/(\d+)').findall
        while True:
            page = self.request(url, params=params).text
            results, pos = text.extract(
                page, '<div class="results">', '<div class="results-count">')

            yield from find_ids(results)

            pos = page.find("nav-current", pos)
            if page.find('"nav-page', pos) < 0:
                break
            params["page"] += 1


class MyfigurecollectionItemExtractor(MyfigurecollectionExtractor):
    subcategory = "item"
    directory_fmt = ("{category}", "Items")
    filename_fmt = "{id}_{num:>02}_{filename}.{extension}"
    archive_fmt = "i{id}_{num}"
    pattern = BASE_PATTERN + r"/item/(\d+)"
    example = "https://myfigurecollection.net/item/12345"

    def items(self):
        item_id = self.groups[0]
        url = f"{self.root}/item/{item_id}"
        extr = text.extract_from(self.request(url).text)

        item = {
            "id"        : item_id,
            "title_html": text.unescape(extr(
                'property="og:title" content="', '"')),
            "post_url"  : text.unescape(extr(
                'property="og:url" content="', '"')),
            "pictures"  : extr(
                'name="pictures" content="', '"'),
            "Category"  : split(extr(
                'class="data-label">Categor', "</div></div>")),
            "classification": split_meta(extr(
                'class="data-label">Classificatio', "</div></div>")),
            "title"     : rm(extr(
                'class="data-label">Title', "</div></div>")),
            "origin"    : split(extr(
                'class="data-label">Origi', "</div></div>")),
            "character" : split(extr(
                'class="data-label">Characte', "</div></div>")),
            "company"   : split_meta(extr(
                'class="data-label">Compan', "</div></div>")),
            "artist"    : split_meta(extr(
                'class="data-label">Artis', "</div></div>")),
            "release"   : self._parse_releases(extr(
                'class="data-label">Releas',
                '</div></div><div class="data-field"><div class="data-l')),
            "material"  : rm(extr(
                'abel">Materia', "</div></div>")),
            "dimensions": rm(extr(
                'abel">Dimensio', "</div></div>")),
            "various"   : rm(extr(
                'abel">Variou', "</div></div>")),
            "tags"      : text.split_html(extr(
                '<div class="object-tags">', "</section>"))[::2],
        }

        item["material"] = m.split(" , ") if (m := item["material"]) else ""

        files = util.json_loads(text.unquote(item.pop("pictures")))
        item["count"] = len(files)

        yield Message.Directory, "", item
        for item["num"], file in enumerate(files, 1):
            url = file["src"]
            item["width"] = file["w"]
            item["height"] = file["h"]
            text.nameext_from_url(url, item)
            if not item["filename"]:
                item["filename"] = item_id
                item["extension"] = "jpg"
            yield Message.Url, url, item

    def _parse_releases(self, html):
        items = html.split('<div class="data-value">')
        del items[0]

        results = []
        for item in items:
            date, pos = text.extract(item, ">", "<")
            type, pos = text.extract(item, "<em>", "<", pos)
            price, pos = text.extract(item, "<br/>", "(", pos)

            parts = date.split("/")
            try:
                name = f"{parts[2]}-{parts[1]}-{parts[0]}"
            except Exception:
                if len(parts) < 2:
                    results.append(text.remove_html(item))
                    continue
                name = f"{parts[1]}-{parts[0]}"
            if price:
                name = f"{name}: {price.replace('<small>', '').strip()}"
            if type:
                name = f"{name} ({type})"
            results.append(name)
        return results


class MyfigurecollectionPictureExtractor(MyfigurecollectionExtractor):
    subcategory = "picture"
    directory_fmt = ("{category}", "{user}", "Photos")
    filename_fmt = "{id} {title}.{extension}"
    archive_fmt = "p{id}"
    pattern = BASE_PATTERN + r"/picture/(\d+)"
    example = "https://myfigurecollection.net/picture/12345"

    def items(self):
        item_id = self.groups[0]
        url = f"{self.root}/picture/{item_id}"
        extr = text.extract_from(self.request(url).text)

        item = {
            "id"      : item_id,
            "title"   : text.unescape(extr(
                'property="og:title" content="', '"')),
            "post_url": text.unescape(extr(
                'property="og:url" content="', '"')),
            "Category": text.split_html(extr(
                'class="categories">', "</div></div><")),
            "user"  : text.remove_html(extr("<section>", "</a><span")),
            "date"  : self.parse_datetime(extr(
                '<span title="', '"'), "%m/%d/%Y, %H:%M:%S"),
            "url"   : extr('the-picture"><a href="', '"'),
            "width" : text.parse_int(extr(
                '<a class="size', ">") and extr("", "&times;")),
            "height": text.parse_int(extr("", " ")),
            "size"  : text.parse_bytes(extr("(", "iB")),
            "description": extr('<div class="bbcode">', "</div>"),
            "tags"  : text.split_html(extr(
                '<div class="object-tags">', "</section>"))[::2],
        }

        url = item["url"]
        yield Message.Directory, "", item
        yield Message.Url, url, text.nameext_from_url(url, item)


class MyfigurecollectionArticleExtractor(MyfigurecollectionExtractor):
    subcategory = "article"
    directory_fmt = ("{category}", "{user}", "Articles",
                     "{date:%Y-%m-%d} {id} {title}")
    filename_fmt = "{num:>02}.{extension}"
    archive_fmt = "a{id}_{num}"
    pattern = BASE_PATTERN + r"/blogpost/(\d+)"
    example = "https://myfigurecollection.net/blogpost/12345"

    def items(self):
        item_id = self.groups[0]
        url = f"{self.root}/blogpost/{item_id}"
        extr = text.extract_from(self.request(url).text)

        item = {
            "id"      : item_id,
            "title"   : text.unescape(extr(
                'property="og:title" content="', '"')),
            "post_url": text.unescape(extr(
                'property="og:url" content="', '"')),
            "Category": text.split_html(extr(
                'class="categories">', "</div></div><")),
            "user"  : text.remove_html(extr("<section>", "</a><span")),
            "date"  : self.parse_datetime(extr(
                '<span title="', '"'), "%m/%d/%Y, %H:%M:%S"),
            "body"  : extr(
                'eBody"><div class="bbcode">', '</div></div></div></div><div'),
            "views" : extr(">", " ").replace(",", ""),
            "likes" : extr(">", " ").replace(",", ""),
            "comments": extr('/comments/">', " ").replace(",", ""),
            "tags"  : text.split_html(extr(
                '<div class="object-tags">', "</section>"))[::2],
        }

        files = text.re(r'<img[^>]*? alt="([^"]+)').findall(
            item["body"])
        item["count"] = len(files)

        yield Message.Directory, "", item
        for item["num"], url in enumerate(files, 1):
            yield Message.Url, url, text.nameext_from_url(url, item)


class MyfigurecollectionUserExtractor(Dispatch, MyfigurecollectionExtractor):
    pattern = USER_PATTERN + r"/?(?:$|\?|#)"
    example = "https://myfigurecollection.net/profile/USER"

    def items(self):
        base = f"{self.root}/profile/{self.groups[0]}/"
        return self._dispatch_extractors((
            (MyfigurecollectionUserCollectionExtractor, base + "collection/"),
            (MyfigurecollectionUserPicturesExtractor  , base + "pictures/"),
            (MyfigurecollectionUserArticlesExtractor  , base + "blogposts/"),
        ), ("user-pictures",))


class MyfigurecollectionUserCollectionExtractor(MyfigurecollectionExtractor):
    subcategory = "user-collection"
    pattern = (BASE_PATTERN + r"/(?:profile/([^/?#]+)/collection"
               r"|\?(mode=view&username=[^&#]+&tab=collection[^#]*))")
    example = "https://myfigurecollection.net/profile/USER/collection/"

    def items(self):
        username, query = self.groups
        if username:
            params = {
                "mode"      : "view",
                "username"  : username,
                "tab"       : "collection",
                "status"    : "2",
                "current"   : "keywords",
                "rootId"    : "-1",
                "categoryId": "-1",
                "output"    : "2",
                "sort"      : "category",
                "order"     : "asc",
                "_tb"       : "user",
                "page"      : 1,

            }
        else:
            params = text.parse_query(query)

        data = {"_extractor": MyfigurecollectionItemExtractor}
        base = self.root + "/item/"
        for item_id in self._pagination(params):
            yield Message.Queue, base + item_id, data


class MyfigurecollectionUserPicturesExtractor(MyfigurecollectionExtractor):
    subcategory = "user-pictures"
    pattern = (BASE_PATTERN + r"/(?:profile/([^/?#]+)/pictures"
               r"|\?(mode=view&username=[^&#]+&tab=pictures[^#]*))")
    example = "https://myfigurecollection.net/profile/USER/pictures/"

    def items(self):
        username, query = self.groups
        if username:
            params = {
                "mode"      : "view",
                "username"  : username,
                "tab"       : "pictures",
                "current"   : "tags",
                "categoryId": "0",
                "albumId"   : "-1",
                "sort"      : "date",
                "order"     : "desc",
                "_tb"       : "user",
                "page"      : 1,
            }

            url = f"{self.root}/profile/{username}/pictures/"
            page = self.request(url).text
            categories = text.extr(page, 'class="object-categories', "</div>")

            items = []
            for cid in text.extract_iter(categories, 'picture-category-', '"'):
                params["categoryId"] = cid
                items.append(self._pagination(params.copy()))
            items = itertools.chain(*items)
        else:
            params = text.parse_query(query)
            items = self._pagination(params)

        data = {"_extractor": MyfigurecollectionPictureExtractor}
        base = self.root + "/picture/"
        for item_id in items:
            yield Message.Queue, base + item_id, data


class MyfigurecollectionUserArticlesExtractor(MyfigurecollectionExtractor):
    subcategory = "user-articles"
    pattern = (BASE_PATTERN + r"/(?:profile/([^/?#]+)/blogposts"
               r"|\?(mode=view&username=[^&#]+&tab=blogposts[^#]*))")
    example = "https://myfigurecollection.net/profile/USER/blogposts/"

    def items(self):
        username, query = self.groups

        if username:
            params = {
                "mode"      : "view",
                "username"  : username,
                "tab"       : "blogposts",
                "current"   : "keywords",
                "sort"      : "date",
                "order"     : "desc",
                "categoryId": "-1",
                "isSelected": "0",
                "_tb"       : "user",
                "page"      : "1",
            }
        else:
            params = text.parse_query(query)

        data = {"_extractor": MyfigurecollectionArticleExtractor}
        base = self.root + "/blogpost/"
        for item_id in util.unique_sequence(self._pagination(params)):
            yield Message.Queue, base + item_id, data


def split(html):
    if not html:
        return ()
    results = text.split_html(html)
    del results[0]
    return results


def split_meta(html):
    items = html.split("<meta ")
    del items[0]

    results = []
    for item in items:
        pos = item.find("</span>")
        name = text.unescape(item[item.rfind(">", 0, pos)+1:pos])
        if role := text.extr(item, "<em>", "<"):
            name = f"{name} ({text.unescape(role)})"
        results.append(name)
    return results


def rm(html):
    return (text.unescape(text.remove_html(html[html.find(">")+1:]))
            if html else "")
