"""第五话检查草稿的网页看图与轻量 PDF；不生成正式定稿。"""
from pathlib import Path
import io
import sys
from PIL import Image
import pymupdf

if sys.argv[1:] != ['--draft']:
    raise SystemExit('仅允许 --draft，禁止写正式目录')
root = Path(__file__).resolve().parents[1]
out = root / 'deliverables/review-chapter-05-v3'
pages = [out / 'pages' / 'page-00-cover.png'] + [out / 'pages' / f'page-{n:02d}.png' for n in range(1, 10)]
labels = ['封面','出发','商量路线','企鹅和肩上骑','海底隧道','四人合影','水母','休息','企鹅玩偶','回家']
assert all(p.is_file() for p in pages)
lines = ['# 《今天一起去水族馆》 · 历史检查版', '', '> **历史文件：水族馆现为第六话。请查看 [第六话新版](../review-chapter-06-aquarium/第六话_逐页检查版.md)；本目录与文件名保留供追溯。**', '', '> 封面＋9页；尚未用户验收。水族馆现已确定为第六话；本历史轻量PDF为检查预览，不是最终定稿。', '> 部分对白为制作提案，末页为用户指定原句。', '']
for label, page in zip(labels, pages):
    lines += [f'## {label}', '', f'![{label}](pages/{page.name})', '']
(out / '第五话_逐页检查版.md').write_text('\n'.join(lines), encoding='utf-8')
doc = pymupdf.open()
for page in pages:
    with Image.open(page) as image:
        assert image.size == (1440, 1920)
        thumb = image.convert('RGB').resize((720, 960), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        thumb.save(buf, format='JPEG', quality=88, subsampling=0, optimize=True)
    pdfpage = doc.new_page(width=691.2, height=921.6)
    pdfpage.insert_image(pdfpage.rect, stream=buf.getvalue())
doc.set_metadata({'title':'今天一起去水族馆检查预览（非定稿）', 'subject':'720x960 JPEG quality 88 subsampling 0'})
doc.save(out / '第五话_轻量检查预览.pdf', deflate=True, garbage=4)
doc.close()
print(f'逐页看图及10页轻量检查 PDF: {out}')
