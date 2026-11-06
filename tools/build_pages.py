# -*- coding: utf-8 -*-
"""生成《全家都在藏私》第一话 竖屏条漫页（1080x1920）。

版式：顶部主画面（0-924）→ 中部对白区 → 下部旁白区。
画与字严格分区，气泡不压脸；中文全部由代码排版，避免 AI 生成错字。
坐标均为页面坐标，画面上已按固定裁切参数落位。
"""
import os
import sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
from comic_lib import (PAPER, CREAM, INK, ACCENT, GREY, font, cover, bubble,
                       caption, sfx, header, chat_box, tw)

W, H = 1080, 1920
ART_Y, ART_H = 104, 820
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "assets/art")
OUT = os.path.join(ROOT, "comic/ep01")
os.makedirs(OUT, exist_ok=True)
SERIES = "全家都在藏私"


# ----------------------------------------------------------------- 基础构件
def new_page(n):
    im = Image.new("RGB", (W, H), PAPER)
    header(im, f"VOL.01   {SERIES}", f"{n:02d} / 06")
    d = ImageDraw.Draw(im)
    f = font(19, "reg")
    d.text((56, H - 62), "外人眼里的神仙家庭 · 第一话", font=f, fill=(178, 165, 152))
    r = "原创短篇漫画 / 竖屏连载"
    d.text((W - 56 - tw(d, r, f), H - 62), r, font=f, fill=(178, 165, 152))
    # 进度点
    for i in range(6):
        cx = W / 2 - 55 + i * 22
        fill = ACCENT if i == n - 1 else (223, 212, 199)
        d.ellipse((cx - 3, 1822, cx + 3, 1828), fill=fill)
    return im


def put_art(im, name, fx=0.5, fy=0.5):
    src = Image.open(os.path.join(ART, name)).convert("RGB")
    im.paste(cover(src, W, ART_H, fx, fy), (0, ART_Y))
    ImageDraw.Draw(im).line([(0, ART_Y + ART_H), (W, ART_Y + ART_H)],
                            fill=(224, 214, 201), width=2)


def pill(im, text, xy, size=24):
    d = ImageDraw.Draw(im)
    f = font(size, "med")
    w = tw(d, text, f)
    x, y = xy
    d.rounded_rectangle((x, y, x + w + 32, y + size + 22), radius=(size + 22) // 2,
                        fill=(255, 255, 255), outline=(60, 50, 42), width=2)
    d.text((x + 16, y + 9), text, font=f, fill=INK)


def watermark(im, text, xy, size=300):
    """极浅的大号页码，用来给竖屏页面下半部做质感。"""
    ImageDraw.Draw(im).text(xy, text, font=font(size, "med"), fill=(245, 239, 231))


def txt(im, text, xy, size, color=INK, weight="med"):
    ImageDraw.Draw(im).text(xy, text, font=font(size, weight), fill=color)


def rule(im, y, x0=56, x1=1024, color=(224, 214, 201), w=2):
    ImageDraw.Draw(im).line([(x0, y), (x1, y)], fill=color, width=w)


