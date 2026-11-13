"""导出第五话治愈版检查稿；仅供草稿，沿用 896×1200 原生画幅。"""
from pathlib import Path
import io
import sys
import zipfile
import pymupdf
from PIL import Image
from pdf_export import save_lossless_pdf_from_paths

if sys.argv[1:] != ['--draft']:
    raise SystemExit('仅允许 --draft')
root = Path(__file__).resolve().parents[1]
out = root / 'deliverables/章节/第五话/review-chapter-05-home-recovery'
pages = [out/'pages/page-00-cover.png'] + [out/f'pages/page-{n:02}.png' for n in range(1,18)]
labels = ['封面（标题待定）','一起玩游戏','累了，靠着妹妹','妹妹摸头','抱着妹妹的腿','抱着妹妹撒娇','去找姐姐','姐姐的提议','叫妈妈','姐姐亲一口','姐姐搂肩','姐姐捧脸','明天去水族馆','小满的请求','二弟答应','小满高兴拥抱','再抱一会儿','背着小满']
if not all(p.is_file() for p in pages):
    raise SystemExit('缺少页图')
lines = ['# 第五话｜累了一天的治愈 · 逐页检查版','','> 封面＋17页；非定稿，封面标题待用户裁定。已有画面保留，新增互动已按剧情链插入。', '> 本版采用原画的 896×1200 像素出图；看细节以 PNG 为准。','']
for label,p in zip(labels,pages):
    lines.extend([f'## {label}','',f'![{label}](pages/{p.name})',''])
(out/'第五话_逐页检查版.md').write_text('\n'.join(lines),encoding='utf-8')
doc=pymupdf.open()
for p in pages:
    with Image.open(p) as image:
        if image.size != (896,1200): raise ValueError(f'尺寸异常：{p}')
        thumb=image.convert('RGB').resize((720,964),Image.Resampling.LANCZOS)
        buf=io.BytesIO(); thumb.save(buf,format='JPEG',quality=88,subsampling=0,optimize=True)
    page=doc.new_page(width=691.2,height=925.44)
    page.insert_image(page.rect,stream=buf.getvalue())
doc.set_metadata({'title':'第五话治愈版检查稿（非定稿）','subject':'720x964 JPEG quality 88 subsampling 0'})
tmp=out/'preview-tmp.pdf'
doc.save(tmp,deflate=True,garbage=4); doc.close(); tmp.replace(out/'第五话_轻量检查预览.pdf')
tmp=out/'lossless-tmp.pdf'
save_lossless_pdf_from_paths(pages,tmp,resolution=150)
tmp.replace(out/'第五话_检查版无损备份.pdf')
tmp=out/'images-tmp.zip'
with zipfile.ZipFile(tmp, 'w', compression=zipfile.ZIP_STORED) as archive:
    for p in pages:
        archive.write(p, arcname=p.name)
tmp.replace(out/'第五话_检查版图片.zip')
print('18页 PNG、轻量PDF、无损PDF和图片ZIP已输出')
