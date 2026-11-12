"""Experimental page 02: typeset the verified algebra; not a full chapter build."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'art/chapter-08-reset-v1/02-solution.png'
OUT = ROOT / 'deliverables/review-chapter-08-reset-v2/page-02-typeset-preview.png'
FONT = ROOT / 'assets/fonts/NotoSansCJKsc-Bold.otf'
im = Image.open(SOURCE).convert('RGB')
if im.size != (848, 1264):
    raise ValueError(f'Unexpected page size: {im.size}')
draw = ImageDraw.Draw(im)
font = ImageFont.truetype(str(FONT), 21)
math_font = ImageFont.truetype(str(FONT), 22)
for rect, lines in [((20, 55, 410, 166), ['辰希：先用恒等式变形，', '代入，答案是十八。']),
                    ((438, 55, 828, 166), ['老师：思路很清楚，', '大家记一下这个变形。'])]:
    draw.ellipse(rect, fill='#fffdf7', outline='#34383a', width=2)
    cx = (rect[0] + rect[2]) / 2
    for y, text in zip((70, 106), lines):
        box = draw.textbbox((0, 0), text, font=font)
        width = box[2] - box[0]
        if width > rect[2] - rect[0] - 32:
            raise ValueError(f'Dialogue too wide: {text}')
        draw.text((cx - width / 2, y), text, font=font, fill='#242a2c')
lines = [
    'x³＋y³＋z³－3xyz',
    '＝(x＋y＋z)[(x＋y＋z)²－3(xy＋yz＋zx)]',
    '＝6×(36－33)＝18',
]
for y, text in zip((386, 426, 466), lines):
    box = draw.textbbox((0, 0), text, font=math_font)
    if 78 + box[2] - box[0] > 812:
        raise ValueError(f'Math line too wide: {text}')
    draw.text((78, y), text, font=math_font, fill='#f6f5e7')
OUT.parent.mkdir(parents=True, exist_ok=True)
im.save(OUT, optimize=True)
print(OUT)
