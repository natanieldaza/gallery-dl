# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import kagane


__tests__ = (
{
    "#url"     : "https://kagane.to/series/019cd87a-0a8d-7ef6-b72b-5a250a72bd79/reader/019ea2c4-61ef-718e-bffe-842dca4aa270",
    "#class"   : kagane.KaganeChapterExtractor,
    "#pattern" : r"https://kstatic\.to/api/v\d/books/page/[\w-]+/[\w-]+\.jxl",
    "#count"   : 13,

    "chapter"       : 1150,
    "chapter_id"    : "019ea2c4-61ef-718e-bffe-842dca4aa270",
    "chapter_minor" : "",
    "chapter_string": "ONE PIECE - Chapter 1150 - Chapter 1150: Domi Reversi",
    "content_rating": "Suggestive",
    "count"         : 13,
    "height"        : int,
    "lang"          : "en",
    "language"      : "English",
    "manga"         : "ONE PIECE",
    "manga_date"    : "dt:2026-03-10 16:00:02",
    "manga_id"      : "019cd87a-0a8d-7ef6-b72b-5a250a72bd79",
    "page"          : range(1, 13),
    "page_id"       : str,
    "rating"        : float,
    "status"        : str,
    "title"         : "Chapter 1150: Domi Reversi",
    "type"          : "Manga",
    "volume"        : int,
    "width"         : int,
    "tags"          : list,
    "manga_alt"     : ["ONE PIECE", "ワンピース", "원피스"],
    "genres"        : [
        "Drama",
        "Fantasy",
        "Adventure",
        "Action",
        "Comedy",
        "Shounen",
    ],
},

{
    "#url"     : "https://kagane.to/series/019cd87a-0a8d-7ef6-b72b-5a250a72bd79",
    "#class"   : kagane.KaganeMangaExtractor,
    "#pattern" : kagane.KaganeChapterExtractor.pattern,
    "#count"   : 40,

    "chapter"       : int,
    "chapter_minor" : {"", ".5"},
    "chapter_id"    : str,
    "content_rating": "Suggestive",
    "date"          : "type:datetime",
    "lang"          : "en",
    "language"      : "English",
    "manga"         : "ONE PIECE",
    "manga_date"    : "dt:2026-03-10 16:00:02",
    "manga_id"      : "019cd87a-0a8d-7ef6-b72b-5a250a72bd79",
    "rating"        : float,
    "status"        : str,
    "type"          : "Manga",
    "views"         : int,
    "tags"          : list,
    "manga_alt"     : ["ONE PIECE", "ワンピース", "원피스"],
    "genres"        : [
        "Drama",
        "Fantasy",
        "Adventure",
        "Action",
        "Comedy",
        "Shounen",
    ],
},

{
    "#url"     : "https://kagane.si/series/the-ogre-s-bride-019c5678-f35c-7589-9375-912718d50bd0",
    "#class"   : kagane.KaganeMangaExtractor,
},

{
    "#url"     : "https://kagane.cx/series/the-ogre-s-bride-019c5678-f35c-7589-9375-912718d50bd0",
    "#class"   : kagane.KaganeMangaExtractor,
},

{
    "#url"     : "https://kagane.moe/series/the-ogre-s-bride-019c5678-f35c-7589-9375-912718d50bd0",
    "#class"   : kagane.KaganeMangaExtractor,
},

{
    "#url"     : "https://kagane.net/series/the-ogre-s-bride-019c5678-f35c-7589-9375-912718d50bd0",
    "#class"   : kagane.KaganeMangaExtractor,
},

)
