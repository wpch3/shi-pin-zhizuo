"""第五话独立检查草稿；不写正式版。封面标题未裁定，故不写入。"""
from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageFont
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text
from draft_output import save_png_if_changed

if sys.argv[1:] != ['--draft']:
    raise SystemExit('仅允许 --draft，禁止写正式目录')
ROOT = Path(__file__).resolve().parents[1]
OLD, NEW = ROOT / 'art/chapter-05-aquarium', ROOT / 'art/chapter-05-aquarium-v2'
OUT = ROOT / 'deliverables/review-chapter-05-v2/pages'
OUT.mkdir(parents=True, exist_ok=True)
W, H = 1440, 1920
FONT = ROOT / 'assets/fonts/NotoSansCJKsc-Bold.otf'

def scene(name):
    path = (OLD if name in ('cover.png', 'shot-02.png') else NEW) / name
    with Image.open(path) as src:
        if src.size != (896, 1200):
            raise ValueError(f'源画尺寸异常: {path} {src.size}')
        return src.convert('RGB').resize((W, H), Image.Resampling.LANCZOS)

def speech(im, lines, center, target, size=29):
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(str(FONT), size)
    layout = measure_speech_text(draw, lines, center, font, size)
    shape = oval_speech(center, layout['bubble_size'], target, tail_length=30, tail_width=28, bend=2)
    draw.polygon(shape, fill='#F8F4EB')
    draw.line(shape + [shape[0]], fill='#292B2C', width=3, joint='curve')
    for x, y, line in layout['positions']:
        draw.text((x, y), line, font=font, fill='#292B2C')

def save(im, num):
    if num:
        ImageDraw.Draw(im).text((1290, 1860), f'{num:02d} / 08', font=ImageFont.truetype(str(FONT), 20), fill='#F8F4EB', stroke_width=2, stroke_fill='#292B2C')
    save_png_if_changed(im, OUT / ('page-00-cover.png' if num == 0 else f'page-{num:02}.png'))

im = scene('cover.png')
save(im, 0)

im = scene('shot-01.png')
speech(im, ['小叔，快走！', '企鹅在等我们！'], (250, 140), (360, 1140), 29)
speech(im, ['来了，别跑太快。'], (1120, 160), (600, 620), 29)
save(im, 1)

im = scene('shot-02.png')
speech(im, ['我要先看企鹅！'], (240, 135), (600, 1300), 29)
speech(im, ['我想看水母。'], (1190, 140), (1160, 920), 29)
speech(im, ['好，都去看。'], (240, 385), (500, 580), 29)
save(im, 2)

im = scene('shot-03.png')
speech(im, ['有两个女人这么喜欢你，', '二哥是不是很幸福呀？'], (1110, 130), (1150, 880), 29)
speech(im, ['明明是三个。'], (250, 280), (350, 850), 29)
speech(im, ['还有小满！'], (1140, 400), (800, 510), 29)
save(im, 3)

im = scene('shot-04-fixed.png')
speech(im, ['鱼在天上飞！'], (1120, 130), (940, 1190), 29)
speech(im, ['它们是在游。'], (260, 285), (360, 650), 29)
speech(im, ['今天就让它们', '飞一会儿吧。'], (1120, 430), (630, 750), 29)
save(im, 4)

im = scene('shot-05.png')
speech(im, ['它们好像在发光。'], (270, 140), (570, 890), 29)
speech(im, ['嗯，慢慢看。'], (1120, 200), (820, 660), 29)
save(im, 5)

im = scene('shot-06.png')
speech(im, ['今天最喜欢哪个？'], (1090, 140), (880, 820), 29)
speech(im, ['企鹅！还有水母！'], (270, 270), (650, 1000), 29)
speech(im, ['这已经不止一个了。'], (1120, 400), (1160, 940), 29)
save(im, 6)

im = scene('shot-07.png')
speech(im, ['这个和刚才的', '企鹅一样！'], (260, 140), (650, 1250), 29)
speech(im, ['你今天最喜欢', '企鹅，对吧？'], (1130, 210), (820, 630), 29)
save(im, 7)

im = scene('shot-08-fixed.png')
speech(im, ['能和你们一直在一起……', '我真的是最幸福的人。'], (1000, 150), (720, 590), 30)
save(im, 8)
print('第五话文字检查草稿:', OUT)
