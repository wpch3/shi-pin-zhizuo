from pathlib import Path
import json
import sys
from PIL import Image, ImageDraw, ImageFont
from draft_output import save_png_if_changed, ensure_draft_pdf
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text

ROOT = Path(__file__).resolve().parents[1]
if sys.argv[1:] not in (['--draft'], ['--draft', '--review']):
    raise SystemExit('第二话并轨仍在制作中；仅可用 --draft [--review] 生成隔离试排，禁止覆盖正式交付。')
REVIEW = '--review' in sys.argv[1:]
DRAFT = ROOT / ('deliverables/drafts/chapter-02-review' if REVIEW else 'deliverables/drafts/chapter-02')
CANDIDATES = ROOT / 'art/candidates-face-review/chapter-02'
REVIEW_SOURCES = {'shot-01.png': 'shot-01-fresh.png', 'shot-06.png': 'shot-06-style-aligned.png'}
W, H = 1440, 1920
VERTICAL_SIZE = (1440, 2146)
SRC = ROOT / 'art/chapter-02-v4'
OUT = DRAFT / 'reading'
VERTICAL_OUT = DRAFT / 'vertical'
OUT.mkdir(parents=True, exist_ok=True)
VERTICAL_OUT.mkdir(parents=True, exist_ok=True)
FONT = ROOT / 'assets/fonts/NotoSansCJKsc-Bold.otf'
PAPER = '#F8F4EB'
INK = '#292B2C'
RED = '#92504C'
YELLOW = '#E9BD4F'
MUTED = '#746E67'


def ft(size):
    return ImageFont.truetype(str(FONT), size)


def scene(name):
    path = CANDIDATES / REVIEW_SOURCES[name] if REVIEW and name in REVIEW_SOURCES else SRC / name
    if not path.exists():
        raise FileNotFoundError(f'缺少已审查的第二话原画：{path}')
    return Image.open(path).convert('RGB').resize((W, H), Image.Resampling.LANCZOS)


def speech(im, lines, center, target, size=29):
    """可见文字精确居中；椭圆长弧与尾巴采用同一闭合外轮廓。"""
    d = ImageDraw.Draw(im)
    f = ft(size)
    layout = measure_speech_text(d, lines, center, f, size)
    bw, bh = layout['bubble_size']
    outline = oval_speech(center, (bw, bh), target, tail_length=30, tail_width=28, bend=2)
    d.polygon(outline, fill=PAPER)
    d.line(outline+[outline[0]], fill=INK, width=3, joint='curve')
    for x, y, line in layout['positions']:
        d.text((x, y), line, font=f, fill=INK)
    return layout['box']


def num(im, n=None):
    d = ImageDraw.Draw(im)
    value = 'COVER' if n is None else f'{n:02d} / 07'
    d.text((1250, 1855), value, font=ft(18), fill=MUTED)


pages = []
reading_changed = 0

im = scene('cover.png')
d = ImageDraw.Draw(im)
d.text((38, 28), '二姐的独占时间', font=ft(66), fill=YELLOW, stroke_width=4, stroke_fill=INK)
speech(im, ['今天没人要抢你咯，', '专心陪着姐姐我哦。'], (1000, 190), (995, 466), 29)
d = ImageDraw.Draw(im)
d.text((60, 1780), '《二弟的休息日被全家预约了》 第二话', font=ft(25), fill=RED, stroke_width=2, stroke_fill=PAPER)
num(im)
reading_changed += save_png_if_changed(im, OUT/'page-00-cover.png')
pages.append(im)

im = scene('shot-01.png')
speech(im, ['他们晚上才回来。', '电脑先关了，', '今天不许再忙工作。'], (350, 205) if REVIEW else (350, 590), (500, 530) if REVIEW else (610, 907), 29)
speech(im, ['……嗯。'], (1120, 300) if REVIEW else (1100, 690), (1060, 715) if REVIEW else (1045, 965), 29)
num(im, 1)
reading_changed += save_png_if_changed(im, OUT/'page-01.png')
pages.append(im)

im = scene('shot-02.png')
speech(im, ['第一件事，', '帮我把内衣和袜子洗了。'], (320, 560), (418, 867), 29)
speech(im, ['……这就是', '你说的陪你？'], (1090, 555), (1045, 803), 28)
speech(im, ['你洗，我陪。'], (650, 735), (418, 867), 29)
num(im, 2)
reading_changed += save_png_if_changed(im, OUT/'page-02.png')
pages.append(im)

