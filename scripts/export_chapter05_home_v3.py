"""只导出第五话居家前置的非定稿检查预览。"""
from pathlib import Path
import io, sys, zipfile
from pdf_export import save_lossless_pdf_from_paths
from PIL import Image
import pymupdf

if sys.argv[1:] != ['--draft']: raise SystemExit('仅允许 --draft')
root = Path(__file__).resolve().parents[1]
out = root / 'deliverables/章节/第五话/review-chapter-05-home-v3'
pages = [out/'pages/page-00-cover.png'] + [out/f'pages/page-{n:02d}.png' for n in range(1,12)]
labels = ['封面（标题待定）','游戏','游戏结束','妹妹摸头','起身找姐姐','姐姐的提议','叫妈妈','姐姐亲脸颊','水族馆提议','小满请求','二弟答应','小满拥抱']
assert all(p.exists() for p in pages)
lines = ['# 第五话居家前置 · 检查版', '', '> 非定稿、未经用户验收。本版供用户逐页验收，不是最终定稿。封面标题和气泡等待用户裁定。', '> 目前增加独立的「叫妈妈」和「二弟答应」两页，保证情节先后；实际封面＋11页。', '']
for label,p in zip(labels,pages):
    # GitHub 的图片 URL 不会按文件系统方式跟随仓库内符号链接，直接指向历史页。
    image_url = f'../review-chapter-05-home/pages/{p.name}' if p.is_symlink() else f'pages/{p.name}'
    lines += [f'## {label}','',f'![{label}]({image_url})','']
(out/'第五话_逐页检查版.md').write_text('\n'.join(lines),encoding='utf-8')
doc=pymupdf.open()
for p in pages:
    with Image.open(p) as image:
        assert image.size==(1440,1920)
        thumb=image.convert('RGB').resize((720,960),Image.Resampling.LANCZOS)
        buf=io.BytesIO(); thumb.save(buf,format='JPEG',quality=88,subsampling=0,optimize=True)
    page=doc.new_page(width=691.2,height=921.6)
    page.insert_image(page.rect,stream=buf.getvalue())
doc.set_metadata({'title':'第五话居家前置检查版（非定稿）','subject':'720x960 JPEG quality 88 subsampling 0'})
tmp=out/'preview-tmp.pdf'
doc.save(tmp,deflate=True,garbage=4); doc.close(); tmp.replace(out/'第五话_轻量检查预览.pdf')
print('试排和轻量预览：12页')

# 检查用无损备份和图片包：复用现有 PNG，不另行生图。
save_lossless_pdf_from_paths(pages, out/'第五话_检查版无损备份.pdf', resolution=150)
with zipfile.ZipFile(out/'第五话_检查版图片.zip', 'w', compression=zipfile.ZIP_STORED) as z:
    for p in pages: z.write(p, arcname=p.name)
print('无损PDF与图片ZIP已导出')
