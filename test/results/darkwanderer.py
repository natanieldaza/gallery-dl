# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import xenforo


__tests__ = (
{
    "#url"     : "https://darkwanderer.net/threads/thanks-for-this-topic.16028/post-56859",
    "#category": ("xenforo", "darkwanderer", "post"),
    "#class"   : xenforo.XenforoPostExtractor,
    "#results" : (
        "https://darkwanderer.net/attachments/1697595291587-png.334103/",
        "https://darkwanderer.net/attachments/1697595441962-png.334104/",
        "https://darkwanderer.net/attachments/1697595478453-png.334105/",
    ),

    "count"       : 3,
    "extension"   : "png",
    "id"          : int,
    "num"         : int,
    "num_external": 0,
    "num_internal": int,
    "type"        : "inline",
    "post"        : {
        "attachments": "",
        "author"     : "Prata0180",
        "author_id"  : "14960",
        "author_slug": "prata0180",
        "author_url" : "https://darkwanderer.net/members/prata0180.14960/",
        "count"      : 3,
        "date"       : "dt:2023-10-18 02:18:35",
        "id"         : "56859",
    },
    "thread"      : {
        "author"     : "gw3n",
        "author_id"  : "9151",
        "author_slug": "gw3n",
        "author_url" : "https://darkwanderer.net/members/gw3n.9151/",
        "date"       : "dt:2021-08-25 10:26:35",
        "id"         : "16028",
        "posts"      : 11,
        "section"    : "Reverse Interracial",
        "tags"       : (),
        "title"      : "Thanks for this topic.",
        "url"        : "https://darkwanderer.net/threads/thanks-for-this-topic.16028/",
        "views"      : int,
        "path"       : [
            "Cuckold / Interracial Pics and Videos",
            "Reverse Interracial",
        ],
    },
},

{
    "#url"     : "https://darkwanderer.net/threads/thanks-for-this-topic.16028/",
    "#category": ("xenforo", "darkwanderer", "thread"),
    "#class"   : xenforo.XenforoThreadExtractor,
    "#pattern" : r"https://darkwanderer\.net/attachments/.+",
    "#count"   : 11,

    "count"       : int,
    "id"          : int,
    "thread"      : {
        "author"     : "gw3n",
        "id"         : "16028",
        "title"      : "Thanks for this topic.",
    },
},

{
    "#url"     : "https://darkwanderer.net/forums/off-topic.42/",
    "#category": ("xenforo", "darkwanderer", "forum"),
    "#class"   : xenforo.XenforoForumExtractor,
    "#pattern" : xenforo.XenforoThreadExtractor.pattern,
    "#count"   : range(50, 90),
},

)
