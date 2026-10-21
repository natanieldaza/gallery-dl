# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

gallery_dl = __import__("gallery_dl.extractor.8muses")
_8muses = getattr(gallery_dl.extractor, "8muses")


__tests__ = (
{
    "#url"     : "https://comics.8muses.com/porn/album/MCC-Comics",
    "#class"   : _8muses._8musesAlbumExtractor,
    "#pattern" : _8muses._8musesAlbumExtractor.pattern,
    "#count"   : range(180, 500),

    "name"   : str,
    "private": False,
    "url"    : str,
},

{
    "#url"     : "https://comics.8muses.com/comics/album/Various-Authors/Chessire88/From-Trainers-to-Pokmons",
    "#comment" : "non-ASCII characters",
    "#class"   : _8muses._8musesAlbumExtractor,
    "#exception": "HttpError",
},

{
    "#url"     : "https://comics.8muses.com/comics/album/Tufos-Comics/Gallery",
    "#comment" : "private albums without 'permalink' (#6717)",
    "#class"   : _8muses._8musesAlbumExtractor,
    "#count"   : range(100, 150),
},

{
    "#url"     : "https://comics.8muses.com/comics/album/Various-Authors/JankinGen",
    "#class"   : _8muses._8musesAlbumExtractor,
    "#results" : "https://comics.8muses.com/porn/album/Various-Authors/JankinGen/Princess-Laura-Sex-Adventure",

    "name"   : "Princess Laura Sex Adventure",
    "private": False,
    "url"    : "https://comics.8muses.com/porn/album/Various-Authors/JankinGen/Princess-Laura-Sex-Adventure",
},

{
    "#url"     : "https://comics.8muses.com/comics/album/Various-Authors/JankinGen/Princess-Laura-Sex-Adventure/Issue-1",
    "#class"   : _8muses._8musesAlbumExtractor,
    "#pattern" : "https://comics.8muses.com/image/fl/.+",
    "#count"   : 8,

    "count"    : 8,
    "page"     : range(1, 8),
    "extension": "jpg",
    "hash"     : str,
    "url"      : r"re:https://comics.8muses.com/image/fl/.+",
    "album"    : {
        "date"   : "dt:2018-07-10 00:00:00",
        "id"     : 21159,
        "likes"  : 0,
        "parent" : 21158,
        "private": False,
        "title"  : "Issue 1",
        "url"    : "https://comics.8muses.com/porn/album/Various-Authors/JankinGen/Princess-Laura-Sex-Adventure/Issue-1",
        "views"  : range(60_000, 200_000),
        "path"   : [
            "Various Authors",
            "JankinGen",
            "Princess Laura Sex Adventure",
            "Issue 1",
        ],
    },
},

)
