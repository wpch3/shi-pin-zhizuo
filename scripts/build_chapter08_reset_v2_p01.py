"""Render only the experimental reset page 01; not a complete chapter build.

Requires Pillow. Never edits or crops the source image.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'art/chapter-08-reset-v2/01-new-class.png'
OUT = ROOT / 'deliverables/章节/第八话/review-chapter-08-reset-v2/page-01-typeset-preview.png'
FONT = ROOT / 'assets/fonts/NotoSansCJKsc-Bold.otf'
im = Image.open(SOURCE).convert('RGB')
if im.size != (896, 1200):
    raise ValueError(f'Unexpected page size: {im.size}')
draw = ImageDraw.Draw(im)
font = ImageFont.truetype(str(FONT), 25)
math_font = ImageFont.truetype(str(FONT), 23)
# Oval without a pointer, explicitly identifying an off-screen teacher.
draw.ellipse((257, 37, 639, 155), fill='#fffdf7', outline='#34383a', width=2)
for text, y in [('老师（画外）：', 54), ('这道题，谁有思路？', 92)]:
    box = draw.textbbox((0, 0), text, font=font)
    x = 448 - (box[2] - box[0]) / 2
    draw.text((x, y), text, font=font, fill='#242a2c')
# Source blackboard's clear right-hand region: avoid the pupil's head.
for text, y in [('x＋y＋z＝6', 337), ('xy＋yz＋zx＝11', 375), ('求 x³＋y³＋z³－3xyz', 413)]:
    box = draw.textbbox((0, 0), text, font=math_font)
    if 514 + box[2] - box[0] > 879:
        raise ValueError(f'Math line too wide: {text}')
    draw.text((514, y), text, font=math_font, fill='#f6f5e7')
OUT.parent.mkdir(parents=True, exist_ok=True)
im.save(OUT, optimize=True)
print(OUT)