def note(im, lines, box, size=24, alpha=255):
    """半透明便签：既能加注释，也能盖掉 AI 图里残留的乱码文字。"""
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rounded_rectangle(box, radius=14, fill=(250, 245, 236, alpha),
                        outline=(70, 58, 48, 255), width=2)
    x0, y0, x1, y1 = box
    f = font(size, "med")
    y = y0 + 18
    for ln in lines:
        d.text((x0 + 20, y), ln, font=f, fill=(40, 33, 28, 255))
        y += int(size * 1.55)
    im.paste(Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB"), (0, 0))
    return im


# ----------------------------------------------------------------- 01 封面
def p1():
    im = new_page(1)
    put_art(im, "ep01_p1_elite.png", fx=0.40)
    pill(im, "姐姐 · 知冬 / 27", (48, 138))
    pill(im, "妹妹 · 听夏 / 18", (742, 150))

    txt(im, "第一话", (56, 968), 26, ACCENT)
    txt(im, "全家都在藏私", (56, 1006), 74)
    rule(im, 1112, 56, 248, ACCENT, 5)

    txt(im, "这是外人眼里的林家。", (56, 1148), 34, INK, "reg")
    txt(im, "体面、完美、遥不可及。", (56, 1206), 34, INK, "reg")
    txt(im, "——直到他们推开家门。", (56, 1300), 36, ACCENT)

    cast = Image.open(os.path.join(ART, "cast_strip.png")).convert("RGB")
    cw = 980
    cast = cast.resize((cw, int(cast.height * cw / cast.width)), Image.LANCZOS)
    txt(im, "本话登场", (56, 1414), 22, GREY, "reg")
    im.paste(cast, ((W - cw) // 2, 1452))
    return im


# ----------------------------------------------------------------- 02 二哥
def p2():
    im = new_page(2)
    put_art(im, "ep01_p2_couch.png", fx=0.48)
    watermark(im, "02", (730, 1000))
    note(im, ["外卖第 4 天。", "这个家里最会做饭的人，", "正在等别人给他做饭。"],
         (18, 676, 372, 902), size=23)

    bubble(im, "行吧。", (96, 950, 420, 1074), target=(425, ART_Y + ART_H - 2), size=36)
    caption(im, ["手机从早上七点响到现在。他一条都没回。"],
            (460, 958, 1030, 1036), size=26, fill=(255, 255, 255),
            line_color=(224, 214, 201))

    txt(im, "在所有人眼里，", (56, 1392), 32, GREY, "reg")
    txt(im, "他是全家最没出息的", (56, 1444), 50)
    txt(im, "那一个。", (56, 1518), 50)

    chat_box(im, "爸", "儿子，公司今年最大的项目，又靠你收尾了。",
             (56, 1630, 1024, 1748), size=30)
    txt(im, "（他没说，这个项目他已经连熬了九个通宵。）", (56, 1774), 24, GREY, "reg")
    return im


# ----------------------------------------------------------------- 03 破门
def p3():
    im = new_page(3)
    put_art(im, "ep01_p3_door.png", fx=0.50)
    watermark(im, "03", (730, 1050))
    sfx(im, "砰！", (150, 150), size=104)

    bubble(im, "弟弟——姐姐的电量只剩 1% 了！", (56, 946, 540, 1150),
           target=(500, ART_Y + ART_H - 2), size=38)
    bubble(im, "二哥！今晚轮到我挂！", (580, 990, 1024, 1156),
           target=(780, ART_Y + ART_H - 2), size=38)

    txt(im, "一秒前还是女神和学霸。", (56, 1404), 32, GREY, "reg")
    txt(im, "一秒后，人设全线崩塌。", (56, 1460), 44, ACCENT)
    txt(im, "而她们冲向的，是全家最没出息的那个人。", (56, 1556), 27, GREY, "reg")
    rule(im, 1660)
    txt(im, "本周第三次。", (56, 1686), 30, INK, "reg")
    txt(im, "纪录保持者：姐姐。", (256, 1690), 24, GREY, "reg")
    return im


# ----------------------------------------------------------------- 04 挂件
def p4():
    im = new_page(4)
    put_art(im, "ep01_p4_chibi.png", fx=0.50)
    watermark(im, "04", (730, 1010))

    bubble(im, "……这就是我不能站起来的原因。", (56, 946, 690, 1150),
           target=(520, ART_Y + ART_H - 2), size=35)
    bubble(im, "二哥是我的！", (660, 962, 1024, 1092),
           target=(810, ART_Y + ART_H - 2), size=32)

    txt(im, "挂在他腿上的小不点，是我大哥的女儿。", (56, 1402), 30, INK, "reg")
    txt(im, "大哥在南方的工地，已经一年没回家了。", (56, 1454), 30, INK, "reg")
    rule(im, 1526)
    txt(im, "他是全家的插座。", (56, 1552), 50, ACCENT)
    return im


# ----------------------------------------------------------------- 05 视频
def p5():
    im = new_page(5)
    put_art(im, "ep01_p5_call.png", fx=0.45)

    bubble(im, "……我下周回去。", (56, 942, 560, 1086),
           target=(510, ART_Y + ART_H - 2), size=40)
    caption(im, ["母亲（画外）", "回来干嘛？你房间都改成储物间了。"],
            (56, 1116, 600, 1272), size=28, fill=(255, 255, 255),
            line_color=(60, 50, 42))
    bubble(im, "那我睡沙发。", (640, 1104, 1024, 1210), size=34)
    bubble(im, "C 位在那儿。", (640, 1234, 1024, 1340), size=34)

    chat_card(im, "林家一家人 · 6", [
        ("妹妹", "录了，全程。"),
        ("妹妹", "▷ 视频 00:23"),
        ("妈", "他要回来了。"),
        ("二哥", "房间我收拾好了。", "right"),
        ("爸", "（撤回了一条消息）", "center"),
    ], (56, 1402, 1024, 1798))
    return im


# ----------------------------------------------------------------- 06 深夜
def p6():
    im = new_page(6)
    put_art(im, "ep01_p6_night.png", fx=0.45)
    caption(im, ["凌晨 1:47，视频结束后的第 4 分钟。"], (40, 150, 470, 226),
            size=24, fill=(255, 255, 255), line_color=(70, 58, 48))

    txt(im, "外人眼里的冷面经理，", (56, 976), 32, GREY, "reg")
    txt(im, "手机里存了 482 张", (56, 1028), 42)
    txt(im, "家里的照片。", (56, 1090), 42)
    txt(im, "一张都没发过。", (56, 1196), 68, ACCENT)
    rule(im, 1316)
    txt(im, "第一话 · 完", (56, 1342), 34)
    txt(im, "下回：第二话《我妈才是全家的顶流》", (56, 1402), 26, GREY, "reg")

    box = (56, 1512, 1024, 1672)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(box, radius=8, fill=CREAM, outline=(60, 50, 42), width=2)
    f = font(34, "med")
    t = "「下周回去。这次是真的。」"
    d.text(((box[0] + box[2]) / 2 - tw(d, t, f) / 2, 1548), t, font=f, fill=INK)
    f2 = font(24, "reg")
    t2 = "—— 大哥"
    d.text(((box[0] + box[2]) / 2 - tw(d, t2, f2) / 2, 1600), t2, font=f2, fill=GREY)
    return im



# ----------------------------------------------------------------- 群聊卡片
def chat_card(im, title, rows, box):
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=18, fill=(255, 255, 255), outline=(70, 58, 48), width=2)
    d.text((x0 + 26, y0 + 18), title, font=font(22, "med"), fill=GREY)
    d.line([(x0 + 2, y0 + 58), (x1 - 2, y0 + 58)], fill=(232, 223, 212), width=2)
    y = y0 + 78
    for row in rows:
        name, text = row[0], row[1]
        align = row[2] if len(row) > 2 else "left"
        fn = font(21, "med")
        ft = font(27, "reg")
        if align == "center":
            w = tw(d, text, ft)
            d.text(((x0 + x1) / 2 - w / 2, y), text, font=ft, fill=(160, 148, 136))
            y += 58
        elif align == "right":
            w = tw(d, text, ft)
            d.text((x1 - 30 - w, y - 2), text, font=ft, fill=INK)
            dw = tw(d, name, fn)
            d.text((x1 - 30 - w - dw - 18, y + 2), name, font=fn, fill=ACCENT)
            y += 60
        else:
            d.text((x0 + 30, y), name, font=fn, fill=ACCENT)
            d.text((x0 + 30 + tw(d, name, fn) + 18, y - 2), text, font=ft, fill=INK)
            y += 58
    return box


if __name__ == "__main__":
    for i, fn in enumerate([p1, p2, p3, p4, p5, p6], 1):
        img = fn()
        path = os.path.join(OUT, f"p{i:02d}.png")
        img.save(path)
        print("saved", path, img.size)


