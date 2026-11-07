import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'data/characters.json').read_text(encoding='utf-8'))
FONT=ROOT/'assets/fonts/NotoSansCJKsc-Bold.otf'
W,H=1440,1920
OUT=ROOT/'deliverables/full-v3'; COUT=OUT/'characters'; OOUT=OUT/'chapter-01'
COUT.mkdir(parents=True,exist_ok=True);OOUT.mkdir(parents=True,exist_ok=True)
PAPER='#F8F4EB'; INK='#292B2C'; RED='#92504C'; YELLOW='#E9BD4F'; MUTED='#746E67'

def ft(n):return ImageFont.truetype(str(FONT),n)
def lines(d,s,f,width):
 out=[];line=''
 for ch in s:
  if ch=='\n':out.append(line);line='';continue
  if d.textbbox((0,0),line+ch,font=f)[2]>width and line:out.append(line);line=ch
  else:line+=ch
 if line:out.append(line)
 return out

def text(d,s,xy,width,size=32,fill=INK,gap=12):
 x,y=xy;f=ft(size)
 for line in lines(d,s,f,width):d.text((x,y),line,font=f,fill=fill);y+=size+gap
 return y

def title(d,s,size=68):d.text((42,30),s,font=ft(size),fill=YELLOW,stroke_width=4,stroke_fill=INK)
def bubble(im,speaker,s,box,size=38,dark=False):
 d=ImageDraw.Draw(im);x,y,w,h=box;fill=INK if dark else PAPER;body=PAPER if dark else INK
 d.rounded_rectangle((x,y,x+w,y+h),radius=25,fill=fill,outline=RED if dark else INK,width=3)
 d.polygon(((x+60,y+h-2),(x+100,y+h-2),(x+75,y+h+25)),fill=fill)
 d.text((x+25,y+15),speaker,font=ft(23),fill=YELLOW if dark else RED)
 yy=y+60
 for line in lines(d,s,ft(size),w-50):d.text((x+25,yy),line,font=ft(size),fill=body);yy+=size+12

def scene(p):return Image.open(p).convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
def page_num(im,n):ImageDraw.Draw(im).text((1240,1855),f'{n:02d} / 07',font=ft(21),fill=MUTED)
def trim(im):
 a=np.asarray(im.convert('RGB'));mask=np.min(a,axis=2)<238
 rows=np.flatnonzero(mask.sum(axis=1)>8);cols=np.flatnonzero(mask.sum(axis=0)>8)
 return im.crop((int(cols[0]),int(rows[0]),int(cols[-1])+1,int(rows[-1])+1)) if len(rows) and len(cols) else im

