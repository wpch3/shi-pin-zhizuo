"""Add the user-approved title to the cover, preserving the approved chapter pages."""
from pathlib import Path
import os
import sys
from PIL import Image, ImageDraw, ImageFont

if sys.argv[1:] != ['--draft']:
    raise SystemExit('仅允许 --draft')
root = Path(__file__).resolve().parents[1]
source = root / 'deliverables/章节/第五话/review-chapter-05-home-recovery-v3/pages'
out = root / 'deliverables/章节/第五话/review-chapter-05-home-titled/pages'
if out.exists() and any(out.iterdir()):
    raise SystemExit('第五话确认版已有页面；为保护作品，禁止原地重建。请复制脚本并使用新的输出目录。')
out.mkdir(parents=True, exist_ok=True)
font = root / 'assets/fonts/NotoSansCJKsc-Bold.otf'
with Image.open(source/'page-00-cover.png') as original:
    im = original.convert('RGB')
if im.size != (896,1200):
    raise ValueError('Unexpected cover size')
draw = ImageDraw.Draw(im)
title_font = ImageFont.truetype(str(font), 34)
for y, line in [(13, '累了一天，'), (57, '姐姐妹妹和小侄女治愈我')]:
    draw.text((22,y),line,font=title_font,fill='#E9BD4F',stroke_width=3,stroke_fill='#292B2C')
small_font = ImageFont.truetype(str(font), 13)
draw.text((22,1172), '《二弟的休息日被全家预约了》 第五话', font=small_font, fill='#9B6561', stroke_width=1, stroke_fill='#FFF8EE')
im.save(out/'page-00-cover.png', optimize=True)
for n in range(1,18):
    name = f'page-{n:02}.png'
    dest = out/name
    target = os.path.relpath((source/name).resolve(), out)
    if dest.is_symlink():
        if os.readlink(dest) == target:
            continue
        dest.unlink()
    elif dest.exists():
        raise FileExistsError(f'不覆盖既有正文: {dest}')
    dest.symlink_to(target)
print('标题封面已排版；17页正文复用原图。')
