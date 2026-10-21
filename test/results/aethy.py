# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import mastodon


__tests__ = (
{
    "#url"     : "https://aethy.com/@InvaderNos",
    "#category": ("mastodon", "aethy", "user"),
    "#class"   : mastodon.MastodonUserExtractor,
    "#range"   : "1-60",
    "#count"   : 60,
},

{
    "#url"     : "https://aethy.com/@kitagawa_sui@misskey.io",
    "#category": ("mastodon", "aethy", "user"),
    "#class"   : mastodon.MastodonUserExtractor,
},

{
    "#url"     : "https://aethy.com/@id:10843",
    "#category": ("mastodon", "aethy", "user"),
    "#class"   : mastodon.MastodonUserExtractor,
},

{
    "#url"     : "https://aethy.com/users/id:10843",
    "#category": ("mastodon", "aethy", "user"),
    "#class"   : mastodon.MastodonUserExtractor,
},

{
    "#url"     : "https://aethy.com/users/InvaderNos",
    "#category": ("mastodon", "aethy", "user"),
    "#class"   : mastodon.MastodonUserExtractor,
},

{
    "#url"     : "https://aethy.com/bookmarks",
    "#category": ("mastodon", "aethy", "bookmark"),
    "#class"   : mastodon.MastodonBookmarkExtractor,
    "#auth"    : True,
},

{
    "#url"     : "https://aethy.com/favourites",
    "#category": ("mastodon", "aethy", "favorite"),
    "#class"   : mastodon.MastodonFavoriteExtractor,
    "#auth"    : True,
},

{
    "#url"     : "https://aethy.com/lists/92653",
    "#category": ("mastodon", "aethy", "list"),
    "#class"   : mastodon.MastodonListExtractor,
},

{
    "#url"     : "https://aethy.com/tags/mastodon",
    "#category": ("mastodon", "aethy", "hashtag"),
    "#class"   : mastodon.MastodonHashtagExtractor,
    "#auth"    : True,
    "#range"   : "1-10",
},

{
    "#url"     : "https://aethy.com/@InvaderNos/following",
    "#category": ("mastodon", "aethy", "following"),
    "#class"   : mastodon.MastodonFollowingExtractor,
},

{
    "#url"     : "https://aethy.com/@InvaderNos/following",
    "#category": ("mastodon", "aethy", "following"),
    "#class"   : mastodon.MastodonFollowingExtractor,
},

{
    "#url"     : "https://aethy.com/users/id:10843/following",
    "#category": ("mastodon", "aethy", "following"),
    "#class"   : mastodon.MastodonFollowingExtractor,
},

{
    "#url"     : "https://aethy.com/@InvaderNos/113240168182097151",
    "#category": ("mastodon", "aethy", "status"),
    "#class"   : mastodon.MastodonStatusExtractor,
    "#results" : "https://cdn.aethy.com/media_attachments/files/113/240/160/915/290/983/original/5e437c01a1832805.jpeg",

    "card"            : None,
    "content"         : "<p>You know what I&#39;m pinning this here too</p><p>Welcome to my account guys hope you have fun &lt;3 :pikawave:​ :pikawave:​ :pikawave:​ :pikawave:​</p>",
    "count"           : 1,
    "created_at"      : "2024-10-02T22:23:59.692Z",
    "date"            : "dt:2024-10-02 22:23:59",
    "edited_at"       : None,
    "extension"       : "jpeg",
    "favourites_count": int,
    "filename"        : "5e437c01a1832805",
    "id"              : "113240168182097151",
    "in_reply_to_account_id": None,
    "in_reply_to_id"  : None,
    "instance"        : "aethy.com",
    "instance_remote" : None,
    "language"        : "en",
    "local_only"      : False,
    "mentions"        : [],
    "num"             : 1,
    "poll"            : None,
    "reblog"          : None,
    "reblogs_count"   : int,
    "replies_count"   : int,
    "sensitive"       : False,
    "spoiler_text"    : "",
    "tags"            : [],
    "uri"             : "https://aethy.com/users/InvaderNos/statuses/113240168182097151",
    "url"             : "https://aethy.com/@InvaderNos/113240168182097151",
    "visibility"      : "unlisted",
    "account"         : {
        "acct"           : "InvaderNos",
        "avatar"         : "https://cdn.aethy.com/accounts/avatars/109/363/581/410/397/481/original/1038a52cd4539a6a.gif",
        "avatar_static"  : "https://cdn.aethy.com/accounts/avatars/109/363/581/410/397/481/static/1038a52cd4539a6a.png",
        "bot"            : False,
        "created_at"     : "2022-11-18T00:00:00.000Z",
        "discoverable"   : True,
        "display_name"   : "InvaderNos :shaymin_sip:",
        "followers_count": int,
        "following_count": int,
        "group"          : False,
        "header"         : "https://cdn.aethy.com/accounts/headers/109/363/581/410/397/481/original/5f8e8971a78904ce.jpg",
        "header_static"  : "https://cdn.aethy.com/accounts/headers/109/363/581/410/397/481/original/5f8e8971a78904ce.jpg",
        "id"             : "109363581410397481",
        "last_status_at" : "iso:dt",
        "locked"         : False,
        "noindex"        : False,
        "note"           : "<p>Being problematic is the most fun a girl can have online and, as is common knowledge, girls just wanna have fun :googlyeye:​ω:googlyeye:​</p><p>:blobcattrash: I mostly yap here</p>",
        "roles"          : [],
        "statuses_count" : int,
        "uri"            : "https://aethy.com/users/InvaderNos",
        "url"            : "https://aethy.com/@InvaderNos",
        "username"       : "InvaderNos",
    },
},

)
