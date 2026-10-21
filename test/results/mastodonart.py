# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mastodon


__tests__ = (
{
    "#url"     : "https://mastodon.art/@clever_reports",
    "#category": ("mastodon", "mastodon.art", "user"),
    "#class"   : mastodon.MastodonUserExtractor,
    "#range"   : "1-60",
    "#count"   : 60,
},

{
    "#url"     : "https://mastodon.art/@GetCarter@mastodonapp.uk",
    "#category": ("mastodon", "mastodon.art", "user"),
    "#class"   : mastodon.MastodonUserExtractor,
},

{
    "#url"     : "https://mastodon.art/@id:10843",
    "#category": ("mastodon", "mastodon.art", "user"),
    "#class"   : mastodon.MastodonUserExtractor,
},

{
    "#url"     : "https://mastodon.art/users/id:10843",
    "#category": ("mastodon", "mastodon.art", "user"),
    "#class"   : mastodon.MastodonUserExtractor,
},

{
    "#url"     : "https://mastodon.art/users/clever_reports",
    "#category": ("mastodon", "mastodon.art", "user"),
    "#class"   : mastodon.MastodonUserExtractor,
},

{
    "#url"     : "https://mastodon.art/bookmarks",
    "#category": ("mastodon", "mastodon.art", "bookmark"),
    "#class"   : mastodon.MastodonBookmarkExtractor,
    "#auth"    : True,
},

{
    "#url"     : "https://mastodon.art/favourites",
    "#category": ("mastodon", "mastodon.art", "favorite"),
    "#class"   : mastodon.MastodonFavoriteExtractor,
    "#auth"    : True,
},

{
    "#url"     : "https://mastodon.art/lists/92653",
    "#category": ("mastodon", "mastodon.art", "list"),
    "#class"   : mastodon.MastodonListExtractor,
},

{
    "#url"     : "https://mastodon.art/tags/mastodon",
    "#category": ("mastodon", "mastodon.art", "hashtag"),
    "#class"   : mastodon.MastodonHashtagExtractor,
    "#auth"    : True,
    "#range"   : "1-10",
},

{
    "#url"     : "https://mastodon.art/@clever_reports/following",
    "#category": ("mastodon", "mastodon.art", "following"),
    "#class"   : mastodon.MastodonFollowingExtractor,
},

{
    "#url"     : "https://mastodon.art/@clever_reports/following",
    "#category": ("mastodon", "mastodon.art", "following"),
    "#class"   : mastodon.MastodonFollowingExtractor,
},

{
    "#url"     : "https://mastodon.art/users/id:10843/following",
    "#category": ("mastodon", "mastodon.art", "following"),
    "#class"   : mastodon.MastodonFollowingExtractor,
},

{
    "#url"     : "https://mastodon.art/@clever_reports/117340110905862635",
    "#category": ("mastodon", "mastodon.art", "status"),
    "#class"   : mastodon.MastodonStatusExtractor,
},

)
