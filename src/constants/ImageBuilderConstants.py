from enum import Enum


class RGBColor(Enum):
    BGCOLOR = "#dddddd"
    FGGREENTEXTCOLOR = "#789922"


class ARGBColor(Enum):
    ALPHATEXTCOLOR = (255, 255, 255, 0)
    FGHEADERTEXTCOLOR = (51, 51, 51, 255)
    FGTHREADNUMBERCOLOR = (250, 102, 0, 255)


class Coordinates(Enum):
    NULL = (0, 0)
    MAINIMAGE = (170, 170)
    MAINIMAGEROTATION = (30, 42)
    BACKGROUND = (450, 233)
    MAINTEXTSIZE = (220, 225)
    MAINTEXTOFFSET = (210, 62)
    HEADEROFFSET = (6, 0)
    HEADERROTATION = (350, 255)


class Others(Enum):
    FONTSIZE = 15
    THREADOFFSET = 20
