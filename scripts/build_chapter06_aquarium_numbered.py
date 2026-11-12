"""Label the existing aquarium review as chapter six without changing its nine story pages."""
from pathlib import Path
import io
import os
import sys
from PIL import Image, ImageDraw, ImageFont
import pymupdf

if sys.argv[1:] != ['--draft']:
    raise SystemExit('仅允许 --draft，保留原检查版')
root = Path(__file__).resolve().parents[1]
old = root / 'deliverables/review-chapter-05-v3/pages'
out = root / 'deliverables/章节/第六话/review-chapter-06-aquarium'
pages_dir = out / 'pages'
pages_dir.mkdir(parents=True, exist_ok=True)
with Image.open(old/'page-00-cover.png') as image:
    im = image.convert('RGB')
if im.size != (1440, 1920):
    raise ValueError('封面尺寸异常')
draw = ImageDraw.Draw(im)
font = ImageFont.truetype(str(root/'assets/fonts/NotoSansCJKsc-Bold.otf'), 21)
label = '《二弟的休息日被全家预约了》 第六话'
draw.text((38, 1850), label, font=font, fill='#D9A9A1', stroke_width=2, stroke_fill='#FFF8EE')
im.save(pages_dir/'page-00-cover.png', optimize=True)
for n in range(1,10):
    src = old/f'page-{n:02d}.png'
    dst = pages_dir/src.name
    if not src.is_file():
        raise FileNotFoundError(src)
    link = os.path.relpath(src.resolve(), pages_dir)
    if dst.is_symlink():
        if os.readlink(dst) == link:
            continue
        dst.unlink()
    elif dst.exists():
        raise FileExistsError(dst)
    dst.symlink_to(link)
pages = [pages_dir/'page-00-cover.png'] + [pages_dir/f'page-{n:02d}.png' for n in range(1,10)]
labels = ['封面','出发','商量路线','企鹅和肩上骑','海底隧道','四人合影','水母','休息','企鹅玩偶','回家']
lines = ['# 第六话｜今天一起去水族馆 · 逐页检查版', '', '> 水族馆篇已更正为第六话；封面＋9页。正文沿用原检查版，尚待用户对本话整体验收。', '> 第03页部分对白气泡距离较远，归属需留意；轻量PDF仅供预览，细节请看PNG。', '']
for label, page in zip(labels,pages):
    url = os.path.relpath(page.resolve(),out) if page.is_symlink() else f'pages/{page.name}'
    lines += [f'## {label}', '', f'![{label}]({url})', '']
(out/'第六话_逐页检查版.md').write_text('\n'.join(lines),encoding='utf-8')
doc = pymupdf.open()
for page in pages:
    with Image.open(page) as image:
        if image.size != (1440,1920):
            raise ValueError(f'尺寸异常：{page}')
        thumb = image.convert('RGB').resize((720,960),Image.Resampling.LANCZOS)
        buf = io.BytesIO(); thumb.save(buf,format='JPEG',quality=88,subsampling=0,optimize=True)
    p = doc.new_page(width=691.2,height=921.6)
    p.insert_image(p.rect,stream=buf.getvalue())
doc.set_metadata({'title':'第六话 今天一起去水族馆（检查版）','subject':'720x960 JPEG quality 88 subsampling 0'})
tmp = out/'preview-tmp.pdf'
doc.save(tmp,deflate=True,garbage=4); doc.close(); tmp.replace(out/'第六话_轻量检查预览.pdf')
print('第六话检查版：封面＋9页；旧版保留。')
