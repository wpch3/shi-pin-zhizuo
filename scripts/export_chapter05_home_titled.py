"""导出第五话治愈版检查稿；仅供草稿，沿用 896×1200 原生画幅。"""
from pathlib import Path
import io
import sys
import os
import pymupdf
from PIL import Image

if sys.argv[1:] != ['--draft']:
    raise SystemExit('仅允许 --draft')
root = Path(__file__).resolve().parents[1]
out = root / 'deliverables/review-chapter-05-home-titled'
pages = [out/'pages/page-00-cover.png'] + [out/f'pages/page-{n:02}.png' for n in range(1,18)]
labels = ['封面','一起玩游戏','累了，靠着妹妹','妹妹摸头','抱着妹妹的腿','抱着妹妹撒娇','去找姐姐','姐姐的提议','叫妈妈','姐姐亲一口','姐姐搂肩','姐姐捧脸','明天去水族馆','小满的请求','二弟答应','小满高兴拥抱','再抱一会儿','背着小满']
if not all(p.is_file() for p in pages):
    raise SystemExit('缺少页图')
lines = ['# 第五话｜累了一天，姐姐妹妹和小侄女治愈我','','> 封面＋17页；用户确认正文完工并确定标题。本版仅在已确认的正文版本上为封面排入标题。', '> 本版采用原画的 896×1200 像素出图；看细节以 PNG 为准。','']
for label,p in zip(labels,pages):
    image_url = os.path.relpath(p.resolve(), out) if p.is_symlink() else f'pages/{p.name}'
    lines.extend([f'## {label}','',f'![{label}]({image_url})',''])
(out/'第五话_逐页检查版.md').write_text('\n'.join(lines),encoding='utf-8')
doc=pymupdf.open()
for p in pages:
    with Image.open(p) as image:
        if image.size != (896,1200): raise ValueError(f'尺寸异常：{p}')
        thumb=image.convert('RGB').resize((720,964),Image.Resampling.LANCZOS)
        buf=io.BytesIO(); thumb.save(buf,format='JPEG',quality=88,subsampling=0,optimize=True)
    page=doc.new_page(width=691.2,height=925.44)
    page.insert_image(page.rect,stream=buf.getvalue())
doc.set_metadata({'title':'第五话｜累了一天，姐姐妹妹和小侄女治愈我','subject':'720x964 JPEG quality 88 subsampling 0'})
tmp=out/'preview-tmp.pdf'
doc.save(tmp,deflate=True,garbage=4); doc.close(); tmp.replace(out/'第五话_轻量检查预览.pdf')
print('18页逐页看图与轻量PDF已输出；不重复导出无损备份和ZIP')
