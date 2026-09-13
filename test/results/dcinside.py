# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import dcinside


__tests__ = (
{
    "#url"     : "https://gall.dcinside.com/mgallery/board/view?id=projectmx&no=14994409",
    "#class"   : dcinside.DcinsideGalleryExtractor,
    "#results" : (
        "https://dcimg1.dcinside.com/viewimage.php?id=3dafdf2ce0d12cab76&no=24b0d769e1d32ca73de885fa1bd62531058478fac3157bc024e4bab3a06677d6d31d4957ed12b900e4a4ff1ad5734a6e5c0f5d163c4901cdb8e4f7c6616fd39a3109f70107",
        "https://dcimg1.dcinside.com/viewimage.php?id=3dafdf2ce0d12cab76&no=24b0d769e1d32ca73de885fa1bd62531058478fac3157bc024e4bab3a06677d6d31d4957ed12b900e4a4ff1ad5734a6e5c0f5d163c4901cdb8e1f3926f6ad29a25dea500f8",
    ),

    "board"       : "projectmx",
    "comments"    : range(25, 50),
    "content"     : "5일페 ［난선생님에게아무것도아니야사라져도누구도신경쓰지않을거야그렇지만날계속봐줬으면좋겠...］부스에 굿즈로 나가는 친구들입니다타이밍 좋게 게임에도 실장되어서 너무 기쁘네요^_^",
    "count"       : 2,
    "date"        : "dt:2025-04-22 14:37:57",
    "display_name": "메홍챠",
    "extension"   : "jpg",
    "hash"        : {
        "2caed427f6d63cb16aa8c5b158c12a3a1ad241f0fad285a362abf5ad4a",
        "2caed427f6d63cb16aa8c5b132f5020e75544ba9563d9cf99c8ea652d451ad6b3b1a",
    },
    "id"          : 14994409,
    "num"         : {1, 2},
    "title"       : "지뢰계 히카리/노조미 그림그렸어요 - 블루 아카이브 마이너 갤러리",
    "username"    : "wd3h8jz2hdnf",
    "views"       : range(5600, 9000),
},

{
    "#url"     : "https://gall.dcinside.com/mgallery/board/view?id=projectmx&no=18786425",
    "#class"   : dcinside.DcinsideGalleryExtractor,
    "#results" : "https://dcimg4.dcinside.co.kr/viewimage.php?id=3dafdf2ce0d12cab76&no=24b0d769e1d32ca73de785fa11d028311db29c13695a307ccacdd430f4f615f7eb84edfc6b29cdec230edf23c04e256cf557c84ded177ace55d1c855695cabfe62ae3774f6f10737fe8eb97661d41b7132dc",

    "board"       : "projectmx",
    "comments"    : range(15, 50),
    "content"     : "호시노",
    "count"       : 1,
    "date"        : "dt:2026-07-11 05:40:41",
    "display_name": "유람",
    "extension"   : "jpg",
    "hash"        : "7cea8875b2866fff3ae68fe0449f3433a1b3fa7f1a302c6695f8b3906777b0",
    "id"          : 18786425,
    "num"         : 1,
    "title"       : "으헤으헤으헤으헤으헤으헤 - 블루 아카이브 마이너 갤러리",
    "username"    : "chinese5249",
    "views"       : range(3500, 9000),
},

{
    "#url"     : "https://gall.dcinside.com/mgallery/board/view?id=drawing&no=24172",
    "#comment" : "lazy-loaded images (#443)",
    "#class"   : dcinside.DcinsideGalleryExtractor,
    "#results" : (
        "https://dcimg1.dcinside.com/viewimage.php?id=29afd131ecdc3f&no=24b0d769e1d32ca73fed84fa11d02831150e3d5bd66e1c599a53538ed1f12cc2bb5dc8cdd3365397726c6b0257a05cd3dc739d35a28f965f727cc2910ef0b67c822a",
        "https://dcimg1.dcinside.com/viewimage.php?id=29afd131ecdc3f&no=24b0d769e1d32ca73fed84fa11d02831150e3d5bd66e1c599a53538ed1f12cc2bb5dc8cdd3365397726c6b0257a05cd3dc739d35a28fc10f712ac39d09a1b67ccdbd",
        "https://dcimg1.dcinside.com/viewimage.php?id=29afd131ecdc3f&no=24b0d769e1d32ca73fed84fa11d02831150e3d5bd66e1c599a53538ed1f12cc2bb5dc8cdd3365397726c6b0257a05cd3dc739d35a28f97092270c5c00ef4b67c8fa8",
        "https://dcimg1.dcinside.com/viewimage.php?id=29afd131ecdc3f&no=24b0d769e1d32ca73fed84fa11d02831150e3d5bd66e1c599a53538ed1f12cc2bb5dc8cdd3365397726c6b0257a05cd3dc739d35a28f9e07267a90c30cf1b67c7c8c",
    ),

    "board"       : "drawing",
    "comments"    : range(15, 30),
    "content"     : "파개",
    "count"       : 4,
    "date"        : "dt:2019-10-11 08:59:32",
    "display_name": "쌈바라차차",
    "extension"   : "jpg",
    "id"          : 24172,
    "title"       : "최근그림들 - 그림 마이너 갤러리",
    "username"    : "tkaqkfkcici",
},

{
    "#url"     : "https://gall.dcinside.com/mgallery/board/view/?id=onlk&no=2495",
    "#comment" : "ads in 'writing_view_box' element (#444)",
    "#class"   : dcinside.DcinsideGalleryExtractor,
    "#results" : "https://dcimg1.dcinside.com/viewimage.php?id=22b3dc2d&no=24b0d769e1d32ca73de986fa11d02831cece6b72dd02ce8c7323b841a681867dcccab0086364c69aac05bb410adb656aa57a963991117bde68d41fd967a689",

    "board"       : "onlk",
    "comments"    : range(5, 15),
    "content"     : "릴레는 간호사나 좀비나 유령중에 고민을 상당히 오래햇네용",
    "date"        : "dt:2023-11-07 10:53:34",
    "display_name": "쌈바라차차",
    "extension"   : "jpg",
    "hash"        : "a04810ad242eb553ae3417499a2dcc73408f8eac4f7b3157dcf1bb98b70cd7",
    "id"          : 2495,
    "title"       : "할로윈짤을 그렸사와요 - 플레이어(웹툰) 마이너 갤러리",
    "username"    : "tkaqkfkcici",
},

{
    "#url"     : "https://gallog.dcinside.com/chinese5249",
    "#class"   : dcinside.DcinsideUserExtractor,
    "#pattern" : dcinside.DcinsideGalleryExtractor.pattern,
    "#count"   : 51,
},

{
    "#url"     : "https://gallog.dcinside.com/chinese5249/posting",
    "#class"   : dcinside.DcinsideUserExtractor,
},

{
    "#url"     : "https://gallog.dcinside.com/chinese5249/posting/index?cno=5",
    "#class"   : dcinside.DcinsideUserExtractor,
    "#results" : (
        "https://gall.dcinside.com/mgallery/board/view?id=stellive&no=4925219",
        "https://gall.dcinside.com/mgallery/board/view?id=stellive&no=4802116",
        "https://gall.dcinside.com/mgallery/board/view?id=stellive&no=4797792",
    ),
},

)
