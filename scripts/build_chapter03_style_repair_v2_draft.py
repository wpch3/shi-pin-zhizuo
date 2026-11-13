"""第三话08/09图文试排；保留旧成品，未验收候选不可覆盖正式版。"""
from pathlib import Path
import os,sys
from PIL import Image,ImageDraw,ImageFont
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text
if sys.argv[1:] != ['--draft']: raise SystemExit('仅允许 --draft')
root=Path(__file__).resolve().parents[1];out=root/'deliverables/章节/第三话/review-chapter-03-style-repair-v2';pages=out/'pages';pages.mkdir(parents=True,exist_ok=True)
font=root/'assets/fonts/NotoSansCJKsc-Bold.otf'
def bubble(im, lines, center, target, size):
 d=ImageDraw.Draw(im);f=ImageFont.truetype(str(font),size);layout=measure_speech_text(d,lines,center,f,size)
 s=oval_speech(center,layout['bubble_size'],target,tail_length=30,tail_width=28,bend=2)
 d.polygon(s,fill='#F8F4EB');d.line(s+[s[0]],fill='#292B2C',width=3,joint='curve')
 for x,y,line in layout['positions']:d.text((x,y),line,font=f,fill='#292B2C')
def page(n,source,dialogues):
 with Image.open(root/source) as src: im=src.convert('RGB').resize((1440,1920),Image.Resampling.LANCZOS)
 for args in dialogues:bubble(im,*args)
 d=ImageDraw.Draw(im);d.text((1250,1855),f'{n:02} / 11',font=ImageFont.truetype(str(font),18),fill='#292B2C',stroke_width=2,stroke_fill='#F8F4EB')
 im.save(pages/f'page-{n:02}.png',optimize=True)
page(8,'art/chapter-03-style-repair/shot-08-v4.png',[(['一人一半……','你不许笑我。'],(300,200),(470,690),29),(['……嗯，不笑。'],(1120,190),(960,620),29)])
page(9,'art/chapter-03-style-repair/shot-09-v1.png',[(['靠近一点，看镜头！'],(330,190),(520,700),28),(['这样？'],(1180,230),(1000,620),28),(['对，笑一下嘛。'],(330,400),(520,700),28)])
orig=root/'deliverables/章节/第三话/历史图源/full-v4';md=['# 第三话｜风格返修试排（未完成）','','> 只重绘08和09；其他10页沿用原成品，旧成品未被覆盖。08背心补回麻花纹，保留两把勺及一份甜品；09为候选。仍待逐页核对风格、衣饰与肢体，试排不是正式替换。','']
for i in range(12):
 name='page-00-cover.png' if i==0 else f'page-{i:02}.png';src=pages/name if i in (8,9) else orig/name
 rel=os.path.relpath(src,out);md += [f'## {"封面" if i==0 else f"第{i:02}页"}','',f'![第{i:02}页]({rel})','']
(out/'第三话_风格返修试排.md').write_text('\n'.join(md),encoding='utf8')
print('08/09候选试排；其余页引用原版。')
