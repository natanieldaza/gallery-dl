# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import toyhouse


__tests__ = (
{
    "#url"     : "https://www.toyhou.se/d-floe/art",
    "#class"   : toyhouse.ToyhouseArtExtractor,
    "#pattern" : r"https://f\d+\.toyhou\.se/file/f\d+-toyhou-se/images/\d+_\w+\.\w+$",
    "#range"   : "1-30",
    "#count"   : 30,

    "artists"   : list,
    "characters": list,
    "date"      : "type:datetime",
    "hash"      : r"re:\w+",
    "id"        : r"re:\d+",
    "url"       : str,
    "user"      : "d-floe",
},

{
    "#url"     : "https://www.toyhou.se/kroksoc/art",
    "#comment" : "protected by Content Warning",
    "#class"   : toyhouse.ToyhouseArtExtractor,
    "#count"   : range(15, 20),
},

{
    "#url"     : "https://toyhou.se/~images/40587320",
    "#class"   : toyhouse.ToyhouseImageExtractor,
    "#sha1_content": "058ec8427977ab432c4cc5be5a6dd39ce18713ef",

    "artists"   : ["d-floe"],
    "characters": ["Sumi"],
    "date"      : "dt:2021-10-08 01:32:47",
    "extension" : "png",
    "filename"  : "40587320_TT1NaBUr3FLkS1p",
    "hash"      : "TT1NaBUr3FLkS1p",
    "id"        : "40587320",
    "url"       : "https://f2.toyhou.se/file/f2-toyhou-se/images/40587320_TT1NaBUr3FLkS1p.png",
},

{
    "#url"     : "https://f2.toyhou.se/file/f2-toyhou-se/images/77522898_kFSr5TtpmymWBip.png",
    "#comment" : "direct link, multiple artists, 'Content Warning'",
    "#class"   : toyhouse.ToyhouseImageExtractor,
    "#results" : "https://f2.toyhou.se/file/f2-toyhou-se/images/77522898_kFSr5TtpmymWBip.png",
    "#log"     : "Accepting 'Content Warning'",

    "character"     : "Cada",
    "character_id"  : "23067343",
    "character_slug": "cada",
    "characters"    : ["Cada (main forms)"],
    "date"          : "dt:2024-02-10 16:30:14",
    "detail"        : "love this smi base. me and my best friend fr",
    "display_name"  : "cadaverine",
    "extension"     : "png",
    "filename"      : "77522898_kFSr5TtpmymWBip",
    "folder"        : "Ø ꜰᴀɴᴅᴏᴍꜱ/ʀᴇʟᴀᴛᴇᴅ",
    "folder_id"     : "2506744",
    "hash"          : "kFSr5TtpmymWBip",
    "id"            : "77522898",
    "status"        : "original",
    "url"           : "https://f2.toyhou.se/file/f2-toyhou-se/images/77522898_kFSr5TtpmymWBip.png",
    "user"          : "cadaverine",
    "artists"       : [
        "Smiggles base used (Base)",
        "cadaverine (Edits)",
    ],
},

{
    "#url"     : "https://f2.toyhou.se/file/f2-toyhou-se/watermarks/36817425_bqhGcwcnU.png?1625561467",
    "#comment" : "direct link, multiple artists",
    "#class"   : toyhouse.ToyhouseImageExtractor,
    "#exception": "HttpError",

    "artists"   : [
        "http://aminoapps.com/p/92sf3z",
        "kroksoc (Color)",
    ],
    "characters" : ["Reiichi❀"],
    "date"       : "dt:2021-07-03 20:02:02",
    "detail"     : "",
    "hash"       : "bqhGcwcnU",
    "id"         : "36817425",
    "status"     : "original",
},

{
    "#url"     : "https://f2.toyhou.se/file/f2-toyhou-se/images/40587320_TT1NaBUr3FLkS1p.png",
    "#class"   : toyhouse.ToyhouseImageExtractor,
},

{
    "#url"     : "https://toyhou.se/~images/90697482",
    "#comment" : "multiple characters",
    "#class"   : toyhouse.ToyhouseImageExtractor,
    "#results" : "https://f2.toyhou.se/file/f2-toyhou-se/images/90697482_ohVDjxWjeepj3LC.png",

    "artists"   : ["d-floe"],
    "date"      : "dt:2024-11-01 20:43:46",
    "extension" : "png",
    "filename"  : "90697482_ohVDjxWjeepj3LC",
    "hash"      : "ohVDjxWjeepj3LC",
    "id"        : "90697482",
    "url"       : "https://f2.toyhou.se/file/f2-toyhou-se/images/90697482_ohVDjxWjeepj3LC.png",
    "characters": [
        "Ash",
        "Sumi",
    ],
},

{
    "#url"     : "https://toyhou.se/~images/93386749",
    "#class"   : toyhouse.ToyhouseImageExtractor,
    "#results" : "https://f2.toyhou.se/file/f2-toyhou-se/watermarks/93386749_SjnbSIamQ.png",

    "artists"   : ["NowhereMotel"],
    "date"      : "dt:2024-12-29 21:54:01",
    "detail"    : "Dog band",
    "extension" : "png",
    "filename"  : "93386749_SjnbSIamQ",
    "hash"      : "SjnbSIamQ",
    "id"        : "93386749",
    "status"    : "watermark",
    "characters": [
        "Reed",
        "Ferris",
        "Danny",
        "Shiba",
    ],
},

{
    "#url"     : "https://f2.toyhou.se/file/f2-toyhou-se/thumbnails/98266697_jGT.png",
    "#comment" : "thumbnail",
    "#class"   : toyhouse.ToyhouseImageExtractor,
    "#results" : "https://f2.toyhou.se/file/f2-toyhou-se/thumbnails/98266697_jGT.png",

    "artists"   : ["NowhereMotel"],
    "characters": ["KitKat"],
    "date"      : "dt:2025-04-03 20:38:27",
    "detail"    : "0",
    "extension" : "png",
    "filename"  : "98266697_jGT",
    "hash"      : "jGT",
    "id"        : "98266697",
    "status"    : "thumbnail",
},

{
    "#url"     : "https://toyhou.se/9867694.reed/93386749",
    "#class"   : toyhouse.ToyhouseImageExtractor,
},

{
    "#url"     : "https://toyhou.se/2496602.styx/5896823.humanoid/63604940",
    "#comment" : "sub/variant URL",
    "#class"   : toyhouse.ToyhouseImageExtractor,
    "#results" : "https://f2.toyhou.se/file/f2-toyhou-se/images/63604940_M50adCZAxy9MYaV.jpg",

    "artists"       : ["doktor monty", "cadaverine"],
    "character"     : "Styx",
    "character_id"  : "2496602",
    "character_slug": "styx",
    "characters"    : ["Styx (Humanoid)"],
    "date"          : "dt:2023-04-11 12:20:51",
    "detail"        : "older oekaki art :)",
    "display_name"  : "cadaverine",
    "extension"     : "jpg",
    "filename"      : "63604940_M50adCZAxy9MYaV",
    "folder"        : "ѳ ғʟɪɢʜᴛ ʀɪsɪɴɢ",
    "folder_id"     : "498796",
    "hash"          : "M50adCZAxy9MYaV",
    "id"            : "63604940",
    "status"        : "original",
    "url"           : "https://f2.toyhou.se/file/f2-toyhou-se/images/63604940_M50adCZAxy9MYaV.jpg",
    "user"          : "cadaverine",
    "variant_id"    : "5896823",
    "variant_slug"  : "humanoid",
},

{
    "#url"     : "https://toyhou.se/1824619.apricot/gallery",
    "#class"   : toyhouse.ToyhouseCharacterGalleryExtractor,
    "#pattern" : r"https://(f2\.toyhou\.se/file/f2\-toyhou\-se|file\.toyhou\.se)/images/\d+_\w+\.(jpg|png|gif)",
    "#count"   : 129,

    "character"     : "Apricot",
    "character_id"  : "1824619",
    "character_slug": "apricot",
    "date"          : "type:datetime",
    "extension"     : {"jpg", "png", "gif"},
    "status"        : "original",
    "user"          : "d-floe",
},

{
    "#url"     : "https://toyhou.se/9869607.the-carnelian/27007593.cinna/gallery",
    "#comment" : "character tab page (#493)",
    "#class"   : toyhouse.ToyhouseCharacterGalleryExtractor,
    "#results" : "https://f2.toyhou.se/file/f2-toyhou-se/images/81260655_zKy4ABYvKzDecY4.png",

    "artists"       : ["darkvvision"],
    "character"     : "THE CARNELIAN",
    "characters"    : ["THE CARNELIAN (CINNA)"],
    "character_id"  : "9869607",
    "character_slug": "the-carnelian",
    "date"          : "dt:2024-04-27 23:13:42",
    "detail"        : "0",
    "display_name"  : "nun",
    "extension"     : "png",
    "filename"      : "81260655_zKy4ABYvKzDecY4",
    "folder"        : "CINNAS",
    "folder_id"     : "5449272",
    "hash"          : "zKy4ABYvKzDecY4",
    "id"            : "81260655",
    "status"        : "original",
    "tab"           : "CINNA",
    "tab_id"        : "27007593",
    "tab_slug"      : "cinna",
    "url"           : "https://f2.toyhou.se/file/f2-toyhou-se/images/81260655_zKy4ABYvKzDecY4.png",
    "user"          : "nun",
},

{
    "#url"     : "https://toyhou.se/9869607.foo/27007593./gallery",
    "#class"   : toyhouse.ToyhouseCharacterGalleryExtractor,
},

)
