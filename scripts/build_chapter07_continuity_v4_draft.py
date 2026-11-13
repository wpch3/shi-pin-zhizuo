"""第七话试排 v4：06 按原图比例排字；07 沿用 v3，旧版保留。"""
from pathlib import Path
import io, os, re, sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text
if sys.argv[1:] != ['--draft']: raise SystemExit('仅允许 --draft')
root=Path(__file__).resolve().parents[1]; out=root/'deliverables/章节/第七话/review-chapter-07-continuity-v4'; (out/'pages').mkdir(parents=True,exist_ok=True)
font=root/'assets/fonts/NotoSansCJKsc-Bold.otf'; source=root/'art/chapter-07-cooking-v6/shot-06-v2.png'
with Image.open(source) as image: im=image.convert('RGB')
if im.size != (848,1264): raise ValueError(f'图片尺寸变化，请重新定位排字: {im.size}')
d=ImageDraw.Draw(im);f=ImageFont.truetype(str(font),19); boxes=[]
for lines,center,target in [(['给妈妈留一份。'],(160,96),(220,290)),(['我再写张纸条。'],(692,140),(710,310))]:
 lay=measure_speech_text(d,lines,center,f,19); box=lay['box']
 if not (0<=box[0]<box[2]<=im.width and 0<=box[1]<box[3]<=im.height): raise ValueError(box)
 for a in boxes:
  if not (box[2]<=a[0] or a[2]<=box[0] or box[3]<=a[1] or a[3]<=box[1]): raise ValueError((box,a))
 boxes.append(box);shape=oval_speech(center,lay['bubble_size'],target,tail_length=24,tail_width=20,bend=2)
 d.polygon(shape,fill='#F8F4EB');d.line(shape+[shape[0]],fill='#292B2C',width=2,joint='curve')
 for x,y,line in lay['positions']: d.text((x,y),line,font=f,fill='#292B2C')
d.text((744,1225),'06 / 07',font=ImageFont.truetype(str(font),13),fill='#292B2C',stroke_width=1,stroke_fill='#F8F4EB')
im.save(out/'pages/page-06.png',optimize=True)
paths=[root/'deliverables/章节/第七话/review-chapter-07-dialogue-draft/pages'/('page-00-cover.png' if i==0 else f'page-{i:02}.png') for i in range(6)]+[out/'pages/page-06.png',root/'deliverables/章节/第七话/review-chapter-07-continuity-v3/pages/page-07.png']
lines=['# 第七话｜连贯性返修试排 v4（未验收）','','> 第06页采用848×1264的重生候选并按原比例排字，PDF的第06页相应更窄，不裁切、不拉伸；第07页沿用v3的纸条提示框。对白与纸条内容是未审定提案；封面标题未定，所有页面待用户验收。','']
doc=pymupdf.open()
for i,path in enumerate(paths):
 label='封面' if not i else f'第{i:02}页';lines += [f'## {label}','',f'![{label}]({os.path.relpath(path,out)})','']
 with Image.open(path) as image:
  iw,ih=image.size; preview=image.convert('RGB');preview.thumbnail((720,960),Image.Resampling.LANCZOS)
 data=io.BytesIO();preview.save(data,format='JPEG',quality=90,subsampling=0,optimize=True)
 # Physical page retains image aspect ratio. No fitting into a forced 3:4 rectangle.
 page=doc.new_page(width=691.2,height=691.2*ih/iw);page.insert_image(page.rect,stream=data.getvalue())
doc.set_metadata({'title':'第七话 连贯性试排v4 非定稿','subject':'等比预览，06页保留源图比例'});tmp=out/'tmp.pdf';doc.save(tmp,deflate=True,garbage=4);doc.close();tmp.replace(out/'第七话_连贯性轻量试排.pdf')
(out/'第七话_连贯性试排.md').write_text('\n'.join(lines),encoding='utf8')
print('06 size', im.size, 'bubble boxes', boxes)
