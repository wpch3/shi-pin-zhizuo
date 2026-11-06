# -*- coding: utf-8 -*-
"""生成「上一版 vs 重制版」光影/画风对照图。"""
import os
import sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
from comic_lib import PAPER, INK, ACCENT, GREY, font, cover, tw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out")
os.makedirs(OUT, exist_ok=True)

W = 1560
CELL = 700
M, GAP = 50, 60
X1 = M
X2 = M + CELL + GAP


def label(d, text, xy, size=22, color=GREY, weight="med"):
    d.text(xy, text, font=font(size, weight), fill=color)


def build():
    canvas = Image.new("RGB", (W, 1400), PAPER)
    d = ImageDraw.Draw(canvas)

    d.text((M, 54), "光影与画风对照", font=font(48, "med"), fill=INK)
    label(d, "同一场戏，两种打光：左边是上一版，右边是本次重制。", (M + 2, 122), 24, GREY, "reg")
    d.line([(M, 176), (W - M, 176)], fill=(224, 214, 201), width=2)

    label(d, "上一版 · 原方案", (X1, 200), 24, (150, 138, 126))
    label(d, "重制版 · 本次", (X2, 200), 24, ACCENT)

    # ---- 第一组：姐姐/妹妹场景
    y1 = 240
    old1 = Image.open(os.path.join(ROOT, "assets/review/old_elite.png")).convert("RGB")
    canvas.paste(old1.resize((CELL, int(old1.height * CELL / old1.width)), Image.LANCZOS), (X1, y1))
    h1 = int(old1.height * CELL / old1.width)

    new1 = Image.open(os.path.join(ROOT, "assets/art/ep01_p1_elite.png")).convert("RGB")
    canvas.paste(cover(new1, CELL, h1, 0.0, 0.0), (X2, y1))
    label(d, "逆光 + 光晕 + 浅景深，人物边缘发亮", (X1, y1 + h1 + 10), 21)
    label(d, "单层柔光，无泛光，边缘干净", (X2, y1 + h1 + 10), 21)

    # ---- 第二组：Q 版
    y2 = y1 + h1 + 76
    old2 = Image.open(os.path.join(ROOT, "assets/review/old_chibi.png")).convert("RGB")
    h2 = int(old2.height * CELL / old2.width)
    canvas.paste(old2.resize((CELL, h2), Image.LANCZOS), (X1, y2))

    new2 = Image.open(os.path.join(ROOT, "assets/art/ep01_p4_chibi.png")).convert("RGB")
    canvas.paste(cover(new2, CELL, h2, 0.5, 0.12), (X2, y2))
    label(d, "高光溢出、厚涂光泽，姐姐多出一副眼镜", (X1, y2 + h2 + 10), 21)
    label(d, "平涂两层，配色与设定图一致", (X2, y2 + h2 + 10), 21)

    # ---- 结论
    y3 = y2 + h2 + 72
    d.line([(M, y3), (W - M, y3)], fill=(224, 214, 201), width=2)
    rows = [
        ("光", "旧：每一格都在打逆光，窗光晕开、边缘发光，暗部压到发黑。",
              "新：只保留一层柔和主光，阴影从三四层压到两层，整页对比度统一。"),
        ("色", "旧：饱和度拉满，像游戏 CG 预告片，连续翻页会累。",
              "新：提亮中间调，纸感底色，竖屏连读 6 页不刺眼。"),
        ("人", "旧：同一角色跨页换脸——姐姐忽有忽无的眼镜、二哥发色在棕黑之间跳。",
              "新：先锁人物设定图，再用它做参考逐格生成；中文全部由代码排版，不再出现乱码字。"),
    ]
    yy = y3 + 34
    for tag, a, b in rows:
        d.ellipse((M, yy + 4, M + 44, yy + 48), fill=ACCENT)
        t = tw(d, tag, font(26, "med"))
        d.text((M + 22 - t / 2, yy + 11), tag, font=font(26, "med"), fill=(255, 255, 255))
        d.text((M + 64, yy), a, font=font(25, "reg"), fill=INK)
        d.text((M + 64, yy + 38), b, font=font(25, "reg"), fill=INK)
        yy += 100

    path = os.path.join(OUT, "光影对照.png")
    canvas.crop((0, 0, W, yy - 10)).save(path)
    print("saved", path)


if __name__ == "__main__":
    build()
