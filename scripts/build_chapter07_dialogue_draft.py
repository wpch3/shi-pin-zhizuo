"""第七话试排：不同版本的原画加候选对白；不覆盖正式版。"""
from pathlib import Path
import sys, numpy as np
from PIL import Image,ImageDraw,ImageFont
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text
if sys.argv[1:] != ['--draft']: raise SystemExit('仅允许 --draft')
root=Path(__file__).resolve().parents[1];out=root/'deliverables/review-chapter-07-dialogue-draft';pages=out/'pages';pages.mkdir(parents=True,exist_ok=True)
font=root/'assets/fonts/NotoSansCJKsc-Bold.otf'; W,H=1440,1920
src=['art/chapter-07-cooking-v2/cover.png','art/chapter-07-cooking-v1/shot-01.png','art/chapter-07-cooking-v2/shot-02.png','art/chapter-07-cooking-v5/shot-03.png','art/chapter-07-cooking-v4/shot-04-v2.png','art/chapter-07-cooking-v4/shot-05-v2.png','art/chapter-07-cooking-v5/shot-06.png','art/chapter-07-cooking-v5/shot-07.png']
# 对白均为制作提案，不是用户锁定对白。
dialogues={1:[(['妈妈今晚有事，','来不及做饭。'],(300,170),(390,570)),(['那今晚交给我吧。'],(1100,180),(1010,550))],2:[(['青菜洗好了。'],(250,140),(450,600)),(['我再炒一道，','汤也快好了。'],(1110,140),(1020,580))],3:[(['我来摆餐具！'],(1110,125),(1010,675)),(['好，我帮你数一数。'],(350,270),(390,680))],4:[(['看着就很香。'],(1120,125),(1070,565)),(['最后一道也好了。'],(330,125),(450,480))],5:[(['小满：小叔，','今天的菜好丰盛！'],(245,115),None),(['喜欢就多吃点。'],(1200,115),(990,470))],6:[(['给妈妈留一份。'],(260,155),(380,550)),(['我再写张纸条。'],(1140,155),(1040,610))],7:[(['你们真贴心。'],(1110,145),(1040,500))]}

def speech(im,lines,center,target):
 d=ImageDraw.Draw(im);f=ImageFont.truetype(str(font),27);lay=measure_speech_text(d,lines,center,f,27)
 if target is None:
  # 小满在画面下方，远距离尾巴会误指向姐姐；暂以带姓名的无尾字幕表示。
  d.rounded_rectangle(lay['box'],radius=18,fill='#F8F4EB',outline='#292B2C',width=3)
 else:
  s=oval_speech(center,lay['bubble_size'],target,tail_length=35,tail_width=28,bend=2);d.polygon(s,fill='#F8F4EB');d.line(s+[s[0]],fill='#292B2C',width=3,joint='curve')
 for x,y,line in lay['positions']:d.text((x,y),line,font=f,fill='#292B2C')
 return lay['box']

def paper(im):
 # 字形在高分辨率透明图中绘制，然后投影到原画实际纸面；禁止贴纸底或抹掉纸纹。
 text=Image.new('RGBA',(620,240),(0,0,0,0));d=ImageDraw.Draw(text);f=ImageFont.truetype(str(font),54)
 d.text((15,20),'妈妈，饭菜留好了。',font=f,fill=(79,67,61,255));d.text((15,110),'记得热一热。',font=f,fill=(79,67,61,255))
 k=W/896
 target=[(294*k,938*k),(416*k,978*k),(354*k,1042*k),(231*k,1000*k)]
 # inverse homography maps page pixels to text pixels
 srcp=[(0,0),(620,0),(620,240),(0,240)];a=[];b=[]
 for (x,y),(u,v) in zip(target,srcp):
  a.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);b.extend([u,v])
 coeff=np.linalg.solve(np.asarray(a),np.asarray(b));layer=text.transform((W,H),Image.Transform.PERSPECTIVE,coeff,Image.Resampling.BICUBIC)
 im.paste(layer,(0,0),layer)

for i,p in enumerate(src):
 with Image.open(root/p) as im: im=im.convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
 if i==7: paper(im)
 for lines,center,target in dialogues.get(i,[]): speech(im,lines,center,target)
 if i:
  d=ImageDraw.Draw(im);d.text((1260,1855),f'{i:02} / 07',font=ImageFont.truetype(str(font),20),fill='#292B2C',stroke_width=2,stroke_fill='#F8F4EB')
 im.save(pages/(f'page-{i:02}.png' if i else 'page-00-cover.png'),optimize=True)
md=['# 第七话｜对白与纸条试排（制作中）','','> 候选对白和纸条未审定。封面标题尚未决定；画面细节、排版、跨页连续与第六话末页仍待复核，本稿并非验收版。','']
for i in range(8):
 name=f'page-{i:02}.png' if i else 'page-00-cover.png';label=f'第{i:02}页' if i else '封面';md += [f'## {label}','',f'![{label}](pages/{name})','']
(out/'第七话_对白纸条试排.md').write_text('\n'.join(md),encoding='utf8')
print('七话试排：封面＋七页；文字为候选，须逐页实看。')
