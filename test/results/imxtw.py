# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imagehosts


__tests__ = (
{
    "#url"     : "https://imx.bz/1a2b3c4d5e6f",
    "#category": ("imagehost", "imxtw", "image"),
    "#class"   : imagehosts.ImxtwImageExtractor,
},

{
    "#url"     : "https://imx.tw/1a2b3c4d5e6f",
    "#category": ("imagehost", "imxtw", "image"),
    "#class"   : imagehosts.ImxtwImageExtractor,
},

{
    "#url"     : "https://www.imx.tw/1a2b3c4d5e6f",
    "#category": ("imagehost", "imxtw", "image"),
    "#class"   : imagehosts.ImxtwImageExtractor,
},

)
