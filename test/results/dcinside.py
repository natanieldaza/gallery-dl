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
        "https://image.dcinside.com/viewimage.php?no=24b0d769e1d32ca73de885fa1bd62531058478fac3157bc024e4bab3a06677d6d31d4957ed12b900e4a4ba4f8f184a66ea61b10f0d45c16cd41b0a8f6f6cfef1d4",
        "https://image.dcinside.com/viewimage.php?no=24b0d769e1d32ca73de885fa1bd62531058478fac3157bc024e4bab3a06677d6d31d4957ed12b900e4a4ba4f8f184a66ea61b10f0d40c538da1e0b8f616cfef11d",
    ),

    "board"       : "projectmx",
    "comments"    : range(25, 50),
    "content"     : "5일페 ［난선생님에게아무것도아니야사라져도누구도신경쓰지않을거야그렇지만날계속봐줬으면좋겠...］부스에 굿즈로 나가는 친구들입니다타이밍 좋게 게임에도 실장되어서 너무 기쁘네요^_^",
    "count"       : 2,
    "date"        : "dt:2025-04-22 14:37:57",
    "display_name": "메홍챠",
    "extension"   : "png",
    "fid"         : "3dafdf2ce0d12cab76",
    "filename"    : {
        "asdasddwdwsd",
        "asdasddwdwsdDDFSD",
    },
    "alt"         : {
        "2caed427f6d63cb16aa8c5b158c12a3a1ad241f0fad285a362abf5ad4a",
        "2caed427f6d63cb16aa8c5b132f5020e75544ba9563d9cf99c8ea652d451ad6b3b1a",
    },
    "id"          : 14994409,
    "no"          : {
        "24b0d769e1d32ca73de885fa1bd62531058478fac3157bc024e4bab3a06677d6d31d4957ed12b900e4a4ba4f8f184a66ea61b10f0d45c16cd41b0a8f6f6cfef1d4",
        "24b0d769e1d32ca73de885fa1bd62531058478fac3157bc024e4bab3a06677d6d31d4957ed12b900e4a4ba4f8f184a66ea61b10f0d40c538da1e0b8f616cfef11d",
    },
    "num"         : {1, 2},
    "title"       : "지뢰계 히카리/노조미 그림그렸어요 - 블루 아카이브 마이너 갤러리",
    "username"    : "wd3h8jz2hdnf",
    "views"       : range(5600, 9000),
},

{
    "#url"     : "https://gall.dcinside.com/mgallery/board/view?id=projectmx&no=18786425",
    "#class"   : dcinside.DcinsideGalleryExtractor,
    "#results" : "https://image.dcinside.com/viewimage.php?no=24b0d769e1d32ca73de785fa11d028311db29c13695a307ccacdd430f4f615f7eb84edfc6b29cdec234c8f75a949216a10eab94c2a4596f47cf00499df72a3da17535720fb0557cd190ac62903c4",

    "board"       : "projectmx",
    "comments"    : range(15, 50),
    "content"     : "호시노",
    "count"       : 1,
    "date"        : "dt:2026-07-11 05:40:41",
    "display_name": "유람",
    "extension"   : "png",
    "fid"         : "3dafdf2ce0d12cab76",
    "filename"    : "1783747949952",
    "alt"         : "7cea8875b2866fff3ae68fe0449f3433a1b3fa7f1a302c6695f8b3906777b0",
    "id"          : 18786425,
    "no"          : "24b0d769e1d32ca73de785fa11d028311db29c13695a307ccacdd430f4f615f7eb84edfc6b29cdec234c8f75a949216a10eab94c2a4596f47cf00499df72a3da17535720fb0557cd190ac62903c4",
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
        "https://image.dcinside.com/viewimage.php?no=24b0d769e1d32ca73fed84fa11d02831150e3d5bd66e1c599a53538ed1f12cc2bb5dc8cdd33653d2273e020357a452d5bd70facfcbe900f27151373889cd",
        "https://image.dcinside.com/viewimage.php?no=24b0d769e1d32ca73fed84fa11d02831150e3d5bd66e1c599a53538ed1f12cc2bb5dc8cdd33653d2273e020357a452d5bd70ad9fc8bf01fe7600373889cd",
        "https://image.dcinside.com/viewimage.php?no=24b0d769e1d32ca73fed84fa11d02831150e3d5bd66e1c599a53538ed1f12cc2bb5dc8cdd33653d2273e020357a452d5bd70fb999be507a37155373889cd",
        "https://image.dcinside.com/viewimage.php?no=24b0d769e1d32ca73fed84fa11d02831150e3d5bd66e1c599a53538ed1f12cc2bb5dc8cdd33653d2273e020357a452d5bd70f2979fef52a07350373889cd",
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
    "views"       : int,
},

