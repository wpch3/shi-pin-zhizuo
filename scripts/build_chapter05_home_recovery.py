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
OUT = ROOT / 'deliverables/章节/第六话/review-chapter-05-home-recovery/pages'
OUT.mkdir(parents=True, exist_ok=True)
FONT = ROOT / 'assets/fonts/NotoSansCJKsc-Bold.otf'
W,H=896,1200
S = W / 1440
current_boxes = []

def scene(name):
    current_boxes.clear()
    path=ROOT / 'art' / name
    with Image.open(path) as src:
        if src.size != (896,1200): raise ValueError(f'源画尺寸异常：{path}: {src.size}')
        return src.convert('RGB')

def speech(im, lines, center, target, size=32):
    draw=ImageDraw.Draw(im)
    center = tuple(round(v * S) for v in center)
    target = tuple(round(v * S) for v in target)
    size = round(size * S)
    font=ImageFont.truetype(str(FONT),size)
    layout=measure_speech_text(draw,lines,center,font,size)
    x0,y0,x1,y1=layout['box']
    if x0 < 12 or y0 < 12 or x1 > W-12 or y1 > H-12:
        raise ValueError(f'气泡超出原生画布安全区：{layout["box"]}')
    for ax0,ay0,ax1,ay1 in current_boxes:
        if not (x1 <= ax0 or ax1 <= x0 or y1 <= ay0 or ay1 <= y0):
            raise ValueError('同页气泡框重叠')
    current_boxes.append(layout['box'])
    shape=oval_speech(center,layout['bubble_size'],target,tail_length=round(40*S),tail_width=round(28*S),bend=round(2*S))
    draw.polygon(shape,fill='#F8F4EB')
    draw.line(shape+[shape[0]],fill='#292B2C',width=2,joint='curve')
    for x,y,line in layout['positions']: draw.text((x,y),line,font=font,fill='#292B2C')

def save(im,num):
    if num:
        ImageDraw.Draw(im).text((round(1290*S),round(1860*S)),f'{num:02d} / 17',font=ImageFont.truetype(str(FONT),13),fill='#F8F4EB',stroke_width=1,stroke_fill='#292B2C')
    save_png_if_changed(im,OUT/('page-00-cover.png' if num==0 else f'page-{num:02d}.png'))

im = scene('chapter-05-home-v1/cover.png')
save(im,0)
im = scene('chapter-05-home-v2/shot-01-alt.png')
speech(im,['二哥，再来一局！'],(1120,290),(1010,520),32)
save(im,1)
im = scene('chapter-05-home-v3/shot-02-alt.png')
speech(im,['游戏也打完了……','今天有点累了。'],(1090,510),(860,840),32)
save(im,2)
im = scene('chapter-05-home-v3/shot-03-alt.png')
speech(im,['真像个小宝宝一样','爱撒娇呢。'],(1020,190),(620,360),32)
speech(im,['就让我靠一会儿。'],(1110,710),(830,940),32)
save(im,3)
im = scene('chapter-05-home-options/sister-younger-hug-knees-v3.png')
save(im,4)
im = scene('chapter-05-home-options/sister-younger-cuddle-v3.png')
save(im,5)
im = scene('chapter-05-home-v1/shot-04.png')
speech(im,['姐姐，今天有点累。'],(610,100),(570,270),32)
save(im,6)
im = scene('chapter-05-home-v3/shot-05.png')
speech(im,['如果叫妈妈的话，','说不定我会给你想办法哦。'],(1010,150),(610,250),32)
save(im,7)
im = scene('chapter-05-home-v2/shot-05b-call.png')
speech(im,['妈妈！'],(260,270),(440,440),36)
save(im,8)
im = scene('chapter-05-home-v3/shot-07-alt.png')
save(im,9)
im = scene('chapter-05-home-options/sister-older-embrace.png')
save(im,10)
im = scene('chapter-05-home-options/sister-older-forehead-v2.png')
save(im,11)
im = scene('chapter-05-home-v3/shot-08.png')
speech(im,['小满早就想和我们','一起去水族馆了。','明天你开车，','我们一起去玩吧。'],(340,220),(370,550),32)
save(im,12)
im = scene('chapter-05-home-v3/shot-09-alt.png')
speech(im,['小叔，我们一起去嘛，','好不好？'],(280,390),(490,820),32)
save(im,13)
im = scene('chapter-05-home-v2/shot-08b-answer.png')
speech(im,['只要是你们说的，','我都会去做的。','明天就出发吧。'],(1060,160),(730,320),32)
save(im,14)
im = scene('chapter-05-home-v2/shot-09-final-candidate.png')
speech(im,['太好了！'],(760,510),(700,800),32)
save(im,15)
im = scene('chapter-05-home-options/niece-hug-v2.png')
save(im,16)
im = scene('chapter-05-home-options/niece-piggyback-v4.png')
save(im,17)
print('第五话治愈版草稿:',OUT)
