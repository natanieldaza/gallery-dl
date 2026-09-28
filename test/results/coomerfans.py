# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import coomerfans

__tests__ = (
{
    "#url"     : "https://coomerfans.com/p/84930879/350442/onlyfans",
    "#comment" : "1 image",
    "#class"   : coomerfans.CoomerfansPostExtractor,
    "#pattern" : r"https://img\d+.coomerfans.com/storage/1/vd/gr/2892ac-0197737a-f8a5-72ed-a961-bbd8891479b7.jpg",

    "content"  : "IT'S HERE!!! 😏😏Thank you, for all donations❤️❤️The exclusive video (for all who donated) will be ready by the end of the next week 😘😘",
    "count"    : 1,
    "date"     : "dt:2025-06-12 10:33:29",
    "extension": "jpg",
    "filename" : "2892ac-0197737a-f8a5-72ed-a961-bbd8891479b7",
    "hash"     : "2892ac-0197737a-f8a5-72ed-a961-bbd8891479b7",
    "id"       : 84930879,
    "num"      : 1,
    "post_url" : "https://coomerfans.com/p/84930879/350442/onlyfans",
    "service"  : "onlyfans",
    "title"    : "IT'S HERE!!! 😏😏Thank you, for all donations❤️❤️The exclusive..",
    "type"     : "image",
    "user"     : 350442,
    "username" : "evekozi",
},

{
    "#url"     : "https://coomerfans.com/p/84930883/350442/onlyfans",
    "#comment" : "3 images",
    "#class"   : coomerfans.CoomerfansPostExtractor,
    "#pattern" : (
        r"https://img\d+.coomerfans.com/storage/1/ce/jr/2892ac-0197737a-f8c7-7f87-ab2c-621c49f67e2e.jpg",
        r"https://img\d+.coomerfans.com/storage/1/oq/sm/2892ac-0197737a-f8c9-7954-8b57-5ea9790bbf89.jpg",
        r"https://img\d+.coomerfans.com/storage/1/px/aa/2892ac-0197737a-f8ce-7895-82df-62878d41930b.jpg",
    ),

    "content"  : "Do you have any cream for my tits?💦💦",
    "count"    : 3,
    "num"      : range(1, 3),
    "date"     : "dt:2025-06-09 10:20:01",
    "extension": "jpg",
    "filename" : "iso:uuid",
    "hash"     : "iso:uuid",
    "id"       : 84930883,
    "post_url" : "https://coomerfans.com/p/84930883/350442/onlyfans",
    "service"  : "onlyfans",
    "title"    : "Do you have any cream for my tits?💦💦",
    "type"     : "image",
    "user"     : 350442,
    "username" : "evekozi",
},

{
    "#url"     : "https://coomerfans.com/p/41900211/279276/onlyfans",
    "#comment" : "2 videos",
    "#class"   : coomerfans.CoomerfansPostExtractor,
    "#pattern" : (
        r"https://img\d+.coomerfans.com/storage/7/eg/op/2892ac-0197c0a8-f38c-7a47-9fb6-c67d3adfbb0a.m4v\?e=\d+&hash=[\w-]+",
        r"https://img\d+.coomerfans.com/storage/7/kf/ea/2892ac-0197c0a8-f3ae-7e5b-bf06-87acee40a232.m4v\?e=\d+&hash=[\w-]+",
    ),

    "content"  : "Freshly shaved 🍑✨",
    "count"    : 2,
    "date"     : "dt:2022-08-26 12:18:24",
    "extension": "m4v",
    "id"       : 41900211,
    "post_url" : "https://coomerfans.com/p/41900211/279276/onlyfans",
    "service"  : "onlyfans",
    "title"    : "Freshly shaved 🍑✨",
    "type"     : "video",
    "user"     : 279276,
    "username" : "eliza.nicy",
},

{
    "#url"     : "https://coomerfans.com/u/onlyfans/226845/lenaslittlesecret",
    "#class"   : coomerfans.CoomerfansCreatorExtractor,
    "#pattern" : coomerfans.CoomerfansPostExtractor.pattern,
    "#count"   : 150,
},

{
    "#url"     : "https://coomerfans.com/u/fansly/346390/Blue_Rose8900?page=12",
    "#class"   : coomerfans.CoomerfansCreatorExtractor,
    "#pattern" : coomerfans.CoomerfansPostExtractor.pattern,
    "#count"   : 14,
},

)
