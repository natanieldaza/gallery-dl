# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import xasiat


__tests__ = (
{
    "#url"    : "https://www.xasiat.com/albums/28156/photobook-2024-12-09-bomb/",
    "#class"  : xasiat.XasiatAlbumExtractor,
    "#pattern": r"https://www.xasiat.com/get_image/2/\w{32}/sources/28000/28156/\d+.jpg/",
    "#count"  : 61,

    "title"         : "[Photobook] 2024.12.09 白濱美兎『忘れられない恋の味』BOMBデジタル写真集",
    "album_category": "JAV & AV Models",
    "album_id"      : 28156,
    "album_url"     : "https://www.xasiat.com/albums/28156/photobook-2024-12-09-bomb/",
    "count"         : 61,
    "num"           : range(1, 61),
    "extension"     : "jpg",
    "filename"      : r"re:\d+",
    "model"         : [],
    "tags"          : [
        "BOMB Photobook",
        "Photobook",
    ],
},

{
    "#url"  : "https://www.xasiat.com/ja/albums/28155/cosplay1813/",
    "#class": xasiat.XasiatAlbumExtractor,
    "#count": 40,

    "title"         : "[Cosplay] 喜欢爱理吗 - 早濑优香",
    "album_category": "Cosplay",
    "album_id"      : 28155,
    "album_url"     : "https://www.xasiat.com/ja/albums/28155/cosplay1813/",
    "count"         : 40,
    "num"           : range(1, 40),
    "model"         : [],
    "tags"          : [],
},

{
    "#url"  : "https://www.xasiat.com/fr/albums/23354/friday-impact-beauty-col-1/",
    "#class": xasiat.XasiatAlbumExtractor,
    "#count": 51,

    "title"         : "FRIDAYデジタル写真集 下村明香『Impact Beauty col.1』全カット",
    "album_category": "Gravure Idols",
    "model"         : ["Sayaka Shimomura"],
    "tags"          : [
        "FRIDAY Digital Photobook",
        "De Toute Beauté",
    ],
},

{
    "#url"     : "https://www.xasiat.com/albums/30478/gekkan-young-magazine-2025-no-11/",
    "#comment" : "no 'album_category' (#8569)",
    "#class"   : xasiat.XasiatAlbumExtractor,
    "#pattern" : r"https://www\.xasiat\.com/get_image/\d+/\w+",
    "#count"   : 13,

    "album_category": "",
    "album_id"      : 30478,
    "album_url"     : "https://www.xasiat.com/albums/30478/gekkan-young-magazine-2025-no-11/",
    "count"         : 13,
    "extension"     : "jpg",
    "model"         : [],
    "title"         : "[Gekkan Young Magazine] 2025 No.11",
    "tags"          : [
        "Young Magazine",
        "Teen",
    ],
},

{
    "#url"    : "https://www.xasiat.com/categories/gravure-idols/",
    "#comment": "videos",
    "#class"  : xasiat.XasiatCategoryExtractor,
    "#pattern": xasiat.XasiatVideoExtractor.pattern,
    "#range"  : "1-50",
    "#count"  : 50,
},

{
    "#url"    : "https://www.xasiat.com/albums/categories/gravure-idols/",
    "#class"  : xasiat.XasiatCategoryExtractor,
    "#pattern": xasiat.XasiatAlbumExtractor.pattern,
    "#range"  : "1-50",
    "#count"  : 50,
},

{
    "#url"    : "https://www.xasiat.com/tags/japan/",
    "#comment": "videos",
    "#class"  : xasiat.XasiatTagExtractor,
    "#pattern": xasiat.XasiatVideoExtractor.pattern,
    "#range"  : "1-50",
    "#count"  : 50,
},

{
    "#url"    : "https://www.xasiat.com/albums/tags/japan/",
    "#class"  : xasiat.XasiatTagExtractor,
    "#pattern": xasiat.XasiatAlbumExtractor.pattern,
    "#range"  : "1-50",
    "#count"  : 50,
},

{
    "#url"    : "https://www.xasiat.com/fr/albums/tags/japan/",
    "#comment": "'fr' lang",
    "#class"  : xasiat.XasiatTagExtractor,
    "#pattern": xasiat.XasiatAlbumExtractor.pattern,
    "#range"  : "1-50",
    "#count"  : 50,
},

{
    "#url"    : "https://www.xasiat.com/models/umi-yatsugake/",
    "#comment": "videos",
    "#class"  : xasiat.XasiatModelExtractor,
    "#pattern": xasiat.XasiatVideoExtractor.pattern,
    "#count"  : 35,
},

{
    "#url"    : "https://www.xasiat.com/ja/models/umi-yatsugake/",
    "#comment": "'ja' lang",
    "#class"  : xasiat.XasiatModelExtractor,
    "#pattern": xasiat.XasiatVideoExtractor.pattern,
    "#count"  : 35,
},

{
    "#url"    : "https://www.xasiat.com/albums/models/remu-suzumori/",
    "#class"  : xasiat.XasiatModelExtractor,
    "#pattern": xasiat.XasiatAlbumExtractor.pattern,
    "#count"  : 47,
},

{
    "#url"     : "https://www.xasiat.com/fr/search/2024-2025/",
    "#class"   : xasiat.XasiatSearchExtractor,
    "#pattern" : xasiat.XasiatAlbumExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://www.xasiat.com/videos/94383/sbmo-01285-you-ll-always-be-our-sister-complete-best2-mirai-takahashi/",
    "#class"   : xasiat.XasiatVideoExtractor,
    "#pattern" : r"https://www.xasiat.com/get_file/19/5a6dee732f21cd2ddb206b3a843a0ce3/94000/94383/94383_source.mp4/\?v-acctoken=\w+",

    "count"         : 1,
    "date"          : "dt:2025-08-06 04:41:21",
    "duration"      : 17951,
    "extension"     : "mp4",
    "filename"      : "94383_source",
    "height"        : 1080,
    "likes"         : range(5, 15),
    "model"         : ["Miku Takahashi"],
    "thumbnail"     : "https://pic.xascdn.li/contents/videos_screenshots/94000/94383/preview.jpg",
    "title"         : "SBMO-01285 You'll Always Be Our Sister COMPLETE BEST2-Mirai Takahashi",
    "type"          : "video",
    "video_category": "Gravure Idols",
    "video_id"      : 94383,
    "video_url"     : "https://www.xasiat.com/videos/94383/sbmo-01285-you-ll-always-be-our-sister-complete-best2-mirai-takahashi/",
    "views"         : range(10_000, 20_000),
    "width"         : 1920,
    "tags"          : [
        "28-year-old",
        "SBMO",
        "Sister",
    ],
},

{
    "#url"     : "https://www.xasiat.com/videos/118556/4897531-50-off-217-yuna-a-23-year-old-with-little-experience-moans-innocently-as-she-savours-sex-you-ll-be-able-to-jerk-off-to-this-at-least-20-times-uncensored-as-a-bonus/",
    "#comment" : "4K video",
    "#class"   : xasiat.XasiatVideoExtractor,
    "#pattern" : r"https://www.xasiat.com/get_file/19/413053af254d8dddac4a22f171a94408/118000/118556/118556_source.mp4/\?v-acctoken=\w+",

    "count"         : 1,
    "date"          : "dt:2026-05-11 10:09:45",
    "duration"      : 4479,
    "extension"     : "mp4",
    "filename"      : "118556_source",
    "format"        : "Best Quality",
    "height"        : 2160,
    "likes"         : range(1, 10),
    "model"         : [],
    "thumbnail"     : "https://pic.xascdn.li/contents/videos_screenshots/118000/118556/preview.jpg",
    "title"         : "4897531 50% OFF!♀217 Yuna, a 23-year-old with little experience, moans innocently as she savours sex—you’ll be able to jerk off to this at least 20 times ★ Uncensored as a bonus",
    "type"          : "video",
    "video_category": "JAV Uncensored",
    "video_id"      : 118556,
    "video_url"     : "https://www.xasiat.com/videos/118556/4897531-50-off-217-yuna-a-23-year-old-with-little-experience-moans-innocently-as-she-savours-sex-you-ll-be-able-to-jerk-off-to-this-at-least-20-times-uncensored-as-a-bonus/",
    "views"         : range(11_000, 20_000),
    "width"         : 3840,
    "tags"          : [
        "23-year-old",
        "Tiny Body",
        "Bonus",
    ],
},

{
    "#url"     : "https://www.xasiat.com/videos/95985/4745571-you-ll-love-it-no-pyjpqos-s-nakadashi-idol-faced-beauty-has-a-cute-voice-i-was-very-happy-with-her-shy-personality-or-shyness-bonus/",
    "#comment" : "'format' option",
    "#class"   : xasiat.XasiatVideoExtractor,
    "#options" : {"format": "sd"},
    "#pattern" : r"https://www.xasiat.com/get_file/17/64f4856d4bbc9b9d1d8f34e44bba71ab/95000/95985/95985.mp4/\?v-acctoken=\w+",

    "date"          : "dt:2025-08-26 08:10:05",
    "duration"      : 2203,
    "format"        : "SD",
},

)
