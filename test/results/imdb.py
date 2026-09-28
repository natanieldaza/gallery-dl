# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imdb


__tests__ = (
{
    "#url"     : "https://www.imdb.com/title/tt0133093/mediaviewer/rm3470144001/?ref_=tt_ov_m_sm",
    "#class"   : imdb.ImdbTitleImagesExtractor,
    "#pattern" : r"https://m\.media\-amazon\.com/images/.+\.jpg",
    "#count"   : range(265, 400),

    "copyright": {str, None},
    "count"    : range(265, 400),
    "num"      : range(1, 400),
    "countries": list,
    "createdBy": {str, None},
    "extension": "jpg",
    "filename" : str,
    "width"    : range(180, 3840),
    "height"   : range(180, 3498),
    "id"       : r"re:rm\d+$",
    "languages": list,
    "status"   : "PUBLISHED",
    "title"    : "The Matrix",
    "titles"   : list,
    "type"     : {"still_frame", "event", "poster", "publicity", "behind_the_scenes", "product", "production_art"},
    "url"      : str,
    "year"     : 1999,
    "names"    : list,
    "caption"  : {
        "plaidHtml": str,
        "plainText": str,
    },
    "source"   : {
        "attributionUrl": {str, None},
        "banner"        : None,
        "id"            : {str, None},
        "text"          : {str, None},
    },
},

{
    "#url"     : "https://www.imdb.com/name/nm0323822/mediaviewer/rm38177793/?ref_=nm_ov_m_sm",
    "#class"   : imdb.ImdbNameImagesExtractor,
    "#results" : (
        "https://m.media-amazon.com/images/M/MV5BZDJkMzNiMTEtODdhNS00N2QxLTg4NmItNzlkZWZmYTJiNmI1XkEyXkFqcGc@._V1_.jpg",
        "https://m.media-amazon.com/images/M/MV5BZWU1NGY2MTgtMThmZC00ZjFiLTk4MDYtODJhYTEyOGU3YWRhXkEyXkFqcGc@._V1_.jpg",
        "https://m.media-amazon.com/images/M/MV5BMjM1MjIxNzY1OV5BMl5BanBnXkFtZTgwNjA4MzU1MjE@._V1_.jpg",
        "https://m.media-amazon.com/images/M/MV5BMjAxNTMwNjAxMl5BMl5BanBnXkFtZTgwNjQ3MzU1MjE@._V1_.jpg",
        "https://m.media-amazon.com/images/M/MV5BMTkwNzc4Mzc1NV5BMl5BanBnXkFtZTgwMTc2MzU1MjE@._V1_.jpg",
        "https://m.media-amazon.com/images/M/MV5BMTc1MTIyMTI5OV5BMl5BanBnXkFtZTcwMTc4OTkwOA@@._V1_.jpg",
        "https://m.media-amazon.com/images/M/MV5BMTI0Nzg1OTc0MV5BMl5BanBnXkFtZTcwNTU4NzYzMQ@@._V1_.jpg",
    ),

    "copyright": {str, None},
    "count"    : 7,
    "num"      : range(1, 7),
    "countries": [],
    "createdBy": {str, None},
    "extension": "jpg",
    "filename" : str,
    "width"    : range(200, 1340),
    "height"   : range(200, 2048),
    "id"       : r"re:rm\d+$",
    "languages": [],
    "name"     : "Paul Goddard",
    "titles"   : list,
    "type"     : {"still_frame", "product"},
    "url"      : str,
    "names"    : list,
    "caption"  : {
        "plaidHtml": str,
        "plainText": str,
    },
    "source"   : {
        "attributionUrl": {str, None},
        "banner"        : None,
        "id"            : {"userupload", "amazon", "getty"},
        "text"          : {str, None},
    },
},

)
