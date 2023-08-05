# Copyright (c) 2013 David Holm <dholmster@gmail.com>
# This file is part of SimpleGUITk - https://github.com/dholm/simpleguitk
# See the file 'COPYING' for copying permission.

from __future__ import division

import io
try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen


class Image(object):
    def __init__(self, url):
        from PIL import Image as PilImage
        image = urlopen(url).read()
        self._image = PilImage.open(io.BytesIO(image)).convert('RGBA')
        self._versions = {}

    def get_width(self):
        return self._image.size[0]

    def get_height(self):
        return self._image.size[1]

    def _get_tkimage(self, center, wh_src, wh_dst, rot):
        from PIL import Image as PilImage
        from PIL import ImageTk
        version = ','.join([str(center), str(wh_src), str(wh_dst), str(rot)])
        if version not in self._versions:
            crop = (int(center[0] - wh_src[0] // 2),
                    int(center[1] - wh_src[1] // 2),
                    int(center[0] + wh_src[0] // 2),
                    int(center[1] + wh_src[1] // 2))
            image = self._image.crop([int(x) for x in crop])
            image = image.resize([int(x) for x in wh_dst],
                                 resample=PilImage.BILINEAR)
            image = image.rotate(-rot, resample=PilImage.BICUBIC, expand=1)
            self._versions[version] = ImageTk.PhotoImage(image)
        return self._versions[version]


def load_image(URL):
    return Image(URL)


def get_width(image):
    return image.get_width()


def get_height(image):
    return image.get_height()
