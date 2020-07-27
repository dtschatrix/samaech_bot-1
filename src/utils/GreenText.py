from typing import Optional
from constants import ImageBuilderConstants as const
from PIL import Image, ImageDraw, ImageFont
import random
from datetime import datetime as date
import textwrap


class GreenTextImage:
    def __init__(
        self,
        sender,
        # only for test purposes
        text: str,
        image_path: Optional[
            str
        ] = "resources/images/default_boevaya_kartinochka.jpg",
    ):
        self.Text = text
        self.Sender = sender
        self.Font = ImageFont.truetype(
            "resources/fonts/trebuc.ttf",
            size=const.Others.FONTSIZE.value,
            encoding="utf-8",
        )
        self.ImagePath = image_path

    #
    # TODO: find and add new kartinochki(random choice).
    #

    def create_image(self):
        header = self.create_header(self.Sender)
        mainText = self.create_main_text(self.Text)
        completeImage = self.combine_images(header, mainText)
        return completeImage

    def create_header(self, text: str):
        if len(text) > 10:
            text = "тупое чмо"

        header_text = f'{text} {date.now().strftime("%x %a %X")}'

        draw = Image.new(
            "RGBA",
            const.Coordinates.HEADERROTATION.value,
            const.ARGBColor.ALPHATEXTCOLOR.value,
        )
        draw_text = ImageDraw.Draw(draw)
        # set header text
        draw_text.text(
            const.Coordinates.HEADEROFFSET.value,
            header_text,
            font=self.Font,
            fill=const.ARGBColor.FGHEADERTEXTCOLOR.value,
        )
        # set thread number
        header_size = draw_text.textsize(header_text, font=self.Font)
        draw_text.text(
            (header_size[0] + const.Others.THREADOFFSET.value, 0),
            text=f"№{random.randint(300000,400000)}",
            font=self.Font,
            fill=const.ARGBColor.FGTHREADNUMBERCOLOR.value,
        )

        return draw

    def create_main_text(self, textMessage: str):
        draw = Image.new("RGBA", const.Coordinates.MAINTEXTSIZE.value)
        draw_text = ImageDraw.Draw(draw)
        
        if(len(textMessage) > const.Others.MAXLENGTHTEXT.value):
            draw_text.multiline_text(const.Coordinates.NULL.value,
                                text="я долбоеб и напечатал дохуя говна",
                                font=self.Font,
                                fill=const.RGBColor.FGGREENTEXTCOLOR.value)
        elif(len(textMessage) > const.Others.SPLITLENGTH.value):
            mainText = self.splitText(textMessage, const.Others.SPLITLENGTH.value)  # test purposes()
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

    def combine_images(self, header, text):
        background = Image.new(
            "RGBA", const.Coordinates.BACKGROUND.value, const.RGBColor.BGCOLOR.value)
        image = Image.open(self.ImagePath, "r")
        out = image.resize(const.Coordinates.MAINIMAGE.value)
        
        background.alpha_composite(header)
        background.alpha_composite(text, const.Coordinates.MAINTEXTOFFSET.value)
        background.paste(out, const.Coordinates.MAINIMAGEROTATION.value)

        return background

    def splitText(self, text: str, length: int) -> str:
        wrapper = textwrap.TextWrapper(length)
        word_list = wrapper.wrap(text)
        return '\n'.join(word_list)
      