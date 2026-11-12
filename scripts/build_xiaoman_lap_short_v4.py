"""User-approved v3 images; add the uncle's suggested line to page 3 only."""
from pathlib import Path
import io, os, sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont, ImageChops
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text
if sys.argv[1:] != ['--draft']: raise SystemExit('only --draft')
r=Path(__file__).resolve().parents[1]; out=r/'deliverables/review-xiaoman-lap-short-v4'; pages=out/'pages';pages.mkdir(parents=True,exist_ok=True)
sources=[r/'deliverables/review-xiaoman-lap-short-v1/pages/01.png',r/'deliverables/review-xiaoman-lap-short-v1/pages/02.png',r/'deliverables/review-xiaoman-lap-short-v1/pages/03.png',r/'art/xiaoman-lap-short-v3/04-gentle-face-only.png']
im=Image.open(sources[2]).convert('RGB'); d=ImageDraw.Draw(im)
font=ImageFont.truetype(str(r/'assets/fonts/NotoSansCJKsc-Bold.otf'),37)
lines=['小满，我想趴一会儿，','可以吗？'];center=(980,420);target=(515,1080)
layout=measure_speech_text(d,lines,center,font,37);shape=oval_speech(center,layout['bubble_size'],target,tail_length=52,tail_width=32,bend=1)
d.polygon(shape,fill='#f8f4eb');d.line(shape+[shape[0]],fill='#302c29',width=3,joint='curve')
for x,y,line in layout['positions']:d.text((x,y),line,font=font,fill='#302c29')
p=pages/'03.png';im.save(p,optimize=True); sources[2]=p
lines=['# 小满膝枕短篇｜台词补充版','','画面按用户认可的 v3 保留；第3图新增台词为试排，第4图姿势与表情不变。','']
for i,p in enumerate(sources,1):lines += [f'## 第{i}图','',f'![第{i}图]({os.path.relpath(p,out)})','']
(out/'逐页看图.md').write_text('\n'.join(lines),encoding='utf8')
for light in (False, True):
 pdf=pymupdf.open()
 for p in sources:
  img=Image.open(p).convert('RGB');w,h=img.size
  if light:
   img.thumbnail((720,1400),Image.Resampling.LANCZOS);buf=io.BytesIO();img.save(buf,'JPEG',quality=90,subsampling=0,optimize=True);data=buf.getvalue()
  else:data=p.read_bytes()
  page=pdf.new_page(width=691.2,height=691.2*h/w);page.insert_image(page.rect,stream=data)
 pdf.set_metadata({'title':'小满膝枕短篇 台词补充版'});pdf.save(out/('小满膝枕短篇_台词补充_轻量.pdf' if light else '小满膝枕短篇_台词补充_完整版.pdf'),deflate=True,garbage=4);pdf.close()
for p in out.glob('*.pdf'):
 with pymupdf.open(p) as pdf: assert len(pdf)==4
print('4 pages built')
