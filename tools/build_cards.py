# -*- coding: utf-8 -*-
"""生成《全家都在藏私》人物设定卡（1080x1920）：
每个人的「对外人设」与「在家原型」并置，直接对应本作的核心梗。"""
import os
import sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
from comic_lib import PAPER, CREAM, INK, ACCENT, GREY, font, tw, wrap
from build_cast import HEADS, avatar

W, H = 1080, 1920
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHEET = os.path.join(ROOT, "assets/art/00_character_sheet.png")
OUT = os.path.join(ROOT, "out")
os.makedirs(OUT, exist_ok=True)

CARDS = [
    ("林知冬", "姐姐 · 27", "交大博士，陆家嘴上班。冷感精英，一天说不到十句话。",
     "弟弟一进门就自动断线：脑力体力样样行，唯独在他面前当废物。"),
    ("林听夏", "妹妹 · 18", "CQ一中全校第一，高二拿下 SAT / AP，明年留英的完美优等生。",
     "在二哥面前不装：粘人、爱吃醋，抢「挂件」C 位第一名。"),
    ("林逢春", "二哥 · 25", "作息混乱的 QH 毕业生，在家啃老半年，全家最没出息的那个。",
     "清爽、自信、帅；父亲公司的大项目件件收尾漂亮，全家真正的定海神针。"),
    ("林小满", "侄女 · 5", "幼儿园里最乖的小朋友，老师眼里的天使。",
     "小叔的人形挂件，走到哪挂到哪；睡前必须小叔讲故事，一讲就是三遍。"),
    ("林见秋", "大哥 · 29", "G 企项目总经理，冷面，四兄妹里唯一只有本科学历的人。",
     "手机里存了 482 张家里的照片——一张都没发过。也一年没回过家。"),
]


def chip(d, xy, text, fill, color=INK, size=20):
    f = font(size, "med")
    x, y = xy
    w = tw(d, text, f) + 20
    d.rounded_rectangle((x, y, x + w, y + size + 12), radius=(size + 12) // 2, fill=fill)
    d.text((x + 10, y + 5), text, font=f, fill=color)
    return w


def build():
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    sheet = Image.open(SHEET).convert("RGB")

    d.text((56, 96), "人物设定", font=font(64, "med"), fill=INK)
    d.text((58, 186), "CHARACTER  SHEET   /   《全家都在藏私》第一话", font=font(22, "reg"), fill=GREY)
    d.line([(56, 236), (1024, 236)], fill=(224, 214, 201), width=2)

    head = {h[0]: h for h in HEADS}
    y = 268
    for name, rel, outward, inward in CARDS:
        cx, cy, r = head[name][2], head[name][3], head[name][4]
        a = avatar(sheet, cx, cy, r, 300).resize((156, 156), Image.LANCZOS)
        im.paste(a, (56, y + 26), a)
        d.ellipse((56, y + 26, 56 + 155, y + 26 + 155), outline=(214, 202, 187), width=2)

        x = 240
        d.text((x, y + 16), name, font=font(44, "med"), fill=INK)
        d.text((x + tw(d, name, font(44, "med")) + 16, y + 34), rel, font=font(22, "reg"), fill=GREY)

        cy2 = y + 82
        cw = chip(d, (x, cy2), "外人眼里", (233, 224, 212), GREY)
        f = font(26, "reg")
        lines = wrap(d, outward, f, 1010 - x - cw - 24)
        yy = cy2 + 2
        for ln in lines:
            d.text((x + cw + 16, yy), ln, font=f, fill=INK)
            yy += 38

        cy3 = max(cy2 + 2 + 38 * len(lines) + 14, y + 150)
        cw = chip(d, (x, cy3), "关起门", ACCENT, (255, 255, 255))
        lines2 = wrap(d, inward, f, 1010 - x - cw - 24)
        yy = cy3 + 2
        for ln in lines2:
            d.text((x + cw + 16, yy), ln, font=f, fill=INK)
            yy += 38
        y = max(cy3 + 40 + 38 * len(lines2), y + 268)
        d.line([(56, y - 34), (1024, y - 34)], fill=(235, 226, 215), width=2)

    d.text((56, y + 4), "父亲 林正业：大企业老板，很少回家。", font=font(24, "reg"), fill=GREY)
    d.text((56, y + 44), "母亲 苏晚：全职主妇，每天去自家超市收租兼收银——全家的账都在她手里。",
           font=font(24, "reg"), fill=GREY)
    d.text((56, y + 100), "命名：见秋 / 知冬 / 逢春 / 听夏 —— 见、知、逢、听都是「感知」，",
           font=font(22, "reg"), fill=(178, 165, 152))
    d.text((56, y + 134), "这一家人从不直说，只靠观察；小满是唯一的节气，也是家里唯一「满」的东西。",
           font=font(22, "reg"), fill=(178, 165, 152))

    path = os.path.join(OUT, "人物设定卡.png")
    im.save(path)
    print("saved", path, im.size)


if __name__ == "__main__":
    build()
