# -*- coding: utf-8 -*-
"""从人物设定图裁圆形头像，拼成页脚人物条（含姓名）。"""
import os
import sys
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
from comic_lib import font, tw, INK, GREY, PAPER

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHEET = os.path.join(ROOT, "assets/art/00_character_sheet.png")

# (姓名, 关系, 头部中心x, 头部中心y, 半径) —— 坐标基于 1569x1002 设定图
HEADS = [
    ("林见秋", "大哥 29", 210, 105, 78),
    ("林知冬", "姐姐 27", 536, 130, 70),
    ("林逢春", "二哥 25", 838, 118, 78),
    ("林听夏", "妹妹 18", 1148, 222, 70),
    ("林小满", "侄女 5", 1373, 552, 64),
]


def avatar(sheet, cx, cy, r, size=220):
    box = (cx - r, cy - r, cx + r, cy + r)
    im = sheet.crop(box).resize((size, size), Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(1))
    im.putalpha(mask)
    return im


def build():
    sheet = Image.open(SHEET).convert("RGB")
    n = len(HEADS)
    gap, d_size = 18, 196
    W = n * d_size + (n - 1) * gap
    H = d_size + 76
    canvas = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(canvas)
    for i, (name, rel, cx, cy, r) in enumerate(HEADS):
        a = avatar(sheet, cx, cy, r).resize((d_size, d_size), Image.LANCZOS)
        x = i * (d_size + gap)
        canvas.paste(a, (x, 0), a)
        d.ellipse((x, 0, x + d_size - 1, d_size - 1), outline=(214, 202, 187), width=2)
        f = font(25, "med")
        w = tw(d, name, f)
        d.text((x + d_size / 2 - w / 2, d_size + 10), name, font=f, fill=INK)
        f2 = font(19, "reg")
        w2 = tw(d, rel, f2)
        d.text((x + d_size / 2 - w2 / 2, d_size + 44), rel, font=f2, fill=GREY)
    out = os.path.join(ROOT, "assets/art/cast_strip.png")
    canvas.save(out)
    print("saved", out, canvas.size)
    return canvas


if __name__ == "__main__":
    build()
