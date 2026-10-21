# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import pornhub
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://www.pornhub.com/album/19289801",
    "#class"   : pornhub.PornhubGalleryExtractor,
    "#pattern" : r"https://\w+.phncdn.com/pics/albums/\d+/\d+/\d+/\d+/",
    "#count"   : ">= 300",

    "id"     : int,
    "num"    : int,
    "score"  : int,
    "views"  : int,
    "caption": str,
    "user"   : "Danika Mori",
    "gallery": {
        "id"   : 19289801,
        "score": int,
        "views": int,
        "tags" : list,
        "title": "Danika Mori Best Moments",
    },
},

{
    "#url"     : "https://www.pornhub.com/album/69606532",
    "#comment" : "KeyError due to missing image entry (#6299)",
    "#class"   : pornhub.PornhubGalleryExtractor,
    "#log"     : "69606532: Unable to ensure correct file order",
    "#count"   : 6,
},

{
    "#url"     : "https://www.pornhub.com/album/69040172",
    "#comment" : "404 Error Page Not Found",
    "#class"   : pornhub.PornhubGalleryExtractor,
    "#exception": exception.HttpError,
},

{
    "#url"     : "https://www.pornhub.com/gif/43726891",
    "#class"   : pornhub.PornhubGifExtractor,
    "#pattern" : r"https://\w+\.phncdn\.com/pics/gifs/043/726/891/43726891a\.webm",

    "date"     : "dt:2023-04-20 00:00:00",
    "extension": "webm",
    "filename" : "43726891a",
    "id"       : "43726891",
    "tags"     : [
        "sloppy deepthroat",
        "perfect body",
        "petite brunette",
        "mouth fuck",
        "big dick",
        "natural big tits",
        "deepthroat swallow",
        "amateur couple",
        "homemade",
        "girls wanking boys",
        "hardcore sex",
        "babes 18 year",
    ],
    "timestamp": "5:07",
    "title"    : "Intense sloppy blowjob of Danika Mori",
    "url"      : "https://el.phncdn.com/pics/gifs/043/726/891/43726891a.webm",
    "user"     : "Danika Mori",
    "viewkey"  : "64367c8c78a4a",
},

{
    "#url"     : "https://www.pornhub.com/pornstar/danika-mori",
    "#class"   : pornhub.PornhubUserExtractor,
},

{
    "#url"     : "https://www.pornhub.com/model/hentai-apples-japan",
    "#class"   : pornhub.PornhubUserExtractor,
    "#results" : "https://www.pornhub.com/model/hentai-apples-japan/photos",
},

{
    "#url"     : "https://www.pornhub.com/model/hentai-apples-japan",
    "#class"   : pornhub.PornhubUserExtractor,
    "#options" : {"include": "all"},
    "#results" : (
        "https://www.pornhub.com/model/hentai-apples-japan/avatar",
        "https://www.pornhub.com/model/hentai-apples-japan/background",
        "https://www.pornhub.com/model/hentai-apples-japan/photos",
        "https://www.pornhub.com/model/hentai-apples-japan/gifs",
    ),
},

{
    "#url"     : "https://www.pornhub.com/pornstar/danika-mori/photos",
    "#class"   : pornhub.PornhubPhotosExtractor,
    "#pattern" : pornhub.PornhubGalleryExtractor.pattern,
    "#count"   : ">= 6",
},

{
    "#url"     : "https://www.pornhub.com/users/flyings0l0/photos/public",
    "#class"   : pornhub.PornhubPhotosExtractor,
},

{
    "#url"     : "https://www.pornhub.com/users/flyings0l0/photos/private",
    "#class"   : pornhub.PornhubPhotosExtractor,
},

{
    "#url"     : "https://www.pornhub.com/users/flyings0l0/photos/favorites",
    "#class"   : pornhub.PornhubPhotosExtractor,
},

{
    "#url"     : "https://www.pornhub.com/model/bossgirl/photos",
    "#class"   : pornhub.PornhubPhotosExtractor,
},

{
    "#url"     : "https://www.pornhub.com/pornstar/danika-mori/gifs",
    "#class"   : pornhub.PornhubGifsExtractor,
    "#pattern" : pornhub.PornhubGifExtractor.pattern,
    "#count"   : ">= 30",
},

{
    "#url"     : "https://www.pornhub.com/users/flyings0l0/gifs",
    "#class"   : pornhub.PornhubGifsExtractor,
},

{
    "#url"     : "https://www.pornhub.com/model/bossgirl/gifs/video",
    "#class"   : pornhub.PornhubGifsExtractor,
},

{
    "#url"     : "https://www.pornhub.com/channels/mr-lucky-raw/avatar",
    "#category": ("", "pornhub", "avatar"),
    "#class"   : pornhub.PornhubAssetExtractor,
    "#results" : "https://ei.phncdn.com/(m=eidYGe)(mh=yBQyfFBdshg1aUyz)afd69add-fbf3-452a-8f08-2d142f0dd834.jpg",

    "extension": "jpg",
    "id"       : "afd69add-fbf3-452a-8f08-2d142f0dd834",
    "type"     : "avatar",
    "user"     : "Mr Lucky RAW",
},

{
    "#url"     : "https://www.pornhub.com/model/hentai-apples-japan/avatar",
    "#category": ("", "pornhub", "avatar"),
    "#class"   : pornhub.PornhubAssetExtractor,
    "#results" : "https://ei.phncdn.com/pics/users/0027/8094/6171/avatar95278345/(m=ewILGCjadOf)(mh=lQ9SznzdRpxbFxzs)200x200.jpg",

    "extension": "jpg",
    "id"       : "95278345",
    "type"     : "avatar",
    "user"     : "HENTAI Apples JAPAN",
},

{
    "#url"     : "https://www.pornhub.com/model/hentai-apples-japan/background",
    "#category": ("", "pornhub", "background"),
    "#class"   : pornhub.PornhubAssetExtractor,
    "#results" : "https://ei.phncdn.com/pics/users/0027/8094/6171/cover30133675/(m=eRSa4qFxcWaAb)(mh=BoKH7T_JjYcLmlgf)1323x270.jpg",

    "extension": "jpg",
    "id"       : "30133675",
    "type"     : "background",
    "user"     : "HENTAI Apples JAPAN",
},

)