{
    "#url"     : "https://gall.dcinside.com/mgallery/board/view/?id=onlk&no=2495",
    "#comment" : "ads in writing_view_box element (#444)",
    "#class"   : dcinside.DcinsideGalleryExtractor,
    "#results" : "https://image.dcinside.com/viewimage.php?no=24b0d769e1d32ca73de986fa11d02831cece6b72dd02ce8c7323b841a681867dcccab008263194f3ad05bf4e08dd0e328bd956fc64923e4beec77f",

    "board"       : "onlk",
    "comments"    : range(5, 30),
    "content"     : "릴레는 간호사나 좀비나 유령중에 고민을 상당히 오래햇네용",
    "count"       : 1,
    "date"        : "dt:2023-11-07 10:53:34",
    "display_name": "쌈바라차차",
    "extension"   : "jpg",
    "fid"         : "22b3dc2d",
    "alt"         : "a04810ad242eb553ae3417499a2dcc73408f8eac4f7b3157dcf1bb98b70cd7",
    "id"          : 2495,
    "num"         : 1,
    "title"       : "할로윈짤을 그렸사와요 - 플레이어(웹툰) 마이너 갤러리",
    "username"    : "tkaqkfkcici",
    "views"       : int,
},

{
    "#url"     : "https://gall.dcinside.com/mgallery/board/view?id=wutheringwaves&no=2721769",
    "#comment" : "external cloudfront-hosted images (#478)",
    "#class"   : dcinside.DcinsideGalleryExtractor,
    "#results" : (
        "https://d2i2w6ttft7yxi.cloudfront.net/froala/2026/07/04/20260704074328_8kh10r57x3.jpg",
        "https://d2i2w6ttft7yxi.cloudfront.net/froala/2026/07/04/20260704110530_016qjdxfew.jpg",
        "https://d2i2w6ttft7yxi.cloudfront.net/froala/2026/07/04/20260704074409_7v2e1uq8nd.jpg",
        "https://d2i2w6ttft7yxi.cloudfront.net/froala/2026/07/14/20260714051625_nt7ae1rbp5.jpg",
        "https://image.dcinside.com/viewimage.php?no=24b0d769e1d32ca73de785fa1bd62531de535045b081fc7000c7a813d8d2c9295b1d1391039bb08bc508a1c07792007aa6d89d294720ebdc1c627b04282a2eb1ca3024fc30af",
    ),

    "board"       : "wutheringwaves",
    "content"     : "🎁『7월 서코 커노의 스근한 판매점 통판 폼』 입니다!통판 기간 - 7월 14일 ~ 8월 7일 까지 입니다!🎁 작가 트위터 링크https://x.com/Kerno_kr🎁 통판 폼 링크https://witchform.com/payform/?uuid=ODIYYRKKKO데니아 에이메스 디오라마 실물입니다~현재 품절이었던 물품 (아트북 제외) 전부 재판 진행하겠습니다~극 소량도 제작해서 배송진행합니다!이번 행사도 구매해줘서 넘나링 감사룽다음 굿즈 캐릭터도 추천 받으니 댓글로 ㄱㄱㄱ",
    "count"       : 5,
    "date"        : "dt:2026-07-19 10:22:47",
    "display_name": "커노",
    "id"          : 2721769,
    "title"       : "[7월 서코] 커노의 스근한 판매점 통판 폼 준비해왔따우~ - 명조 워더링 웨이브 마이너 갤러리",
    "username"    : "cushion2768",
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
