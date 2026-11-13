"""膝枕短篇v3: 前三张复用，第四张仅表情局部修订。"""
from pathlib import Path
import os, io, sys
import pymupdf
from PIL import Image, ImageChops
if sys.argv[1:] != ['--draft']: raise SystemExit('only --draft')
r=Path(__file__).resolve().parents[1];out=r/'deliverables/短篇与个人回/小满膝枕/review-xiaoman-lap-short-v3';out.mkdir(parents=True,exist_ok=True)
original=r/'art/xiaoman-lap-short-v2/04-turn-new-view.png'; fixed=r/'art/xiaoman-lap-short-v3/04-gentle-face-only.png'
a=Image.open(original).convert('RGB');b=Image.open(fixed).convert('RGB');assert a.size==b.size
bbox=ImageChops.difference(a,b).getbbox();assert bbox and bbox[0]>=210 and bbox[1]>=365 and bbox[2]<=320 and bbox[3]<=465,bbox
paths=[r/f'deliverables/短篇与个人回/小满膝枕/review-xiaoman-lap-short-v1/pages/{n:02}.png' for n in range(1,4)]+[fixed]
lines=['# 小满与小叔｜膝枕短篇 v3（待审）','','> 第04图按用户回传截图选用原构图，仅局部调整小满表情；前三图沿用v1。对白为试排，整篇尚待用户审阅。不自动算第九话。','']
for n,p in enumerate(paths,1):lines += [f'## 第{n}图','',f'![第{n}图]({os.path.relpath(p,out)})','']
(out/'逐页看图.md').write_text('\n'.join(lines),encoding='utf8')
for light in (False,True):
 doc=pymupdf.open()
 for p in paths:
  with Image.open(p) as img:
   img=img.convert('RGB');w,h=img.size
   if light:
    img.thumbnail((720,1400),Image.Resampling.LANCZOS);buf=io.BytesIO();img.save(buf,format='JPEG',quality=90,subsampling=0,optimize=True);data=buf.getvalue()
   else:data=p.read_bytes()
  page=doc.new_page(width=691.2,height=691.2*h/w);page.insert_image(page.rect,stream=data)
 doc.set_metadata({'title':'小满膝枕短篇 v3 待审'});doc.save(out/('小满膝枕短篇_v3_轻量试排.pdf' if light else '小满膝枕短篇_v3_完整版.pdf'),deflate=True,garbage=4);doc.close()
with pymupdf.open(out/'小满膝枕短篇_v3_完整版.pdf') as doc:
 assert len(doc)==4
 for page,p in zip(doc,paths):
  refs=page.get_images(full=True);assert len(refs)==1
  pix=pymupdf.Pixmap(doc,refs[0][0]);pix=pymupdf.Pixmap(pymupdf.csRGB,pix) if pix.n!=3 else pix
  im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);expected=Image.open(p).convert('RGB');assert im.size==expected.size and ImageChops.difference(im,expected).getbbox() is None,p
print('4 pages full PDF source-pixel check passed; 04 diff bbox',bbox)
