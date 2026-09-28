# -*- coding: utf-8 -*-

# Copyright 2015-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import sys
from ..text import re_compile

modules = [
    "2ch",
    "2chan",
    "2chen",
    "35photo",
    "4chan",
    "4archive",
    "4chanarchives",
    "500px",
    "8chan",
    "8muses",
    "adultempire",
    "adultphotosets",
    "agnph",
    "ahottie",
    "allporncomic",
    "animepictures",
    "ao3",
    "arcalive",
    "architizer",
    "arena",
    "artfight",
    "artstation",
    "aryion",
    "audiochan",
    "bakashots",
    "batcave",
    "bbc",
    "behance",
    "bellazon",
    "bilibili",
    "blogger",
    "bluesky",
    "boosty",
    "booth",
    "bunkr",
    "cara",
    "catbox",
    "chevereto",
    "cien",
    "civitai",
    "clonr",
    "comedywildlifephoto",
    "comicartfans",
    "comicvine",
    "coomerfans",
    "cosmos",
    "cosplayrule34",
    "cyberdrop",
    "cyberfile",
    "danbooru",
    "dandadan",
    "dankefuerslesen",
    "dcinside",
    "deviantart",
    "discord",
    "dynastyscans",
    "e621",
    "eporner",
    "erome",
    "everia",
    "exhentai",
    "facebook",
    "fanbox",
    "fansly",
    "fantia",
    "fapello",
    "fapachi",
    "fikfap",
    "filester",
    "fitnakedgirls",
    "flickr",
    "foriio",
    "framedsc",
    "furaffinity",
    "furry34",
    "ganknow",
    "gelbooru",
    "gelbooru_v01",
    "gelbooru_v02",
    "girlsreleased",
    "girlswithmuscle",
    "gofile",
    "goonbox",
    "harvardlawnuremberg",
    "hatenablog",
    "hdoujin",
    "hentai2read",
    "hentaicosplays",
    "hentaifoundry",
    "hentaihand",
    "hentaihere",
    "hentainexus",
    "hiperdex",
    "hitomi",
    "hotleak",
    "idolcomplex",
    "imagebam",
    "imagechest",
    "imagefap",
    "imagepond",
    "imageshack",
    "imdb",
    "imgbb",
    "imgbox",
    "imgpile",
    "imgth",
    "imgur",
    "imhentai",
    "inkbunny",
    "instagram",
    "issuu",
    "itaku",
    "iwara",
    "joyreactor",
    "jschan",
    "kabeuchi",
    "kaliscan",
    "kagane",
    "keenspot",
    "kemono",
    "khinsider",
    "kokonotsuba",
    "komikcast",
    "koofr",
    "leakgallery",
    "leftybooru",
    "lensdump",
    "lexica",
    "lightroom",
    "listal",
    "livedoor",
    "lofter",
    "luscious",
    "lynxchan",
    "madokami",
    "mangadex",
    "mangafire",
    "mangafox",
    "mangafreak",
    "mangahere",
    "manganelo",
    "mangapark",
    "mangaread",
    "mangareader",
    "mangataro",
    "mangatown",
    "mangayi",
    "mangoxo",
    "mgrenders",
    "misskey",
    "mixdrop",
    "motherless",
    "myfigurecollection",
    "myhentaigallery",
    "myportfolio",
    "naverblog",
    "naverchzzk",
    "naverwebtoon",
    "newgrounds",
    "nhentai",
    "nijie",
    "nitter",
    "nozomi",
    "nsfwalbum",
    "nudostar",
    "okporn",
    "onlyhaven",
    "paheal",
    "patreon",
    "pawchive",
    "pexels",
    "philomena",
    "pholder",
    "photovogue",
    "picarto",
    "picazor",
    "pictoa",
    "piczel",
    "pillowfort",
    "pinterest",
    "pixeldrain",
    "pixiv",
    "pixnet",
    "plurk",
    "poipiku",
    "poringa",
    "pornhub",
    "pornpics",
    "pornstarstube",
    "postmill",
    "postype",
    "rawkuma",
    "reactor",
    "realbooru",
    "reddit",
    "redgifs",
    "rule34us",
    "rule34vault",
    "rule34xyz",
    "s3ndpics",
    "sakuhentai",
    "sankaku",
    "sankakucomplex",
    "scatbooru",
    "schalenetwork",
    "scrolller",
    "seiga",
    "senmanga",
    "sexcom",
    "shareimage",
    "shimmie2",
    "simplyhentai",
    "sizebooru",
    "skeb",
    "slickpic",
    "slideshare",
    "smugmug",
    "snapchat",
    "sofurry",
    "soundgasm",
    "speakerdeck",
    "steamcommunity",
    "steamgriddb",
    "subscribestar",
    "sxypix",
    "szurubooru",
    "tapas",
    "tcbscans",
    "telegraph",
    "tenor",
    "thefap",
    "thehentaiworld",
    "tiktok",
    "tmohentai",
    "toyhouse",
    "threads",
    "tumblr",
    "tumblrgallery",
    "tungsten",
    "turbo",
    "twibooru",
    "twitter",
    "urlgalleries",
    "unsplash",
    "uploadir",
    "urlshortener",
    "vanillarock",
    "vanlifetrader",
    "vichan",
    "vipergirls",
    "vk",
    "vsco",
    "wallhaven",
    "wallpapercave",
    "warosu",
    "weasyl",
    "webmshare",
    "webtoons",
    "weebcentral",
    "weibo",
    "whitekitten",
    "whyp",
    "wikiart",
    "wikifeet",
    "wikimedia",
    "xasiat",
    "xenforo",
    "xfolio",
    "xhamster",
    "xvideos",
    "yiffverse",
    "yourlesbians",
    "zerochan",
    "booru",
    "moebooru",
    "foolfuuka",
    "foolslide",
    "mastodon",
    "shopify",
    "lolisafe",
    "imagehosts",
    "directlink",
    "recursive",
    "oauth",
    "noop",
    "ytdl",
    "generic",
]


def find(url):
    """Find a suitable extractor for the given URL"""
    for cls in _list_classes():
        if match := cls.pattern.match(url):
            return cls(match)
    return None


def add(cls):
    """Add 'cls' to the list of available extractors"""
    if isinstance(cls.pattern, str):
        cls.pattern = re_compile(cls.pattern)
    _cache.append(cls)
    return cls


def add_module(module):
    """Add all extractors in 'module' to the list of available extractors"""
    if classes := _get_classes(module):
        if isinstance(classes[0].pattern, str):
            for cls in classes:
                cls.pattern = re_compile(cls.pattern)
        _cache.extend(classes)
    return classes


def extractors():
    """Yield all available extractor classes"""
    return sorted(
        _list_classes(),
        key=lambda x: x.__name__
    )


# --------------------------------------------------------------------
# internals


def _list_classes():
    """Yield available extractor classes"""
    yield from _cache

    for module in _module_iter:
        yield from add_module(module)

    globals()["_list_classes"] = lambda : _cache


def _modules_internal():
    globals_ = globals()
    for module_name in modules:
        yield __import__(module_name, globals_, None, None, 1)


def _modules_path(path, files):
    sys.path.insert(0, path)
    try:
        return [__import__(name) for name in files]
    finally:
        del sys.path[0]


def _get_classes(module):
    """Return a list of all extractor classes in a module"""
    return [
        cls for cls in module.__dict__.values() if (
            hasattr(cls, "pattern") and cls.__module__ == module.__name__
        )
    ]


_cache = []
_module_iter = _modules_internal()
