"""只导出第五话居家前置的非定稿检查预览。"""
from pathlib import Path
import io, sys
from PIL import Image
import pymupdf

if sys.argv[1:] != ['--draft']: raise SystemExit('仅允许 --draft')
root = Path(__file__).resolve().parents[1]
out = root / 'deliverables/章节/第六话/review-chapter-05-home'
pages = [out/'pages/page-00-cover.png'] + [out/f'pages/page-{n:02d}.png' for n in range(1,12)]
labels = ['封面（标题待定）','游戏','游戏结束','妹妹摸头','起身找姐姐','姐姐的提议','叫妈妈','姐姐亲脸颊','水族馆提议','小满请求','二弟答应','小满拥抱']
assert all(p.exists() for p in pages)
lines = ['# 第五话居家前置 · 制作中试排', '', '> 非定稿、未经用户验收。画布预筛与视觉复核尚有待办，不能当作正式成品。封面标题和气泡等待用户裁定。', '> 目前增加独立的「叫妈妈」和「二弟答应」两页，保证情节先后；实际封面＋11页。', '']
for label,p in zip(labels,pages): lines += [f'## {label}','',f'![{label}](pages/{p.name})','']
(out/'第五话_制作中试排.md').write_text('\n'.join(lines),encoding='utf-8')
doc=pymupdf.open()
for p in pages:
    with Image.open(p) as image:
        assert image.size==(1440,1920)
        thumb=image.convert('RGB').resize((720,960),Image.Resampling.LANCZOS)
        buf=io.BytesIO(); thumb.save(buf,format='JPEG',quality=88,subsampling=0,optimize=True)
    page=doc.new_page(width=691.2,height=921.6)
    page.insert_image(page.rect,stream=buf.getvalue())
doc.set_metadata({'title':'第五话居家前置制作中试排（非定稿）','subject':'720x960 JPEG quality 88 subsampling 0'})
tmp=out/'preview-tmp.pdf'
doc.save(tmp,deflate=True,garbage=4); doc.close(); tmp.replace(out/'第五话_制作中轻量预览.pdf')
print('试排和轻量预览：12页')
