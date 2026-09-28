# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import steamcommunity


__tests__ = (
{
    "#url"     : "https://steamcommunity.com/sharedfiles/filedetails/?id=296316110",
    "#class"   : steamcommunity.SteamcommunitySharedfileExtractor,
    "#results" : "https://images.steamusercontent.com/ugc/567770337564660542/8552FC9551546163E36D29B0512097A7084C8B1B/",

    "content_type": "screenshots",
    "creator"     : "GiovanH",
    "creator_id"  : "giovanh",
    "date"        : "dt:2014-08-05 09:29:00",
    "description" : "",
    "extension"   : "jpg",
    "file_id"     : "296316110",
    "game"        : "The Stanley Parable",
    "game_appid"  : "221910",
    "width"       : 1366,
    "height"      : 768,
    "likes"       : int,
    "size"        : 177209,
    "title"       : "",
    "ugc_id"      : "567770337564660542/8552FC9551546163E36D29B0512097A7084C8B1B",
    "url"         : "https://steamcommunity.com/sharedfiles/filedetails/?id=296316110",
    "views"       : range(5, 99),
},

{
    "#url"     : "https://steamcommunity.com/sharedfiles/filedetails/?id=2667137268",
    "#class"   : steamcommunity.SteamcommunitySharedfileExtractor,
    "#results" : "https://images.steamusercontent.com/ugc/1839154007536501034/6478074127CCBB03226274B8035FD607B9DA0673/",

    "content_type": "artwork",
    "creator"     : "SomewhatTolerable",
    "creator_id"  : "76561199186562768",
    "date"        : "dt:2021-11-28 07:06:00",
    "description" : "",
    "extension"   : "jpg",
    "file_id"     : "2667137268",
    "game"        : "The Beginner's Guide",
    "game_appid"  : "303210",
    "width"       : 1472,
    "height"      : 1667,
    "likes"       : range(2, 50),
    "size"        : 1080033,
    "title"       : "Escape",
    "ugc_id"      : "1839154007536501034/6478074127CCBB03226274B8035FD607B9DA0673",
    "url"         : "https://steamcommunity.com/sharedfiles/filedetails/?id=2667137268",
    "views"       : range(80, 999),
},

{
    "#url"     : "https://steamcommunity.com/sharedfiles/filedetails/?id=3802119206",
    "#class"   : steamcommunity.SteamcommunitySharedfileExtractor,
    "#results" : "https://images.steamusercontent.com/ugc/9795036510357212076/940E21074F339522F872FA09280AC9FB7A6797AC/",

    "content_type": "artwork",
    "creator"     : "76561198118687531",
    "creator_id"  : "mz007",
    "date"        : "dt:2026-09-15 06:37:00",
    "description" : """ТУН ТУН САХУР, ПИНГВИНЫ ИЗ МАДАГАСКАРА, Т-34 И Т.Д.\r\nСкопируй в консоль CS2:\r\n[code]connect 45.95.31.104:27315[/code]""",
    "extension"   : "jpg",
    "file_id"     : "3802119206",
    "game"        : "Counter-Strike 2",
    "game_appid"  : "730",
    "width"       : 1280,
    "height"      : 1024,
    "likes"       : range(25, 200),
    "size"        : 179306,
    "title"       : "СЕРВЕР С РАНДОМНЫМИ МОДЕЛЬКАМИ",
    "ugc_id"      : "9795036510357212076/940E21074F339522F872FA09280AC9FB7A6797AC",
    "url"         : "https://steamcommunity.com/sharedfiles/filedetails/?id=3802119206",
    "views"       : range(3000, 20000),
},

)
