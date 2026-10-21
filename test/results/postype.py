# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import postype


__tests__ = (
{
    "#url"     : "https://www.postype.com/@miragestar602/post/21436111",
    "#class"   : postype.PostypePostExtractor,
    "#results" : "https://d2ufj6gm1gtdrc.cloudfront.net/2026/01/23/14/22/d1d1de1425262513340277225.png",

    "activeExhibitCollectionId": None,
    "adult"           : False,
    "allowAnonymousSupport": True,
    "anonymousSupport": False,
    "comments"        : 3,
    "count"           : 1,
    "date"            : "dt:2026-01-23 05:23:20",
    "editorVersion"   : "V5",
    "extension"       : "png",
    "filename"        : "d1d1de1425262513340277225",
    "firstPublishedAt": 1769145800,
    "hasMembership"   : False,
    "hasThumbnail"    : True,
    "height"          : 3000,
    "id"              : 21436111,
    "isForever"       : True,
    "liked"           : False,
    "likes"           : range(35, 200),
    "muteType"        : "POSTYPE",
    "num"             : 1,
    "post_id"         : 21436111,
    "price"           : 0,
    "publicOption"    : "PUBLIC",
    "publishedAt"     : 1769145800,
    "purchased"       : False,
    "quoteCount"      : 0,
    "quoteItem"       : None,
    "repostCount"     : 0,
    "scrapped"        : False,
    "shortUrl"        : "https://posty.pe/shh0ep",
    "subTitle"        : "푸른 상자 팬아트",
    "subType"         : "NORMAL",
    "summary"         : "",
    "thumbnail"       : "https://d3mcojo3jv0dbr.cloudfront.net/2026/01/23/14/22/d1d1de1425262513340277225.png",
    "title"           : "이 말을 하기로 결심한 건",
    "url"             : "https://d2ufj6gm1gtdrc.cloudfront.net/2026/01/23/14/22/d1d1de1425262513340277225.png",
    "views"           : None,
    "visibilityOption": "FREE",
    "width"           : 2000,
    "tags"            : [
        "푸른상자",
        "히나",
    ],
    "author"          : {
        "visibility": "ACTIVE",
        "profile"   : {
            "hash"     : "2j1svl",
            "nickname" : "미라주",
            "profileId": 2851853,
            "thumbnail": str,
        },
    },
    "channel"         : {
        "activeMembership": False,
        "allowAnonymousSupport": True,
        "allowedChannelNotification": False,
        "blockShare"      : False,
        "blocked"         : False,
        "channelId"       : 1417902,
        "channelTypeGroup": "NORMAL",
        "id"              : 1417902,
        "isForever"       : True,
        "joinedMembership": False,
        "name"            : "miragestar602",
        "profileId"       : 2851853,
        "role"            : None,
        "subscribed"      : False,
        "subscriberCount" : range(8000, 20000),
        "thumbnail"       : "https://d33pksfia2a94m.cloudfront.net/assets/img/avatar/blog_blank.png",
        "title"           : "미라주",
        "type"            : "BASIC",
    },
    "profile"         : {
        "bio"          : "주로 순애물을 그려서 올립니다. 외주나 기타 문의 : steven0602@naver.com",
        "hash"         : "2j1svl",
        "id"           : 2851853,
        "nickname"     : "미라주",
        "thumbnail"    : str,
        "useMessage"   : True,
        "userProfileId": 2851853,
    },
    "series"          : {
        "id"       : 1030652,
        "postCount": range(190, 300),
        "seriesId" : 1030652,
        "title"    : "종합장",
    },
},

{
    "#url"     : "https://www.postype.com/en/@sanoonsnowfield/post/21587023",
    "#comment" : "URL with ISO 639 language code",
    "#class"   : postype.PostypePostExtractor,
},

{
    "#url"     : "https://www.postype.com/@myosi-15/post/23058789",
    "#comment" : "'.zip' file download (gh#9788)",
    "#class"   : postype.PostypePostExtractor,
    "#pattern" : (
        r"https://\w+.cloudfront.net/2026/08/29/20/06/b08aae2509800520257249154.gif",
        r"https://\w+.cloudfront.net/2026/08/29/20/06/2a69b212545112078901861048.zip\?filename=%EC%B5%9C_images.zip&Expires=\d+&Signature=.+",
        r"https://\w+.cloudfront.net/2026/08/29/20/07/7601ce2207923886135567857.gif",
    ),
},

{
    "#url"     : "https://www.postype.com/@miragestar602",
    "#class"   : postype.PostypeChannelExtractor,
    "#pattern" : r"https://d2ufj6gm1gtdrc\.cloudfront\.net/[^?]+$",
    "#range"   : "1-3",
    "#count"   : 3,
},
)
