"""第七话跨页连贯候选：仅替换07原画，文字仍是未审定提案。"""
from pathlib import Path
import io, os, sys
import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFont
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text
if sys.argv[1:] != ['--draft']: raise SystemExit('仅允许 --draft')
r=Path(__file__).resolve().parents[1]; out=r/'deliverables/章节/第七话/review-chapter-07-continuity-v2'; out.mkdir(parents=True,exist_ok=True)
font=r/'assets/fonts/NotoSansCJKsc-Bold.otf'; W,H=1440,1920
with Image.open(r/'art/chapter-07-cooking-v6/shot-07.png') as src:
 if src.size!=(896,1200):raise ValueError(src.size)
 im=src.convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
# 纸条字为排版提案，透视落在纸面中；绝非生图原有文字。
text=Image.new('RGBA',(620,240));d=ImageDraw.Draw(text);f=ImageFont.truetype(str(font),54)
d.text((15,20),'妈妈，饭菜留好了。',font=f,fill=(79,67,61,255));d.text((15,110),'记得热一热。',font=f,fill=(79,67,61,255))
k=W/896; target=[(319*k,918*k),(459*k,968*k),(342*k,1072*k),(190*k,1001*k)];source=[(0,0),(620,0),(620,240),(0,240)];a=[];b=[]
for (x,y),(u,v) in zip(target,source):
 a.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);b.extend([u,v])
layer=text.transform((W,H),Image.Transform.PERSPECTIVE,np.linalg.solve(np.asarray(a),np.asarray(b)),Image.Resampling.BICUBIC);im.paste(layer,(0,0),layer)
d=ImageDraw.Draw(im); f=ImageFont.truetype(str(font),27); center=(1110,145);lay=measure_speech_text(d,['你们真贴心。'],center,f,27);shape=oval_speech(center,lay['bubble_size'],(1040,500),tail_length=35,tail_width=28,bend=2);d.polygon(shape,fill='#F8F4EB');d.line(shape+[shape[0]],fill='#292B2C',width=3,joint='curve')
for x,y,line in lay['positions']: d.text((x,y),line,font=f,fill='#292B2C')
d.text((1260,1855),'07 / 07',font=ImageFont.truetype(str(font),20),fill='#292B2C',stroke_width=2,stroke_fill='#F8F4EB')
(out/'pages').mkdir(exist_ok=True); im.save(out/'pages/page-07.png',optimize=True)
paths=[r/'deliverables/章节/第七话/review-chapter-07-dialogue-draft/pages'/('page-00-cover.png' if i==0 else f'page-{i:02}.png') for i in range(7)]+[out/'pages/page-07.png']
lines=['# 第七话｜连贯性返修试排 v2（未验收）','','> 仅更换第07页：新生图与第06页厨房、微波炉和餐食尽量对齐；对白和纸条是未审定提案。其他页沿用此前试排，封面标题未定。03读序、05标注、06纸条及全话细节仍待复核。','']
pdf=pymupdf.open()
for i,p in enumerate(paths):
 label='封面' if not i else f'第{i:02}页';lines += [f'## {label}','',f'![{label}]({os.path.relpath(p,out)})','']
 with Image.open(p) as image: preview=image.convert('RGB').resize((720,960),Image.Resampling.LANCZOS)
 buf=io.BytesIO();preview.save(buf,format='JPEG',quality=90,subsampling=0,optimize=True);page=pdf.new_page(width=691.2,height=921.6);page.insert_image(page.rect,stream=buf.getvalue())
pdf.set_metadata({'title':'第七话 连贯性返修试排 v2 非定稿'});pdf.save(out/'第七话_连贯性轻量试排.pdf',deflate=True,garbage=4);pdf.close();(out/'第七话_连贯性试排.md').write_text('\n'.join(lines),encoding='utf-8')
