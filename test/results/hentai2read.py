# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import hentai2read


__tests__ = (
{
    "#url"     : "https://hentai2read.com/reader/13088-popuni-kei-joshi-panic/116411/page-1",
    "#class"   : hentai2read.Hentai2readChapterExtractor,
    "#pattern" : r"https://hentaicdn\.com/hentai/up/13088/c116411-jkvvy8/\d+\.webp",
    "#count"   : 36,

    "author"       : ["Kurisu", "Potato Salad (Himekuri Kurisu)"],
    "chapter"      : 2,
    "chapter_id"   : 116411,
    "chapter_minor": ".5",
    "count"        : 36,
    "lang"         : "en",
    "manga"        : "Popuni Kei Joshi Panic!",
    "manga_id"     : 13088,
    "page"         : int,
    "title"        : "Popuni Kei Joshi Panic! 2.5",
    "type"         : "Original",
},

{
    "#url"     : "https://hentai2read.com/reader/2720-nozoki-ana-ecchi/2965/page-1",
    "#class"   : hentai2read.Hentai2readChapterExtractor,
    "#pattern" : r"https://hentaicdn\.com/hentai/2720/1/hcdn00\d+\.jpg",
    "#count"   : 203,

    "author"       : [],
    "chapter"      : 1,
    "chapter_id"   : 2965,
    "chapter_minor": "",
    "count"        : 203,
    "extension"    : "jpg",
    "filename"     : str,
    "lang"         : "en",
    "manga"        : "Nozoki Ana [Ecchi]",
    "manga_id"     : 2720,
    "page"         : range(1, 203),
    "subcategory"  : "chapter",
    "title"        : "Nozoki Ana 1",
    "type"         : "Original",

},

{
    "#url"     : "https://hentai2read.com/amazon_elixir/",
    "#comment" : "legacy URL format",
    "#class"   : hentai2read.Hentai2readMangaExtractor,
    "#result"  : "",
},

{
    "#url"     : "https://hentai2read.com/oshikage_riot/",
    "#class"   : hentai2read.Hentai2readMangaExtractor,
    "#pattern" : hentai2read.Hentai2readChapterExtractor.pattern,
    "#count"   : 10,

},

{
    "#url"     : "https://hentai2read.com/popuni_kei_joshi_panic/",
    "#class"   : hentai2read.Hentai2readMangaExtractor,
    "#pattern" : hentai2read.Hentai2readChapterExtractor.pattern,

    "chapter"      : int,
    "chapter_id"   : int,
    "chapter_minor": {"", ".5", ".6"},
    "lang"         : "en",
    "manga"        : "Popuni Kei Joshi Panic!",
    "manga_id"     : 13088,
    "title"        : str,
    "type"         : "Original",
},

)