def cutout(fid):
 im=Image.open(ROOT/'art/character-v3'/f'{fid}.png').convert('RGBA')
 seeds=[(0,0),(im.width-1,0),(0,im.height-1),(im.width-1,im.height-1),(im.width//2,0),(0,im.height//2),(im.width-1,im.height//2)]
 for seed in seeds:ImageDraw.floodfill(im,seed,(248,244,235,0),thresh=68)
 return trim(im)

def paste_fit(im,src,box):
 x,y,w,h=box;scale=min(w/src.width,h/src.height);src=src.resize((round(src.width*scale),round(src.height*scale)),Image.Resampling.LANCZOS)
 im.paste(src,(x+(w-src.width)//2,y+(h-src.height)//2),src if src.mode=='RGBA' else None)

pages=[]
# 封面直接采用用户新参考中的姐姐，不混入旧版人物。
im=Image.new('RGB',(W,H),PAPER);paste_fit(im,cutout('older-sister'),(170,190,1100,1420))
d=ImageDraw.Draw(im);title(d,'休假回来的姐姐……');bubble(im,'江望舒','星野，这次长假，先陪我。',(55,260,510,190),size=35,dark=True)
d.text((55,1790),'《星辰落进灯火里》 第一话',font=ft(28),fill=RED)
im.save(OOUT/'page-00-cover.png');pages.append(im)

specs=[
 ('项目刚结束，他想躺平……',('江星野','项目搞定！从今天起，我是家里蹲。',(40,155,450,195),30)),
 ('姐姐休假回来，第一件事——',('江望舒','这次我会待很久，先把以前少陪你的时间补回来。',(40,145,450,275),28)),
 ('刚回家，就开始抢人……',None),
 ('三个人，都想先约他……',('小满','小叔先陪我搭城堡！',(45,150,590,160),34)),
 ('二弟决定，亲自安排……',('江星野','别抢，我把时间都排好了。',(40,145,450,180),29)),
 ('妈妈的安排，永远多一项……',('沈静宜','安排得很好，先把他的休息排上。',(40,1100,500,180),30)),
 ('休息，也被安排得明明白白……',None),
]
for i,(heading,dialogue) in enumerate(specs,1):
 im=scene(ROOT/'art/vertical-v3'/f'shot-{i:02d}.png');d=ImageDraw.Draw(im);title(d,heading,size=62 if i in (2,6,7) else 68)
 if i==3:
  bubble(im,'江辰希','二哥，今天先陪我！',(40,150,510,170),size=32)
  bubble(im,'江望舒','我刚回来，今天先归我。',(900,150,500,170),size=31)
 elif dialogue:bubble(im,*dialogue)
 if i==6:
  d=ImageDraw.Draw(im);d.rounded_rectangle((110,1360,1330,1780),radius=24,fill=PAPER,outline=INK,width=3)
  d.text((155,1395),'江星野的日程表',font=ft(35),fill=RED)
  rows=['1. 陪姐姐散步','2. 陪妹妹挑书','3. 陪小满搭城堡、讲三遍故事','4. 二弟睡觉']
  yy=1470
  for j,row in enumerate(rows):d.text((165,yy),row,font=ft(29 if j==2 else 31),fill=RED if j==3 else INK);yy+=72
 if i==7:
  bubble(im,'沈静宜','你大哥刚发消息：项目结束就好，别熬夜。',(500,140,880,175),size=30,dark=True)
  bubble(im,'小满','小叔休息好，就陪我讲故事！',(360,1580,720,150),size=30)
  d=ImageDraw.Draw(im);d.rounded_rectangle((120,1770,1320,1865),radius=22,fill=INK)
  d.text((170,1793),'二弟被预约的第一天，正式开始。',font=ft(36),fill=YELLOW)
 page_num(im,i);im.save(OOUT/f'page-{i:02d}.png');pages.append(im)

for name in ['第一话_V3_手绘完整重制.pdf','第一话_竖屏全页漫画.pdf']:
 pages[0].save(ROOT/'deliverables'/name,save_all=True,append_images=pages[1:],resolution=150)

cards=[]
for i,c in enumerate(DATA['characters'],1):
 im=Image.new('RGB',(W,H),PAPER);d=ImageDraw.Draw(im)
 d.text((50,35),c['name'],font=ft(66),fill=INK);d.text((55,128),c['role'],font=ft(27),fill=RED);d.line((50,190,1390,190),fill=INK,width=2)
 paste_fit(im,cutout(c['id']),(130,230,1180,720))
 d=ImageDraw.Draw(im);d.text((55,1000),'人物介绍',font=ft(30),fill=RED);y=1060
 for item in c['settings']:
  d.ellipse((58,y+12,70,y+24),fill=RED);y=text(d,item,(90,y),1260,size=27,gap=10)+15
 d.text((55,1830),c['visual'],font=ft(21),fill=MUTED);d.text((1240,1860),f'{i:02d} / 08',font=ft(21),fill=MUTED)
 im.save(COUT/f"{i:02d}-{c['id']}.png");cards.append(im)

im=Image.new('RGB',(W,H),PAPER);d=ImageDraw.Draw(im)
d.text((50,35),'星辰落进灯火里',font=ft(60),fill=INK);d.text((55,125),'全员合照｜江怀川 · 沈静宜 · 江昭远 · 江望舒 · 江星野 · 江辰希 · 小满',font=ft(22),fill=RED)
group=Image.open(ROOT/'art/family-v3/group.png').convert('RGB');paste_fit(im,group,(45,190,1350,1650))
im.save(COUT/'08-family.png');cards.append(im)
for name in ['完整人设与合照_V3.pdf','完整人设与合照.pdf']:
 cards[0].save(ROOT/'deliverables'/name,save_all=True,append_images=cards[1:],resolution=150)
print('Built',len(pages),'V3 comic pages and',len(cards),'character/family pages')
