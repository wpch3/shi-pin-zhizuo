"""第五话居家前置检查草稿；仅 --draft，绝不覆盖水族馆或用户定稿。"""
from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageFont
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text
from draft_output import save_png_if_changed

if sys.argv[1:] != ['--draft']:
    raise SystemExit('仅允许 --draft')
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'deliverables/章节/第六话/review-chapter-05-home/pages'
OUT.mkdir(parents=True, exist_ok=True)
FONT = ROOT / 'assets/fonts/NotoSansCJKsc-Bold.otf'
W,H=1440,1920

def scene(name):
    path=ROOT / 'art' / name
    with Image.open(path) as src:
        if src.size != (896,1200): raise ValueError(f'源画尺寸异常：{path}: {src.size}')
        return src.convert('RGB').resize((W,H), Image.Resampling.LANCZOS)

def speech(im, lines, center, target, size=32):
    draw=ImageDraw.Draw(im)
    font=ImageFont.truetype(str(FONT),size)
    layout=measure_speech_text(draw,lines,center,font,size)
    shape=oval_speech(center,layout['bubble_size'],target,tail_length=40,tail_width=28,bend=2)
    draw.polygon(shape,fill='#F8F4EB')
    draw.line(shape+[shape[0]],fill='#292B2C',width=3,joint='curve')
    for x,y,line in layout['positions']: draw.text((x,y),line,font=font,fill='#292B2C')

def save(im,num):
    if num:
        ImageDraw.Draw(im).text((1290,1860),f'{num:02d} / 11',font=ImageFont.truetype(str(FONT),20),fill='#F8F4EB',stroke_width=2,stroke_fill='#292B2C')
    save_png_if_changed(im,OUT/('page-00-cover.png' if num==0 else f'page-{num:02d}.png'))

im = scene('chapter-05-home-v1/cover.png')
save(im,0)
im = scene('chapter-05-home-v2/shot-01-alt.png')
speech(im,['二哥，再来一局！'],(1120,290),(1010,520),32)
save(im,1)
im = scene('chapter-05-home-v2/shot-02.png')
speech(im,['游戏也打完了……','今天好无聊。'],(1090,510),(860,840),32)
save(im,2)
im = scene('chapter-05-home-v1/shot-03.png')
speech(im,['真像个小宝宝一样','爱撒娇呢。'],(1020,190),(620,360),32)
speech(im,['就让我靠一会儿。'],(1110,710),(830,940),32)
save(im,3)
im = scene('chapter-05-home-v1/shot-04.png')
speech(im,['姐姐，今天好无聊。'],(610,100),(570,270),32)
save(im,4)
im = scene('chapter-05-home-v2/shot-05.png')
speech(im,['如果叫妈妈的话，','说不定我会给你想办法哦。'],(1010,120),(610,250),32)
save(im,5)
im = scene('chapter-05-home-v2/shot-05b-call.png')
speech(im,['妈妈！'],(260,270),(440,440),36)
save(im,6)
im = scene('chapter-05-home-v1/shot-06.png')
save(im,7)
im = scene('chapter-05-home-v1/shot-07.png')
speech(im,['小满早就想和我们','一起去水族馆了。','明天你开车，','我们一起去玩吧。'],(270,1180),(410,580),32)
save(im,8)
im = scene('chapter-05-home-v2/shot-08-alt.png')
speech(im,['小叔，我们一起去嘛，','好不好？'],(620,1010),(830,850),32)
save(im,9)
im = scene('chapter-05-home-v2/shot-08b-answer.png')
speech(im,['只要是你们说的，','我都会去做的。','明天就出发吧。'],(1060,160),(730,320),32)
save(im,10)
im = scene('chapter-05-home-v2/shot-09-final-candidate.png')
speech(im,['太好了！'],(760,510),(700,800),32)
save(im,11)
print('第五话居家前置检查草稿:',OUT)
