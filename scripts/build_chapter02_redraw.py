"""第二话全新原画试排：只输出隔离草稿，台词以既定审校为准。"""
from pathlib import Path
import sys
import json
from PIL import Image, ImageDraw, ImageFont
from draft_output import save_png_if_changed, ensure_draft_pdf
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text

ROOT = Path(__file__).resolve().parents[1]
if sys.argv[1:] != ['--draft']:
    raise SystemExit('只允许 --draft；禁止覆盖旧正式交付。')
SRC = ROOT / 'art/chapter-02-redraw-v2'
OUT = ROOT / 'deliverables/drafts/chapter-02-redraw-v2/reading'
OUT.mkdir(parents=True, exist_ok=True)
FONT = ROOT / 'assets/fonts/NotoSansCJKsc-Bold.otf'
W, H = 1440, 1920
PAPER, INK, YELLOW, RED, MUTED = '#F8F4EB', '#292B2C', '#E9BD4F', '#92504C', '#746E67'

def ft(size): return ImageFont.truetype(str(FONT), size)
def scene(name):
    p = SRC / name
    with Image.open(p) as im:
        if im.size != (896, 1200): raise ValueError(f'尺寸不符，禁止拉伸: {p} {im.size}')
        return im.convert('RGB').resize((W, H), Image.Resampling.LANCZOS)
def speech(im, lines, center, target, size=29):
    d = ImageDraw.Draw(im)
    f = ft(size)
    layout = measure_speech_text(d, lines, center, f, size)
    outline = oval_speech(center, layout['bubble_size'], target, tail_length=30, tail_width=28, bend=2)
    d.polygon(outline, fill=PAPER)
    d.line(outline + [outline[0]], fill=INK, width=3, joint='curve')
    for x, y, line in layout['positions']: d.text((x, y), line, font=f, fill=INK)
def num(im, n=None):
    ImageDraw.Draw(im).text((1250, 1855), 'COVER' if n is None else f'{n:02d} / 07', font=ft(18), fill=MUTED)
def save(im, name):
    save_png_if_changed(im, OUT / name)

im = scene('cover.png')
d = ImageDraw.Draw(im)
d.text((38, 28), '二姐的独占时间', font=ft(66), fill=YELLOW, stroke_width=4, stroke_fill=INK)
speech(im, ['今天没人要抢你咯，', '专心陪着姐姐我哦。'], (1000, 120), (1060, 365), 29)
d = ImageDraw.Draw(im)
d.text((60, 1780), '《二弟的休息日被全家预约了》 第二话', font=ft(25), fill=RED, stroke_width=2, stroke_fill=PAPER)
num(im)
save(im, 'page-00-cover.png')

im = scene('shot-01.png')
speech(im, ['他们晚上才回来。', '电脑先关了，', '今天不许再忙工作。'], (330, 150), (500, 450), 29)
speech(im, ['……嗯。'], (1100, 360), (1080, 700), 29)
num(im, 1)
save(im, 'page-01.png')

im = scene('shot-02-alt.png')
speech(im, ['第一件事，', '帮我把内衣和袜子洗了。'], (315, 110), (465, 420), 29)
speech(im, ['……这就是', '你说的陪你？'], (1250, 230), (1050, 430), 28)
speech(im, ['你洗，我陪。'], (780, 520), (465, 420), 29)
num(im, 2)
save(im, 'page-02.png')

im = scene('shot-03.png')
speech(im, ['水温别太高，', '袜子和内衣', '分开洗——'], (1120, 140), (1100, 600), 29)
speech(im, ['到底谁洗？'], (300, 180), (490, 400), 29)
speech(im, ['你洗，', '我负责指挥。'], (1080, 350), (1100, 600), 28)
num(im, 3)
save(im, 'page-03.png')

im = scene('shot-04.png')
speech(im, ['小时候你也这样', '指挥我？'], (320, 150), (510, 430), 29)
speech(im, ['小时候是我洗，', '你在旁边玩。', '现在换你照顾我，', '不行吗？'], (1100, 290), (1080, 550), 27)
num(im, 4)
save(im, 'page-04.png')

im = scene('shot-05.png')
speech(im, ['知道了，妈——'], (220, 110), (490, 380), 29)
speech(im, ['你刚才', '叫我什么？'], (1120, 170), (1010, 550), 29)
speech(im, ['口误。'], (200, 300), (490, 380), 29)
speech(im, ['我不管，反正我听到了。', '再叫一次嘛。'], (1090, 360), (1010, 550), 27)
num(im, 5)
save(im, 'page-05.png')

im = scene('shot-06.png')
speech(im, ['辛苦啦，奖励你', '陪姐姐午睡半小时。'], (250, 110), (590, 430), 29)
speech(im, ['到底是谁辛苦？'], (1200, 190), (1000, 350), 29)
speech(im, ['我陪你也很辛苦呀。'], (250, 400), (590, 430), 28)
num(im, 6)
save(im, 'page-06.png')

im = scene('shot-07-alt.png')
speech(im, ['星野，别走。'], (430, 105), (730, 380), 29)
speech(im, ['睡吧，我不走。'], (1250, 170), (1080, 360), 29)
d = ImageDraw.Draw(im)
d.rounded_rectangle((410, 1785, 1390, 1870), radius=18, fill=INK)
d.text((435, 1804), '二姐睡了一个好觉，二弟陪她睡了一整个下午。', font=ft(25), fill=YELLOW)
d.text((50, 1870), '07 / 07', font=ft(18), fill=MUTED)
save(im, 'page-07.png')

paths = [OUT / 'page-00-cover.png'] + [OUT / f'page-{i:02}.png' for i in range(1, 8)]
cache_path = OUT.parent / '.pdf-cache.json'
try:
    previous = json.loads(cache_path.read_text(encoding='utf-8'))
except (FileNotFoundError, ValueError):
    previous = {}
cache, _ = ensure_draft_pdf(paths, OUT.parent / 'chapter-02-redraw-draft.pdf', previous)
tmp = cache_path.with_suffix('.tmp')
try:
    tmp.write_text(json.dumps(cache, ensure_ascii=False), encoding='utf-8')
    tmp.replace(cache_path)
finally:
    tmp.unlink(missing_ok=True)
print('第二话全新8页隔离草稿（未经用户验收）:', OUT)
