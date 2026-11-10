"""New chapter six review: change only the redrawn return page, preserve prior version."""
from pathlib import Path
import io,os,sys
import pymupdf
from PIL import Image,ImageDraw,ImageFont
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text
if sys.argv[1:] != ['--draft']: raise SystemExit('仅允许 --draft')
root=Path(__file__).resolve().parents[1]
old=root/'deliverables/review-chapter-06-aquarium-dialogue/pages'
out=root/'deliverables/review-chapter-06-aquarium-arm-link-attempt'
pages_dir=out/'pages';pages_dir.mkdir(parents=True,exist_ok=True)
font_path=root/'assets/fonts/NotoSansCJKsc-Bold.otf'
with Image.open(root/'art/chapter-06-aquarium-repair/return-home-v5.png') as image:
 if image.size != (896,1200): raise ValueError('原图尺寸异常')
 im=image.convert('RGB').resize((1440,1920),Image.Resampling.LANCZOS)
draw=ImageDraw.Draw(im);font=ImageFont.truetype(str(font_path),30)
lines=['能和你们一直在一起……','我真的是最幸福的人。']
center=(1040,210);target=(750,465)
layout=measure_speech_text(draw,lines,center,font,30)
shape=oval_speech(center,layout['bubble_size'],target,tail_length=30,tail_width=28,bend=2)
draw.polygon(shape,fill='#F8F4EB');draw.line(shape+[shape[0]],fill='#292B2C',width=3,joint='curve')
for x,y,line in layout['positions']: draw.text((x,y),line,font=font,fill='#292B2C')
draw.text((1290,1860),'09 / 09',font=ImageFont.truetype(str(font_path),20),fill='#F8F4EB',stroke_width=2,stroke_fill='#292B2C')
im.save(pages_dir/'page-09.png',optimize=True)
for n in range(9):
 name='page-00-cover.png' if n==0 else f'page-{n:02}.png'
 src=old/name;dest=pages_dir/name
 if not src.is_file(): raise FileNotFoundError(src)
 link=os.path.relpath(src.resolve(),pages_dir)
 if dest.is_symlink():
  if os.readlink(dest)==link: continue
  dest.unlink()
 elif dest.exists(): raise FileExistsError(dest)
 dest.symlink_to(link)
pages=[pages_dir/'page-00-cover.png']+[pages_dir/f'page-{n:02}.png' for n in range(1,10)]
labels=['封面','出发','商量路线','企鹅和肩上骑','海底隧道','四人合影','水母','休息','企鹅玩偶','回家（双挽尝试，未完成）']
md=['# 第六话｜今天一起去水族馆 · 末页双挽尝试（未完成）','','> 第09页重画调整画风与上色，保留原结尾对白；姐姐和妹妹均有手接触二弟手臂，但姐姐更像扶着而非清晰挽住，妹妹手臂部分遮挡；双挽动作尚未完整实现，不能作为最终修复。第03页标注仍待确认，旧版保留。','']
for label,page in zip(labels,pages):
 url=os.path.relpath(page.resolve(),out) if page.is_symlink() else f'pages/{page.name}'
 md += [f'## {label}','',f'![{label}]({url})','']
(out/'第六话_逐页检查版.md').write_text('\n'.join(md),encoding='utf8')
doc=pymupdf.open()
for page in pages:
 with Image.open(page) as image:
  if image.size!=(1440,1920): raise ValueError(page)
  thumb=image.convert('RGB').resize((720,960),Image.Resampling.LANCZOS);buf=io.BytesIO();thumb.save(buf,format='JPEG',quality=88,subsampling=0,optimize=True)
 p=doc.new_page(width=691.2,height=921.6);p.insert_image(p.rect,stream=buf.getvalue())
doc.set_metadata({'title':'第六话 今天一起去水族馆 末页双挽尝试（未完成）','subject':'720x960 JPEG quality 88 subsampling 0'})
tmp=out/'preview-tmp.pdf';doc.save(tmp,deflate=True,garbage=4);doc.close();tmp.replace(out/'第六话_轻量检查预览.pdf')
print('第六话回家页风格候选已试排，气泡框：',layout['box'])