im = scene('shot-03.png')
speech(im, ['水温别太高，', '袜子和内衣', '分开洗——'], (1100, 400) if REVIEW else (1100, 610), (1173, 1028), 29)
speech(im, ['到底谁洗？'], (320, 555) if REVIEW else (320, 650), (514, 915), 29)
speech(im, ['你洗，', '我负责指挥。'], (920, 700) if REVIEW else (820, 710), (1173, 1028), 28)
num(im, 3)
reading_changed += save_png_if_changed(im, OUT/'page-03.png')
pages.append(im)

im = scene('shot-04.png')
speech(im, ['小时候你也这样', '指挥我？'], (340, 480), (642, 835), 29)
speech(im, ['小时候是我洗，', '你在旁边玩。', '现在换你照顾我，', '不行吗？'], (1080, 540), (1045, 900), 27)
num(im, 4)
reading_changed += save_png_if_changed(im, OUT/'page-04.png')
pages.append(im)

im = scene('shot-05.png')
speech(im, ['知道了，妈——'], (350, 230) if REVIEW else (400, 480), (650, 835), 29)
speech(im, ['你刚才', '叫我什么？'], (1100, 335) if REVIEW else (1100, 430), (1045, 900), 29)
speech(im, ['口误。'], (470, 440) if REVIEW else (650, 500), (650, 835), 29)
speech(im, ['我不管，反正我听到了。', '再叫一次嘛。'], (1050, 535) if REVIEW else (1050, 585), (1045, 900), 27)
num(im, 5)
reading_changed += save_png_if_changed(im, OUT/'page-05.png')
pages.append(im)

im = scene('shot-06.png')
speech(im, ['辛苦啦，奖励你', '陪姐姐午睡半小时。'], (340, 270) if REVIEW else (340, 420), (642, 835), 29)
speech(im, ['到底是谁辛苦？'], (1200, 410) if REVIEW else (1200, 380), (996, 643), 29)
speech(im, ['我陪你也很辛苦呀。'], (220, 650), (642, 835), 28)
num(im, 6)
reading_changed += save_png_if_changed(im, OUT/'page-06.png')
pages.append(im)

im = scene('shot-07.png')
speech(im, ['星野，别走。'], (500, 170) if REVIEW else (700, 270), (884, 578), 29)
speech(im, ['睡吧，我不走。'], (800, 230) if REVIEW else (1100, 120), (1092, 321), 29)
d = ImageDraw.Draw(im)
d.rounded_rectangle((50, 1785, 1130, 1870), radius=18, fill=INK)
d.text((75, 1804), '二姐睡了一个好觉，二弟陪她睡了一整个下午。', font=ft(25), fill=YELLOW)
num(im, 7)
reading_changed += save_png_if_changed(im, OUT/'page-07.png')
pages.append(im)

# 固定八页顺序，其他遗留文件不参与 PDF。保持原场景、对白、页码，只产生隔离试排。
names = ['page-00-cover.png'] + [f'page-{i:02d}.png' for i in range(1, 8)]
reading_paths = [OUT / name for name in names]
vertical_paths = [VERTICAL_OUT / name for name in names]
vertical_changed = 0
for source_path, dest_path in zip(reading_paths, vertical_paths):
    with Image.open(source_path) as page:
        source = page.convert('RGB')
    assert source.size == (W, H), f'Unexpected draft page size: {source_path}: {source.size}'
    vertical = Image.new('RGB', VERTICAL_SIZE, PAPER)
    vertical.paste(source, (0, (VERTICAL_SIZE[1]-H)//2))
    vertical_changed += save_png_if_changed(vertical, dest_path)

cache_path = DRAFT / '.pdf-cache.json'
try:
    previous = json.loads(cache_path.read_text(encoding='utf-8'))
except (FileNotFoundError, ValueError):
    previous = {}
cache = {}
cache['reading'], reading_pdf_changed = ensure_draft_pdf(
    reading_paths, DRAFT/'chapter-02-draft-reading.pdf', previous.get('reading', {}))
cache['vertical'], vertical_pdf_changed = ensure_draft_pdf(
    vertical_paths, DRAFT/'chapter-02-draft-vertical.pdf', previous.get('vertical', {}))
cache_tmp = cache_path.with_name(cache_path.name + '.tmp')
try:
    cache_tmp.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')
    cache_tmp.replace(cache_path)
finally:
    cache_tmp.unlink(missing_ok=True)
print(f'UNAPPROVED DRAFT chapter 2: {len(pages)} pages; PNG changed: {reading_changed} reading / {vertical_changed} vertical; PDF rebuilt: {reading_pdf_changed} / {vertical_pdf_changed}')
