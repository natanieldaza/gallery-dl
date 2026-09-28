# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import filester


__tests__ = (
{
    "#url"     : "https://filester.me/d/aPc9D5g",
    "#class"   : filester.FilesterFileExtractor,
    "#pattern" : r"https://\w+\.filester\.me/v2/7147825c-5216-4d2a-b126-0e98e0b58d13.png\?token=\w+\.\w{64}&download=true",

    "date"     : "dt:2026-03-06 00:00:00",
    "extension": "png",
    "filename" : """test-テスト-"&>""",
    "hash"     : "eb359cd8f02a7d6762f9863798297ff6a22569c5c87a9d38c55bdb3a3e26003f",
    "id"       : "aPc9D5g",
    "mime"     : "image/png",
    "size"     : "182 bytes",
    "uuid"     : "7147825c-5216-4d2a-b126-0e98e0b58d13",
},

{
    "#url"     : "https://filester.sh/d/aPc9D5g",
    "#class"   : filester.FilesterFileExtractor,
    "#pattern" : r"https://\w+\.filester\.me/v2/7147825c-5216-4d2a-b126-0e98e0b58d13.png\?token=\w+\.\w{64}&download=true",
},

{
    "#url"     : "https://filester.si/d/aPc9D5g",
    "#class"   : filester.FilesterFileExtractor,
    "#pattern" : r"https://\w+\.filester\.me/v2/7147825c-5216-4d2a-b126-0e98e0b58d13.png\?token=\w+\.\w{64}&download=true",
},

{
    "#url"     : "https://filester.gg/d/aPc9D5g",
    "#class"   : filester.FilesterFileExtractor,
    "#pattern" : r"https://\w+\.filester\.me/v2/7147825c-5216-4d2a-b126-0e98e0b58d13.png\?token=\w+\.\w{64}&download=true",
},

{
    "#url"     : "https://filester.me/f/1725bc5b793e8a4a",
    "#class"   : filester.FilesterFolderExtractor,
    "#pattern" : r"https://\w+\.filester\.me/v2/[^/?#]+\?token=\w+\.\w{64}&download=true",

    "count"      : 6,
    "num"        : range(1, 6),
    "date"       : "dt:2026-03-06 00:00:00",
    "extension"  : {"png", "mp4"},
    "filename"   : r"re:\d+_1",
    "folder_date": "dt:2026-03-06 00:00:00",
    "folder_id"  : "1725bc5b793e8a4a",
    "folder_name": '''"&>''',
    "folder_size": 194734,
    "folder_uuid": "iso:uuid",
    "id"         : r"re:\w+",
    "size"       : r"re:\d+",
    "uuid"       : "iso:uuid",
},

{
    "#url"     : "https://filester.me/f/60b41cbbd900ca35",
    "#comment" : "password-protected folder - no password (#467)",
    "#class"   : filester.FilesterFolderExtractor,
    "#exception": "AuthRequired",
},

{
    "#url"     : "https://filester.me/f/60b41cbbd900ca35",
    "#comment" : "password-protected folder - wrong password (#467)",
    "#class"   : filester.FilesterFolderExtractor,
    "#options"  : {"password": "foobar"},
    "#exception": "AuthorizationError",
},

{
    "#url"     : "https://filester.me/f/60b41cbbd900ca35",
    "#comment" : "password-protected folder - correct password (#467)",
    "#class"   : filester.FilesterFolderExtractor,
    "#options" : {"password": "abc123#?^DEF"},
    "#pattern" : (
        r"https://fsc\d+.cdn.cr/v2/33049bc6-36e6-4297-a107-37fcc8ba015b.jpg\?token=[0-9a-f.]+&download=true",
        r"https://fsc\d+.cdn.cr/v2/08730336-738d-4056-8dd4-964611c99d9f.jpg\?token=[0-9a-f.]+&download=true",
    ),
},

)
