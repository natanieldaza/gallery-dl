# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import hentaihere


__tests__ = (
{
    "#url"     : "https://hentaihere.com/reader/13812-amazon-elixir/20902/page-1",
    "#class"   : hentaihere.HentaihereChapterExtractor,
    "#pattern" : r"https://hermes\.hentai\.direct/hentai/13812/1/hcdn\d+\.jpg",
    "#count"   : 16,

    "author"       : ["Morris"],
    "chapter"      : 1,
    "chapter_id"   : 20902,
    "chapter_minor": "",
    "count"        : 16,
    "extension"    : "jpg",
    "filename"     : str,
    "width"        : int,
    "height"       : int,
    "lang"         : "en",
    "manga"        : "Amazon Elixir",
    "manga_cover"  : "https://hermes.hentai.direct/hentai/cover/_S13812.jpg",
    "manga_date"   : "dt:2015-10-29 15:36:26",
    "manga_id"     : 13812,
    "manga_slug"   : "amazon-elixir",
    "manga_url"    : "https://hentaihere.com/original/13812-amazon-elixir",
    "page"         : int,
    "title"        : "Amazon Elixir [Oneshot]",
    "type"         : "original",
    "tags"         : [
        "Cheating",
        "Creampie",
        "Drugs",
        "MILFs",
        "Mother and Son",
        "Sex Toys",
        "X-Ray",
    ],
},

{
    "#url"     : "https://hentaihere.com/reader/2011-countdown-sex-bombs/2020",
    "#comment" : "no '/page-N'",
    "#class"   : hentaihere.HentaihereChapterExtractor,
},

{
    "#url"     : "https://hentaihere.com/m/S13812/1/1/",
    "#comment" : "legacy URL",
    "#class"   : hentaihere.HentaihereChapterExtractor,
},

{
    "#url"     : "https://hentaihere.com/m/S23048/1.5/1/",
    "#comment" : "legacy URL",
    "#class"   : hentaihere.HentaihereChapterExtractor,
    "#pattern" : r"https://hermes.hentai.direct/hentai/23048/1.5/ccdn\d+\.jpg",
    "#count"   : 32,

    "author"       : ["Shinozuka Yuuji"],
    "chapter"      : 1,
    "chapter_id"   : 80186,
    "chapter_minor": ".5",
    "count"        : 32,
    "lang"         : "en",
    "manga"        : "High School Slut's Love Consultation",
    "manga_id"     : 23048,
    "page"         : int,
    "title"        : "High School Slut's Love Consultation + Girlfriend [Full Color]",
    "type"         : "original",
},

{
    "#url"     : "https://hentaihere.com/original/2011-countdown-sex-bombs",
    "#class"   : hentaihere.HentaihereMangaExtractor,
    "#results" : "https://hentaihere.com/reader/2011-countdown-sex-bombs/2020/page-1",

    "author"       : ["UTATANE Hiroyuki"],
    "chapter"      : 1,
    "chapter_id"   : 2020,
    "chapter_minor": "",
    "lang"         : "en",
    "manga"        : "Countdown: Sex Bombs",
    "manga_cover"  : "https://hermes.hentai.direct/hentai/cover/_S2011.jpg",
    "manga_date"   : "dt:2011-11-10 07:42:50",
    "manga_id"     : 2011,
    "manga_slug"   : "countdown-sex-bombs",
    "manga_url"    : "https://hentaihere.com/original/2011-countdown-sex-bombs",
    "title"        : "Volume 1 [END]",
    "type"         : "original",
    "tags"         : [
        "Blow job",
        "Brother and Sister",
        "Creampie",
        "Cunnilingus",
        "Father and Daughter",
        "Female Dominance",
        "Fingering",
        "Gender Bender",
    ],
},

{
    "#url"     : "https://hentaihere.com/m/S7608",
    "#comment" : "legacy URL",
    "#class"   : hentaihere.HentaihereMangaExtractor,
    "#pattern" : hentaihere.HentaihereChapterExtractor.pattern,
    "#count"   : 10,

    "author"       : ["CHIBA Toshirou"],
    "chapter"      : int,
    "chapter_id"   : int,
    "chapter_minor": "",
    "lang"         : "en",
    "manga"        : "Oshikake Riot",
    "manga_cover"  : "https://hermes.hentai.direct/hentai/cover/_S7608.jpg",
    "manga_date"   : "dt:2014-04-16 09:27:26",
    "manga_id"     : 7608,
    "manga_slug"   : "oshikake-riot",
    "manga_url"    : "https://hentaihere.com/original/7608-oshikake-riot",
    "title"        : r"re:Oshikake Riot( \d+)?",
    "type"         : "original",
    "tags"         : [
        "Ahegao",
        "Bondage",
        "Censored",
        "Deep Throat",
        "Glasses",
        "Happy Sex",
        "Kunoichi (Ninja Girls)",
        "Paizuri",
        "Small Breasts",
    ],
},

)
