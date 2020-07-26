from typing import Optional
from constants import ImageBuilderConstants as const
from PIL import Image, ImageDraw, ImageFont
import random
from datetime import datetime as date

from pyrogram import Message


class GreenTextImage:
    def __init__(
        self,
        sender,
        # only for test purposes
        text:str,
        imagePath: Optional[str] = 'resources/images/default_boevaya_kartinochka.jpg'
    ):
        self.Text = text
        self.Sender = sender
        self.Font = ImageFont.truetype(
            "resources/fonts/trebuc.ttf", size=const.Others.FONTSIZE.value, encoding="utf-8")
        self.ImagePath = imagePath
    #
    # TODO: find and add new kartinochki(random choice).
    #

    def createImage(self):
        header = self.createHeader(self.Sender)
        mainText = self.createMainText(self.Text)
        completeImage = self.combineImages(header, mainText)
        return completeImage

    def createHeader(self, text: str):
        if len(text) > 10:
            text = 'тупое чмо'

        header_text = f'{text} {date.now().strftime("%x %a %X")}'

        draw = Image.new("RGBA", const.Coordinates.HEADERROTATION.value,
                         const.ARGBColor.ALPHATEXTCOLOR.value)
        draw_text = ImageDraw.Draw(draw)
        #set header text
        draw_text.text(const.Coordinates.HEADEROFFSET.value,
                  header_text,
                  font=self.Font,
                  fill=const.ARGBColor.FGHEADERTEXTCOLOR.value)
        #set thread number
        header_size = draw_text.textsize(header_text, font=self.Font)
        draw_text.text((header_size[0]+const.Others.THREADOFFSET.value, 0),
                  text=f"№{random.randint(300000,400000)}",
                  font=self.Font,
                  fill=const.ARGBColor.FGTHREADNUMBERCOLOR.value)

        return draw

    def createMainText(self, textMessage: str):
        draw = Image.new("RGBA", const.Coordinates.MAINTEXTSIZE.value)
        draw_text = ImageDraw.Draw(draw)
        
        if(len(textMessage) > 60):
            mainText = self.splitText(textMessage, 32)  # test purposes()
            draw_text.multiline_text(const.Coordinates.NULL.value,
                                text = mainText,
                                font=self.Font,
                                fill=const.RGBColor.FGGREENTEXTCOLOR.value)
        else:
            draw_text.text(const.Coordinates.NULL.value,
                      text= textMessage,
                      font=self.Font,
                      fill=const.RGBColor.FGGREENTEXTCOLOR.value)

        return draw

    def combineImages(self, header, text):
        background = Image.new(
            "RGBA", const.Coordinates.BACKGROUND.value, const.RGBColor.BGCOLOR.value)
        image = Image.open(self.ImagePath, "r")
        out = image.resize(const.Coordinates.MAINIMAGE.value)
        
        background.alpha_composite(header)
        background.alpha_composite(text, const.Coordinates.MAINTEXTOFFSET.value)
        background.paste(out, const.Coordinates.MAINIMAGEROTATION.value)

        return background

    def splitText(self, text: str, length: int) -> str:
        if(length > len(text)):
            return text
        return '\n'.join(text[i:i+length] for i in range(0, len(text), length))
