# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import rawkuma


__tests__ = (
{
    "#url"     : "https://rawkuma.net/manga/saikyou-onmyouji-no-isekai-tenseiki-geboku-no-youkaidomo-ni-kurabete-monster-ga-yowaisugirundaga/chapter-3.28214/",
    "#class"   : rawkuma.RawkumaChapterExtractor,
    "#pattern" : r"https://rcdn\.kyut\.dev/images/s/saikyou-inyoushi-no-isekai-tenseiki-manga-raw/3/\d+\.png",
    "#count"   : 28,

    "chapter"      : 3,
    "chapter_id"   : 28214,
    "chapter_minor": "",
    "count"        : 28,
    "page"         : range(1, 28),
    "date"         : "dt:2025-09-14 15:57:26",
    "extension"    : "png",
    "filename"     : str,
    "lang"         : "ja",
    "language"     : "Japanese",
    "manga"        : "Saikyou Onmyouji no Isekai Tenseiki ~Geboku no Youkaidomo ni Kurabete Monster ga Yowaisugirundaga~",
    "manga_id"     : 784,
},

{
    "#url"     : "https://rawkuma.net/manga/makutsu-no-ou-yomei-ikkagetsu-no-doutei-mahou-shoujo-harem-o-kizuite-ou-e-kunrinsu/chapter-3.4.205398/",
    "#class"   : rawkuma.RawkumaChapterExtractor,
    "#pattern" : r"https://rcdn\.kyut\.dev/m/makutsu\-no\-ou\-yomei\-ikkagetsu\-no\-doutei\-mahou\-shoujo\-harem\-o\-kizuite\-ou\-e\-kunrinsu/chapter\-3\-4/\d+\.jpg",
    "#count"   : 10,

    "chapter"      : 3,
    "chapter_id"   : 205398,
    "chapter_minor": ".4",
    "count"        : 10,
    "page"         : range(1, 10),
    "date"         : "dt:2025-10-03 17:41:22",
    "extension"    : "jpg",
    "filename"     : str,
    "lang"         : "ja",
    "language"     : "Japanese",
    "manga"        : "Makutsu no Ou ~Yomei Ikkagetsu no Doutei, Mahou Shoujo Harem o Kizuite Ou e Kunrinsu~",
    "manga_id"     : 194526,
},

{
    "#url"     : "https://rawkuma.net/manga/yani-neko/chapter-270.160879/",
    "#class"   : rawkuma.RawkumaChapterExtractor,
    "#results" : (
        "https://rcdn.kyut.dev/images/y/yani-neko/270/1.jpg",
        "https://rcdn.kyut.dev/images/y/yani-neko/270/2.jpg",
        "https://rcdn.kyut.dev/images/y/yani-neko/270/3.jpg",
        "https://rcdn.kyut.dev/images/y/yani-neko/270/4.jpg",
    ),

    "chapter"      : 270,
    "chapter_id"   : 160879,
    "chapter_minor": "",
    "count"        : 4,
    "date"         : "dt:2025-09-29 07:40:35",
    "extension"    : "jpg",
    "lang"         : "ja",
    "language"     : "Japanese",
    "manga"        : "Yani Neko",
    "manga_id"     : 58377,
},

{
    "#url"     : "https://rawkuma.net/manga/yani-neko/chapter-274.160909/",
    "#class"   : rawkuma.RawkumaChapterExtractor,
    "#results" : (
        "https://rcdn.kyut.dev/y/yani-neko/chapter-274/1.jpg",
        "https://rcdn.kyut.dev/y/yani-neko/chapter-274/2.jpg",
        "https://rcdn.kyut.dev/y/yani-neko/chapter-274/3.jpg",
        "https://rcdn.kyut.dev/y/yani-neko/chapter-274/4.jpg",
    ),

    "chapter"      : 274,
    "chapter_id"   : 160909,
    "chapter_minor": "",
    "count"        : 4,
    "date"         : "dt:2025-09-29 07:41:21",
    "extension"    : "jpg",
    "lang"         : "ja",
    "language"     : "Japanese",
    "manga"        : "Yani Neko",
    "manga_id"     : 58377,
},

{
    "#url"     : "https://rawkuma.net/manga/makutsu-no-ou-yomei-ikkagetsu-no-doutei-mahou-shoujo-harem-o-kizuite-ou-e-kunrinsu",
    "#class"   : rawkuma.RawkumaMangaExtractor,
    "#pattern" : rawkuma.RawkumaChapterExtractor.pattern,
    "#count"   : range(55, 80),

    "chapter"      : range(1, 20),
    "chapter-minor": {"", ".1", ".2", ".3", ".4"},
    "chapter_id"   : int,
    "manga"        : "Makutsu no Ou ~Yomei Ikkagetsu no Doutei, Mahou Shoujo Harem o Kizuite Ou e Kunrinsu~",
    "manga_id"     : 194526,
},

{
    "#url"     : "https://rawkuma.net/manga/yani-neko/",
    "#class"   : rawkuma.RawkumaMangaExtractor,
    "#pattern" : rawkuma.RawkumaChapterExtractor.pattern,
    "#count"   : range(400, 600),

    "chapter"      : int,
    "chapter-minor": {"", ".5"},
    "chapter_id"   : int,
    "manga"        : "Yani Neko",
    "manga_id"     : 58377,
},

)
