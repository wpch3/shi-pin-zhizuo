"""第三话用户反馈试排：只改变08、10、11，不覆盖原版。"""
from pathlib import Path
import os,sys
from PIL import Image,ImageDraw,ImageFont
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text
if sys.argv[1:] != ['--draft']: raise SystemExit('仅允许 --draft')
root=Path(__file__).resolve().parents[1]
out=root/'deliverables/章节/第三话/review-chapter-03-user-feedback';pages=out/'pages';pages.mkdir(parents=True,exist_ok=True)
font=root/'assets/fonts/NotoSansCJKsc-Bold.otf'
def page(n,source,dialogues):
 with Image.open(root/source) as src:
  if src.size!=(896,1200): raise ValueError((source,src.size))
  im=src.convert('RGB').resize((1440,1920),Image.Resampling.LANCZOS)
 d=ImageDraw.Draw(im);boxes=[]
 for lines,center,target,size,tail in dialogues:
  f=ImageFont.truetype(str(font),size);layout=measure_speech_text(d,lines,center,f,size);box=layout['box']
  assert 0<=box[0]<box[2]<=1440 and 0<=box[1]<box[3]<=1920,(n,box)
  assert all(box[2]<=b[0] or b[2]<=box[0] or box[3]<=b[1] or b[3]<=box[1] for b in boxes),(n,box,boxes)
  boxes.append(box);s=oval_speech(center,layout['bubble_size'],target,tail_length=tail,tail_width=28,bend=2)
  d.polygon(s,fill='#F8F4EB');d.line(s+[s[0]],fill='#292B2C',width=3,joint='curve')
  for x,y,line in layout['positions']:d.text((x,y),line,font=f,fill='#292B2C')
 d.text((1250,1855),f'{n:02} / 11',font=ImageFont.truetype(str(font),18),fill='#292B2C',stroke_width=2,stroke_fill='#F8F4EB')
 im.save(pages/f'page-{n:02}.png',optimize=True);print(n,boxes)
page(8,'art/chapter-03-style-repair/shot-08-v6.png',[(['一人一半……','你不许笑我。'],(300,200),(470,690),29,30),(['……嗯，不笑。'],(1120,190),(960,620),29,30)])
page(10,'art/chapter-03-style-repair/shot-10-v2.png',[(['小希，这位是？'],(280,150),(350,620),29,35),(['这个是我男朋友。'],(760,265),(760,600),30,35)])
page(11,'art/chapter-03-v7/shot-11.png',[(['我才回来，','位置就被你们占完了？'],(340,175),(530,660),28,45),(['小叔，我也要！'],(225,1090),(620,1080),29,55),(['走，小满，我们一起。'],(220,1240),(480,760),28,55)])
orig=root/'deliverables/章节/第三话/历史图源/full-v4'
md=['# 第三话｜用户反馈返修试排','','> 第08页调整表情，第10页重新生图，第11页只改气泡位置；原台词不变。09页和其他页面沿用原成品；此前09返修候选另存，暂不并入。第11页为排版尝试，小满气泡仍可能误指姐姐，尚未修好；本试排未覆盖原版，不是验收版。','']
for i in range(12):
 name='page-00-cover.png' if i==0 else f'page-{i:02}.png';src=pages/name if i in (8,10,11) else orig/name
 md += [f'## {"封面" if i==0 else f"第{i:02}页"}','',f'![第{i:02}页]({os.path.relpath(src,out)})','']
(out/'第三话_用户反馈返修试排.md').write_text('\n'.join(md),encoding='utf8')
