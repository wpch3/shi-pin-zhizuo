"""第三话构建入口：封面 + 9页正片 = 10页。

用户已确认把“买衣服试衣服”拆成两个镜头：妹妹被真心夸奖、哥哥正装让妹妹惊艳。
原锁定第7个事件（女同学问答）在10页版中为第8页；台词和禁止项不变。
缺少已审查原画时明确失败，禁止用立绘、旧话原画或占位图冒充正片。
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text
from pdf_export import save_lossless_pdf_from_paths

ROOT = Path(__file__).resolve().parents[1]
W, H = 1440, 1920
VERTICAL_SIZE = (1440, 2146)
SRC = ROOT / 'art/chapter-03-v4'
OUT = ROOT / 'deliverables/full-v4/chapter-03'
VERTICAL_OUT = ROOT / 'deliverables/full-v4-vertical/chapter-03'
FONT = ROOT / 'assets/fonts/NotoSansCJKsc-Bold.otf'
PAPER = '#F8F4EB'
INK = '#292B2C'
RED = '#92504C'
YELLOW = '#E9BD4F'
MUTED = '#746E67'
REQUIRED = ['cover.png'] + [f'shot-{i:02d}.png' for i in range(1, 10)]


def ft(size):
    return ImageFont.truetype(str(FONT), size)


def scene(name):
    path = SRC / name
    if not path.exists():
        raise FileNotFoundError(f'缺少已审查的第三话原画：{path}；不得用占位图或立绘替代。')
    source = Image.open(path).convert('RGB')
    fitted = ImageOps.contain(source, (W, H), Image.Resampling.LANCZOS)
    result = Image.new('RGB', (W, H), PAPER)
    result.paste(fitted, ((W - fitted.width) // 2, (H - fitted.height) // 2))
    return result


def speech(im, lines, center, target, size=29):
    d = ImageDraw.Draw(im)
    f = ft(size)
    layout = measure_speech_text(d, lines, center, f, size)
    bw, bh = layout['bubble_size']
    outline = oval_speech(center, (bw, bh), target, tail_length=30, tail_width=28, bend=2)
    d.polygon(outline, fill=PAPER)
    d.line(outline + [outline[0]], fill=INK, width=3, joint='curve')
    for x, y, line in layout['positions']:
        d.text((x, y), line, font=f, fill=INK)
    return layout['box']


def num(im, n=None):
    d = ImageDraw.Draw(im)
    value = 'COVER' if n is None else f'{n:02d} / 09'
    d.text((1250, 1855), value, font=ft(18), fill=MUTED)


def save_png(im, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, optimize=True, compress_level=9)


missing = [name for name in REQUIRED if not (SRC / name).exists()]
if missing:
    raise FileNotFoundError('第三话尚缺已审查原画：' + ', '.join(missing))
OUT.mkdir(parents=True, exist_ok=True)
VERTICAL_OUT.mkdir(parents=True, exist_ok=True)
pages = []

# 封面：主角妹妹，独立构图；只使用系列名与“第三话”。
im = scene('cover.png')
d = ImageDraw.Draw(im)
d.text((40, 45), '二弟的休息日被全家预约了', font=ft(56), fill=YELLOW, stroke_width=4, stroke_fill=INK)
d.text((40, 135), '第三话', font=ft(32), fill=RED, stroke_width=2, stroke_fill=PAPER)
save_png(im, OUT / 'page-00-cover.png')
pages.append(im)

im = scene('shot-01.png')
speech(im, ['二哥，七点啦！', '说好今天陪我逛街的。'], (330, 220), (590, 705), 29)
speech(im, ['……起，', '给我两分钟。'], (1080, 300), (1060, 780), 29)
num(im, 1)
save_png(im, OUT / 'page-01.png')
pages.append(im)

im = scene('shot-02.png')
speech(im, ['收拾好了，出发！'], (330, 230), (560, 800), 29)
speech(im, ['嗯，走吧。'], (1080, 300), (1010, 720), 29)
num(im, 2)
save_png(im, OUT / 'page-02.png')
pages.append(im)

# 第3页：试衣与真心夸奖。哥哥不是敷衍，正面接住“不许敷衍我”。
im = scene('shot-03.png')
speech(im, ['这件怎么样？'], (300, 150), (480, 700), 28)
speech(im, ['你先试，我看看。'], (1080, 150), (970, 610), 28)
speech(im, ['那你不许敷衍我。'], (300, 360), (480, 700), 28)
speech(im, ['没敷衍。', '很好看，这颜色很衬你。'], (1080, 380), (970, 610), 28)
num(im, 3)
save_png(im, OUT / 'page-03.png')
pages.append(im)

# 第4页：哥哥正装试穿，妹妹被惊艳。正装只是试穿，后续外出服连续。
im = scene('shot-04.png')
speech(im, ['哇……二哥，', '你穿正装这么帅的吗？'], (330, 170), (480, 720), 29)
speech(im, ['嗯，走吧。'], (1080, 170), (970, 600), 29)
num(im, 4)
save_png(im, OUT / 'page-04.png')
pages.append(im)

im = scene('shot-05.png')
speech(im, ['这个好吃，你尝一口。'], (330, 160), (560, 900), 29)
speech(im, ['嗯，不错。'], (1080, 160), (900, 880), 29)
speech(im, ['那再给我留一点。'], (330, 360), (560, 900), 28)
num(im, 5)
save_png(im, OUT / 'page-05.png')
pages.append(im)

im = scene('shot-06.png')
speech(im, ['两头吸管，', '正好一起喝。'], (300, 150), (590, 770), 29)
speech(im, ['嗯，一起。'], (1100, 170), (930, 750), 29)
num(im, 6)
save_png(im, OUT / 'page-06.png')
pages.append(im)

im = scene('shot-07.png')
speech(im, ['靠近一点，看镜头！'], (300, 140), (500, 830), 28)
speech(im, ['这样？'], (1100, 150), (960, 730), 28)
speech(im, ['对，笑一下嘛。'], (300, 350), (500, 830), 28)
num(im, 7)
save_png(im, OUT / 'page-07.png')
pages.append(im)

# 第8页：原锁定第7个事件。女同学先问，妹妹答指定句；哥哥不接话。
im = scene('shot-08.png')
speech(im, ['这位是……？'], (1080, 130), (1050, 700), 29)
speech(im, ['这个是我男朋友。'], (700, 220), (700, 820), 30)
num(im, 8)
save_png(im, OUT / 'page-08.png')
pages.append(im)

im = scene('shot-09.png')
speech(im, ['我才回来，', '位置就被你们占完了？'], (1080, 130), (1050, 650), 28)
speech(im, ['小叔，我也要！'], (1080, 340), (870, 1150), 29)
speech(im, ['走，小满，我们一起。'], (350, 520), (1050, 650), 28)
num(im, 9)
save_png(im, OUT / 'page-09.png')
pages.append(im)

save_lossless_pdf_from_paths(sorted(OUT.glob('page-*.png')), ROOT / 'deliverables/第三话_妹妹的休息日.pdf', resolution=150)
vertical_pages = []
for source_path in sorted(OUT.glob('page-*.png')):
    source = Image.open(source_path).convert('RGB')
    assert source.size == (W, H), f'Unexpected page size: {source_path}: {source.size}'
    vertical = Image.new('RGB', VERTICAL_SIZE, PAPER)
    vertical.paste(source, (0, (VERTICAL_SIZE[1] - H) // 2))
    save_png(vertical, VERTICAL_OUT / source_path.name)
    vertical_pages.append(vertical)
save_lossless_pdf_from_paths(sorted(VERTICAL_OUT.glob('page-*.png')), ROOT / 'deliverables/第三话_竖屏全页漫画.pdf', resolution=150)
print('Built chapter 03:', len(pages), 'pages (cover + 9 story pages)')
