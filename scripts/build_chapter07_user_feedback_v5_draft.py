"""第七话跨页连贯候选：仅替换07原画，文字仍是未审定提案。"""
from pathlib import Path
import io, os, sys
import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFont
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text
if sys.argv[1:] != ['--draft']: raise SystemExit('仅允许 --draft')
r=Path(__file__).resolve().parents[1]; out=r/'deliverables/章节/第七话/review-chapter-07-user-feedback-v5'; out.mkdir(parents=True,exist_ok=True)
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
# 为手机阅读添加纸条原文提示框，不代替纸面上的透视小字。
d=ImageDraw.Draw(im); note_font=ImageFont.truetype(str(font),32)
d.rounded_rectangle((50,105,555,260),radius=16,fill='#F8F4EB',outline='#292B2C',width=3)
d.text((75,120),'纸条：',font=note_font,fill='#292B2C')
d.text((75,164),'妈妈，饭菜留好了。',font=note_font,fill='#292B2C')
d.text((75,208),'记得热一热。',font=note_font,fill='#292B2C')
f=ImageFont.truetype(str(font),27); center=(1110,145);lay=measure_speech_text(d,['有你们在，我真幸福。'],center,f,27);shape=oval_speech(center,lay['bubble_size'],(1040,500),tail_length=35,tail_width=28,bend=2);d.polygon(shape,fill='#F8F4EB');d.line(shape+[shape[0]],fill='#292B2C',width=3,joint='curve')
for x,y,line in lay['positions']: d.text((x,y),line,font=f,fill='#292B2C')
d.text((1260,1855),'07 / 07',font=ImageFont.truetype(str(font),20),fill='#292B2C',stroke_width=2,stroke_fill='#F8F4EB')
(out/'pages').mkdir(exist_ok=True); im.save(out/'pages/page-07.png',optimize=True)
# 05 and 06 are new illustrations; add the existing dialogue as speech balloons.
def add_speech_page(number, source, dialogue):
 with Image.open(r/source) as img:
  if img.size != (896,1200): raise ValueError((source,img.size))
  page=img.convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
 d=ImageDraw.Draw(page); boxes=[]
 for lines,center,target in dialogue:
  f=ImageFont.truetype(str(font),29); lay=measure_speech_text(d,lines,center,f,29); box=lay['box']
  assert 0<=box[0]<box[2]<=W and 0<=box[1]<box[3]<=H
  assert all(box[2]<=b[0] or b[2]<=box[0] or box[3]<=b[1] or b[3]<=box[1] for b in boxes);boxes.append(box)
  shape=oval_speech(center,lay['bubble_size'],target,tail_length=38,tail_width=28,bend=2);d.polygon(shape,fill='#F8F4EB');d.line(shape+[shape[0]],fill='#292B2C',width=3,joint='curve')
  for x,y,line in lay['positions']:d.text((x,y),line,font=f,fill='#292B2C')
 d.text((1260,1855),f'{number:02} / 07',font=ImageFont.truetype(str(font),20),fill='#292B2C',stroke_width=2,stroke_fill='#F8F4EB')
 page.save(out/f'pages/page-{number:02}.png',optimize=True)
 print(number,boxes)
add_speech_page(5,'art/chapter-07-user-repair/shot-05-v1.png',[
 (['小叔，','今天的菜好丰盛！'],(325,130),(450,420)),
 (['喜欢就多吃点。'],(1190,135),(1010,270))])
add_speech_page(6,'art/chapter-07-user-repair/shot-06-v5.png',[
 (['给妈妈留一份。'],(220,130),(450,310)),
 (['我再写张纸条。'],(1140,130),(1080,440))])
paths=[r/'deliverables/章节/第七话/review-chapter-07-dialogue-draft/pages'/('page-00-cover.png' if i==0 else f'page-{i:02}.png') for i in range(5)]+[out/'pages/page-05.png',out/'pages/page-06.png',out/'pages/page-07.png']
lines=['# 第七话｜用户反馈返修试排 v5（待复核）','','> 05重生画面，小满直接说话；06重生画面尝试对齐画风色彩；07保留原画，妈妈的候选对白改成第一人称。其余页面沿用v4；对白和纸条为提案，封面标题未定，未覆盖旧版本。','']
pdf=pymupdf.open()
for i,p in enumerate(paths):
 label='封面' if not i else f'第{i:02}页';lines += [f'## {label}','',f'![{label}]({os.path.relpath(p,out)})','']
 with Image.open(p) as image: preview=image.convert('RGB').resize((720,960),Image.Resampling.LANCZOS)
 buf=io.BytesIO();preview.save(buf,format='JPEG',quality=90,subsampling=0,optimize=True);page=pdf.new_page(width=691.2,height=921.6);page.insert_image(page.rect,stream=buf.getvalue())
pdf.set_metadata({'title':'第七话 用户反馈返修试排v5 待复核'});pdf.save(out/'第七话_返修轻量试排.pdf',deflate=True,garbage=4);pdf.close();(out/'第七话_返修试排.md').write_text('\n'.join(lines),encoding='utf8')
