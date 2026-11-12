"""膝枕短篇工作试排；第四图朝向仍待确认，非定稿。"""
from pathlib import Path
import io, os, sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text
if sys.argv[1:] != ['--draft']: raise SystemExit('only --draft')
r=Path(__file__).resolve().parents[1];o=r/'deliverables/review-xiaoman-lap-short-v1';pages=o/'pages';pages.mkdir(parents=True,exist_ok=True)
sources=['01-invitation.png','02-offer.png','03-rest.png','04-turn-v2.png']
speech={1:[(['小叔，来这里！'],(450,250),(450,650))],2:[(['小满的膝枕', '借给你！'],(425,260),(450,680)),(['好，谢谢小满。'],(1050,320),(940,700))],3:[(['小叔，休息一下吧。'],(410,250),(410,680))]}
font=ImageFont.truetype(str(r/'assets/fonts/NotoSansCJKsc-Bold.otf'),37)
for n,src in enumerate(sources,1):
 with Image.open(r/'art/xiaoman-lap-short-v1'/src) as original:
  w,h=original.size;im=original.convert('RGB').resize((1440,round(h*1440/w)),Image.Resampling.LANCZOS)
 d=ImageDraw.Draw(im)
 for lines,center,target in speech.get(n,[]):
  layout=measure_speech_text(d,lines,center,font,37);shape=oval_speech(center,layout['bubble_size'],target,tail_length=48,tail_width=32,bend=1)
  d.polygon(shape,fill='#f8f4eb');d.line(shape+[shape[0]],fill='#302c29',width=3,joint='curve')
  for x,y,line in layout['positions']:d.text((x,y),line,font=font,fill='#302c29')
 im.save(pages/f'{n:02}.png',optimize=True)
lines=['# 小满与小叔｜膝枕短篇四图工作试排','','> 非定稿。第04图的头部朝向被遮挡，无法清楚看出是否朝向小满腹部，需继续确认或重做。对白为试排提案，尚待用户确认；不属于第九话。','']
for n in range(1,5): lines += [f'## 第{n}图','',f'![第{n}图](pages/{n:02}.png)','']
(o/'逐页看图.md').write_text('\n'.join(lines),encoding='utf8')
for light in (True,False):
 pdf=pymupdf.open()
 for n in range(1,5):
  p=pages/f'{n:02}.png'; im=Image.open(p).convert('RGB'); w,h=im.size
  if light:
   im.thumbnail((720,1400),Image.Resampling.LANCZOS); b=io.BytesIO();im.save(b,'JPEG',quality=90,subsampling=0,optimize=True);data=b.getvalue()
  else:data=p.read_bytes()
  page=pdf.new_page(width=691.2,height=691.2*h/w);page.insert_image(page.rect,stream=data)
 pdf.set_metadata({'title':'小满膝枕短篇 工作试排 第四图待确认'});pdf.save(o/('小满膝枕短篇_轻量工作试排.pdf' if light else '小满膝枕短篇_完整版工作试排.pdf'),deflate=True,garbage=4);pdf.close()
for p in o.glob('*.pdf'):
 with pymupdf.open(p) as doc: assert len(doc)==4
print('4 pages, proportions preserved; final turn direction remains ambiguous')
