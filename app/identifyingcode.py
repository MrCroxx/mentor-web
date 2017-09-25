# -*- coding:utf-8 -*-
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from models import getSHA256
import random


def rndChar():
    return chr(random.randint(65, 90))


def rndColor():
    return (random.randint(64, 255), random.randint(64, 255), random.randint(64, 255))


def rndColor2():
    return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))


def drawIdentifyingCode(width=220, height=50):

    image = Image.new('RGB', (width, height), (255, 255, 255))

    font = ImageFont.truetype('app/static/lib/fonts/Arial.ttf', 32)

    draw = ImageDraw.Draw(image)

    for x in range(width):
        for y in range(height):
            draw.point((x, y), fill=rndColor())

    text = ''

    for t in range(4):
        tx = rndChar()
        draw.text((width / 4 * t + 10, 10), tx, font=font, fill=rndColor2())
        text += tx

    image = image.filter(ImageFilter.BLUR)
    image.save('app/static/tmp/code/' + getSHA256(text), 'jpeg')
    return image, text
