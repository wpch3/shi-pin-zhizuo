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
def title(d,s,size=62):d.text((38,28),s,font=ft(size),fill=YELLOW,stroke_width=4,stroke_fill=INK)
def free(d,speaker,s,xy,width,size=32):
 x,y=xy;d.text((x,y),speaker,font=ft(23),fill=RED);d.line((x,y+36,x+105,y+36),fill=RED,width=3)
 text(d,s,(x,y+53),width,size=size,gap=10)
def bubble(im,speaker,s,box,size=32,dark=False):
 d=ImageDraw.Draw(im);x,y,w,h=box;fill=INK if dark else PAPER;body=PAPER if dark else INK
 d.rounded_rectangle((x,y,x+w,y+h),radius=28,fill=fill,outline=INK,width=3)
 d.text((x+24,y+16),speaker,font=ft(22),fill=YELLOW if dark else RED)
 text(d,s,(x+24,y+58),w-48,size=size,fill=body,gap=9)
def scene(name):return Image.open(SRC/name).convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
def num(im,n=None):
 d=ImageDraw.Draw(im);s='COVER' if n is None else f'{n:02d} / 07';d.text((1250,1855),s,font=ft(18),fill=MUTED)

pages=[]
# 每页使用本页独立的构图和留白，不使用统一模板覆盖人物。
im=scene('cover.png');d=ImageDraw.Draw(im);title(d,'休假回来的姐姐……',66)
free(d,'江望舒','星野，这次长假，先陪我。',(58,165),390,31)
d.text((60,1780),'《星辰落进灯火里》 第一话',font=ft(25),fill=RED)
num(im);im.save(OUT/'page-00-cover.png');pages.append(im)

im=scene('shot-01.png');d=ImageDraw.Draw(im);title(d,'项目刚结束，他想躺平……')
bubble(im,'江星野','项目搞定！从今天起，我是家里蹲。',(55,160,450,210),30)
num(im,1);im.save(OUT/'page-01.png');pages.append(im)

im=scene('shot-02.png');d=ImageDraw.Draw(im);title(d,'姐姐休假回来，第一件事——',57)
# 文字写入画面原生留白框，不另盖对话框。
d.text((100,105),'江望舒',font=ft(23),fill=RED)
text(d,'这次我会待很久，先把以前少陪你的时间补回来。',(100,155),540,31)
num(im,2);im.save(OUT/'page-02.png');pages.append(im)

im=scene('shot-03.png');d=ImageDraw.Draw(im);title(d,'刚回家，就开始抢人……')
text(d,'我刚回来，今天先归我。',(78,178),185,19)
text(d,'二哥，今天先陪我！',(1035,255),270,23)
num(im,3);im.save(OUT/'page-03.png');pages.append(im)

im=scene('shot-04.png');d=ImageDraw.Draw(im);title(d,'三个人，都想先约他……')
text(d,'小叔，先陪我搭城堡！',(75,595),205,19)
num(im,4);im.save(OUT/'page-04.png');pages.append(im)

im=scene('shot-05.png');d=ImageDraw.Draw(im);title(d,'二弟决定，亲自安排……')
free(d,'江星野','别抢，我把时间都排好了。',(65,145),430,30)
# 日程排进桌面原生白纸，不遮挡人物。
d.text((900,1490),'星野的安排',font=ft(29),fill=RED)
text(d,'陪姐姐散步\n陪妹妹挑书\n陪小满搭城堡、讲故事',(900,1545),400,25,gap=13)
num(im,5);im.save(OUT/'page-05.png');pages.append(im)

im=scene('shot-06.png');d=ImageDraw.Draw(im);title(d,'妈妈的安排，永远多一项……',58)
free(d,'沈静宜','安排得很好，先把他的休息排上。',(65,145),520,30)
text(d,'星野：我也有自己的行程啊？',(70,340),540,26,fill=MUTED)
d.text((90,1585),'江星野的日程表',font=ft(31),fill=RED)
d.text((95,1650),'1. 陪姐姐散步    2. 陪妹妹挑书',font=ft(27),fill=INK)
d.text((95,1710),'3. 陪小满搭城堡、讲三遍故事',font=ft(27),fill=INK)
d.text((95,1775),'4. 二弟睡觉',font=ft(30),fill=RED)
num(im,6);im.save(OUT/'page-06.png');pages.append(im)

im=scene('shot-07.png');d=ImageDraw.Draw(im);title(d,'休息，也被安排得明明白白……',54)
# 原生手机消息框与下方对白框。
d.text((875,95),'沈静宜',font=ft(22),fill=RED)
text(d,'你大哥刚从外地发来消息：项目结束就好，别熬夜。',(875,145),440,28)
text(d,'小满：小叔休息好，就陪我讲故事！',(585,1770),700,27)
d.rounded_rectangle((50,1795,520,1870),radius=18,fill=INK)
d.text((75,1815),'二弟被预约的第一天，正式开始。',font=ft(22),fill=YELLOW)
num(im,7);im.save(OUT/'page-07.png');pages.append(im)

for name in ['第一话_V4_精细化重制.pdf','第一话_竖屏全页漫画.pdf']:
 pages[0].save(ROOT/'deliverables'/name,save_all=True,append_images=pages[1:],resolution=150)
print('Built',len(pages),'independently illustrated V4 pages')
