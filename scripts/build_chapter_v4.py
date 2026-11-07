from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
W,H=1440,1920
SRC=ROOT/'art/chapter-01-v4'
OUT=ROOT/'deliverables/full-v4/chapter-01';OUT.mkdir(parents=True,exist_ok=True)
FONT=ROOT/'assets/fonts/NotoSansCJKsc-Bold.otf'
PAPER='#F8F4EB';INK='#292B2C';RED='#92504C';YELLOW='#E9BD4F';MUTED='#746E67'
def ft(n):return ImageFont.truetype(str(FONT),n)
def wrap(d,s,f,width):
 out=[];line=''
 for ch in s:
  if d.textbbox((0,0),line+ch,font=f)[2]>width and line:out.append(line);line=ch
  else:line+=ch
 if line:out.append(line)
 return out
def text(d,s,xy,width,size=32,fill=INK,gap=12):
 x,y=xy;f=ft(size)
 for line in wrap(d,s,f,width):d.text((x,y),line,font=f,fill=fill);y+=size+gap
 return y
def cover_title(d,s,size=66):d.text((38,28),s,font=ft(size),fill=YELLOW,stroke_width=4,stroke_fill=INK)
def bubble(im,speaker,s,box,size=30,dark=False,tail='left'):
 """全话统一暖白圆角对白；深色只用于手机/转述消息。"""
 d=ImageDraw.Draw(im);x,y,w,h=box;fill=INK if dark else PAPER;body=PAPER if dark else INK
 d.rounded_rectangle((x,y,x+w,y+h),radius=28,fill=fill,outline=INK,width=3)
 if tail=='left':d.polygon(((x+60,y+h-3),(x+105,y+h-3),(x+76,y+h+27)),fill=fill,outline=INK,width=3)
 elif tail=='right':d.polygon(((x+w-105,y+h-3),(x+w-60,y+h-3),(x+w-76,y+h+27)),fill=fill,outline=INK,width=3)
 elif tail=='up-left':d.polygon(((x+60,y+3),(x+105,y+3),(x+76,y-27)),fill=fill,outline=INK,width=3)
 d.text((x+24,y+15),speaker,font=ft(21),fill=YELLOW if dark else RED)
 text(d,s,(x+24,y+55),w-48,size=size,fill=body,gap=9)
def scene(name):return Image.open(SRC/name).convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
def num(im,n=None):
 d=ImageDraw.Draw(im);s='COVER' if n is None else f'{n:02d} / 07';d.text((1250,1855),s,font=ft(18),fill=MUTED)
def clean(im,box):ImageDraw.Draw(im).rectangle(box,fill=PAPER)
def angled_schedule(im,title_s,rows,pos,angle,width=420,title_size=25,body_size=22):
 """先排成文字块，再按纸面角度整体旋转，避免横字贴斜纸。"""
 layer=Image.new('RGBA',(width,220),(0,0,0,0));d=ImageDraw.Draw(layer)
 d.text((12,5),title_s,font=ft(title_size),fill=RED)
 y=52
 for row in rows:
  d.text((16,y),row,font=ft(body_size),fill=INK);y+=body_size+15
 layer=layer.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
 im.paste(layer,pos,layer)

pages=[]
im=scene('cover.png');d=ImageDraw.Draw(im);cover_title(d,'休假回来的姐姐……')
bubble(im,'江望舒','星野，这次长假，先陪我。',(55,155,430,180),29,tail='right')
d=ImageDraw.Draw(im);d.text((60,1780),'《星辰落进灯火里》 第一话',font=ft(25),fill=RED)
num(im);im.save(OUT/'page-00-cover.png');pages.append(im)

# 普通正片不再逐页添加黄色解析标题。
im=scene('shot-01.png')
bubble(im,'江星野','项目搞定！从今天起，我是家里蹲。',(55,120,455,195),29,tail='right')
num(im,1);im.save(OUT/'page-01.png');pages.append(im)

im=scene('shot-02.png')
bubble(im,'江望舒','这次我会待很久，先把以前少陪你的时间补回来。',(70,80,625,245),30,tail='right')
num(im,2);im.save(OUT/'page-02.png');pages.append(im)

im=scene('shot-03.png')
bubble(im,'江望舒','我刚回来，今天先归我。',(50,125,340,175),25,tail='right')
bubble(im,'江辰希','二哥，今天先陪我！',(980,205,370,175),26)
num(im,3);im.save(OUT/'page-03.png');pages.append(im)

im=scene('shot-04.png')
bubble(im,'小满','小叔先陪我搭城堡！',(50,535,335,175),25,tail='right')
num(im,4);im.save(OUT/'page-04.png');pages.append(im)

im=scene('shot-05.png')
bubble(im,'江星野','别抢，我把时间都排好了。',(55,115,530,180),29,tail='right')
angled_schedule(im,'星野的安排',['陪姐姐散步','陪妹妹挑书','陪小满搭城堡、讲故事'],(820,1395),28)
num(im,5);im.save(OUT/'page-05.png');pages.append(im)

im=scene('shot-06.png')
bubble(im,'沈静宜','安排得很好，先把他的休息排上。',(55,105,610,185),28,tail='right')
bubble(im,'江星野','我也有自己的行程啊？',(55,345,465,160),27)
d=ImageDraw.Draw(im)
# 清理纸面旧网格，文字限制在桌上纸张四边形内并随纸面旋转。
d.polygon(((585,1405),(910,1280),(1085,1430),(745,1565)),fill='#FCF9F2')
angled_schedule(im,'星野的日程表',['1. 陪姐姐散步  2. 陪妹妹挑书','3. 陪小满搭城堡、讲三遍故事','4. 二弟睡觉'],(660,1165),21,width=400,title_size=22,body_size=18)
num(im,6);im.save(OUT/'page-06.png');pages.append(im)

im=scene('shot-07.png')
# 妈妈不在画面中：使用无尾巴的转述消息框，避免误指向沙发上的二弟。
bubble(im,'妈妈转述 · 大哥消息','项目结束就好，别熬夜。',(55,55,650,220),28,dark=True,tail=None)
# 小满气泡在下方居中，用向上的尾巴明确指向小满，不压任何人物头部。
bubble(im,'小满','小叔休息好，就陪我讲故事！',(380,1600,850,150),27,tail='up-left')
d=ImageDraw.Draw(im);d.rounded_rectangle((50,1795,520,1870),radius=18,fill=INK)
d.text((75,1815),'二弟被预约的第一天，正式开始。',font=ft(22),fill=YELLOW)
num(im,7);im.save(OUT/'page-07.png');pages.append(im)

for name in ['第一话_V4_精细化重制.pdf','第一话_竖屏全页漫画.pdf']:
 pages[0].save(ROOT/'deliverables'/name,save_all=True,append_images=pages[1:],resolution=150)
print('Built unified-dialogue V4:',len(pages),'pages')
