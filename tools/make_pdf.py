# -*- coding: utf-8 -*-
"""把 comic/ep01/p01..p06.png 打包成 PDF，并生成一张连页预览图。"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "comic/ep01")
OUT = os.path.join(ROOT, "out")
os.makedirs(OUT, exist_ok=True)

pages = [Image.open(os.path.join(SRC, f"p{i:02d}.png")).convert("RGB") for i in range(1, 7)]

pdf = os.path.join(OUT, "第一话_全家都在藏私.pdf")
pages[0].save(pdf, save_all=True, append_images=pages[1:], resolution=150.0)
print("pdf:", pdf, round(os.path.getsize(pdf) / 1e6, 2), "MB")

# 连页预览
thumb_w = 360
thumbs = [p.resize((thumb_w, int(p.height * thumb_w / p.width)), Image.LANCZOS) for p in pages]
gap = 16
W = thumb_w * 3 + gap * 4
Hh = thumbs[0].height * 2 + gap * 3
sheet = Image.new("RGB", (W, Hh), (247, 243, 237))
for i, t in enumerate(thumbs):
    x = gap + (i % 3) * (thumb_w + gap)
    y = gap + (i // 3) * (t.height + gap)
    sheet.paste(t, (x, y))
prev = os.path.join(OUT, "第一话_全页预览.png")
sheet.save(prev)
print("preview:", prev, sheet.size)
