"""第七话 v7 候选：封面标题和 03 页；原 v6 其余页原样引用。"""
from pathlib import Path
import io, os, sys, re
import pymupdf
from PIL import Image, ImageDraw, ImageFont, ImageChops
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text
if sys.argv[1:] != ['--draft']: raise SystemExit('仅允许 --draft')
r=Path(__file__).resolve().parents[1]
out=r/'deliverables/章节/第七话/review-chapter-07-user-feedback-v7'; pages=out/'pages';pages.mkdir(parents=True,exist_ok=True)
font=r/'assets/fonts/NotoSansCJKsc-Bold.otf'; W,H=1440,1920
# Add a separate title band instead of covering the existing cover artwork.
cover=Image.open(r/'deliverables/章节/第七话/review-chapter-07-dialogue-draft/pages/page-00-cover.png').convert('RGB')
coverout=Image.new('RGB',(W,H+170),'#f9f3e8');coverout.paste(cover,(0,170));d=ImageDraw.Draw(coverout)
f=ImageFont.truetype(str(font),68)
d.text((W//2,78),'一起做晚饭',font=f,fill='#604a3e',anchor='mm')
d.line((460,143,980,143),fill='#c9ad8c',width=3)
coverout.save(pages/'page-00-cover.png',optimize=True)
# New art retains aspect ratio: pale side margins accommodate the different image aspect.
source=Image.open(r/'art/chapter-07-user-repair-v7/shot-03-smiles.png').convert('RGB')
w=round(source.width*H/source.height)
im=Image.new('RGB',(W,H),'#f7f0e4');im.paste(source.resize((w,H),Image.Resampling.LANCZOS),((W-w)//2,0))
d=ImageDraw.Draw(im); f=ImageFont.truetype(str(font),32)
for lines,center,target in [(['我来摆餐具！'],(1090,125),(1000,650)),(['好，我帮你数一数。'],(370,275),(400,640))]:
 lay=measure_speech_text(d,lines,center,f,32); shape=oval_speech(center,lay['bubble_size'],target,tail_length=35,tail_width=28,bend=2)
 d.polygon(shape,fill='#F8F4EB');d.line(shape+[shape[0]],fill='#292B2C',width=3,joint='curve')
 for x,y,line in lay['positions']: d.text((x,y),line,font=f,fill='#292B2C')
d.text((1260,1855),'03 / 07',font=ImageFont.truetype(str(font),20),fill='#292B2C',stroke_width=2,stroke_fill='#F8F4EB')
im.save(pages/'page-03.png',optimize=True)
old=r/'deliverables/章节/第七话/review-chapter-07-user-feedback-v6/第七话_返修试排.md'
oldpaths=[(old.parent/p).resolve() for p in re.findall(r'!\[[^]]*\]\(([^)]+)\)',old.read_text())]
assert len(oldpaths)==8
paths=oldpaths.copy();paths[0]=pages/'page-00-cover.png';paths[3]=pages/'page-03.png'
lines=['# 第七话｜返修试排 v7（待审）','','> 封面标题《一起做晚饭》是提案，待用户确认，并非正式定名。第03页为表情和摆碗动作候选；对白沿用v6。01、02、04—07页直接沿用v6图源；第七话尚未定稿。','']
for i,p in enumerate(paths):
 label='封面' if i==0 else f'第{i:02}页';lines += ['## '+label,'',f'![{label}]({os.path.relpath(p,out)})','']
(out/'第七话_返修试排.md').write_text('\n'.join(lines),encoding='utf8')
for light in (False,True):
 doc=pymupdf.open()
 for p in paths:
  with Image.open(p) as img:
   img=img.convert('RGB');w,h=img.size
   if light:
    img.thumbnail((720,1050),Image.Resampling.LANCZOS); buf=io.BytesIO(); img.save(buf,format='JPEG',quality=90,subsampling=0,optimize=True);data=buf.getvalue()
   else: data=p.read_bytes()
  page=doc.new_page(width=691.2,height=691.2*h/w);page.insert_image(page.rect,stream=data)
 doc.set_metadata({'title':'第七话 返修试排v7 标题待确认'});doc.save(out/('第七话_返修轻量试排.pdf' if light else '第七话_返修完整版.pdf'),deflate=True,garbage=4);doc.close()
with pymupdf.open(out/'第七话_返修完整版.pdf') as doc:
 assert len(doc)==8
 for page,p in zip(doc,paths):
  refs=page.get_images(full=True);assert len(refs)==1
  pix=pymupdf.Pixmap(doc,refs[0][0]);pix=pymupdf.Pixmap(pymupdf.csRGB,pix) if pix.n!=3 else pix
  actual=Image.frombytes('RGB',(pix.width,pix.height),pix.samples); expected=Image.open(p).convert('RGB')
  assert expected.size==actual.size and ImageChops.difference(expected,actual).getbbox() is None,p
with pymupdf.open(out/'第七话_返修轻量试排.pdf') as doc: assert len(doc)==8
print('8页完整版PDF图像像素与各图源相同；01、02、04—07图源原样沿用v6。')
