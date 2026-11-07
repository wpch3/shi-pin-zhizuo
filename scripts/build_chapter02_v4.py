from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from speech_bubble_geometry import oval_speech

ROOT = Path(__file__).resolve().parents[1]
W, H = 1440, 1920
VERTICAL_SIZE = (1440, 2146)
SRC = ROOT / 'art/chapter-02-v4'
OUT = ROOT / 'deliverables/full-v4/chapter-02'
VERTICAL_OUT = ROOT / 'deliverables/full-v4-vertical/chapter-02'
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
    path = SRC / name
    if not path.exists():
        raise FileNotFoundError(f'缺少已审查的第二话原画：{path}')
    return Image.open(path).convert('RGB').resize((W, H), Image.Resampling.LANCZOS)


def speech(im, lines, center, target, size=29):
    """测量文字生成椭圆；采用MIT开源Speechbubble曲线尾巴与圆角描边。"""
    d = ImageDraw.Draw(im)
    f = ft(size)
    gap = round(size * 0.34)
    boxes = [d.textbbox((0, 0), line, font=f) for line in lines]
    widths = [b[2]-b[0] for b in boxes]
    line_h = size + gap
    text_h = len(lines)*line_h-gap
    pad_x, pad_y = round(size*1.12), round(size*0.84)
    bw = max(widths)+2*pad_x+16
    bh = text_h+2*pad_y+14
    cx, cy = center
    box = (round(cx-bw/2), round(cy-bh/2), round(cx+bw/2), round(cy+bh/2))

    outline = oval_speech(center, (bw, bh), target, tail_length=30, tail_width=28, bend=2)
    # 椭圆与尾巴是同一闭合外轮廓；根部没有第二层椭圆弧或三角底边。
    d.polygon(outline, fill=PAPER)
    d.line(outline+[outline[0]], fill=INK, width=3, joint='curve')

    y = cy-text_h/2
    for line, width, b in zip(lines, widths, boxes):
        d.text((cx-width/2-b[0], y-b[1]), line, font=f, fill=INK)
        y += line_h
    return box


def num(im, n=None):
    d = ImageDraw.Draw(im)
    value = 'COVER' if n is None else f'{n:02d} / 07'
    d.text((1250, 1855), value, font=ft(18), fill=MUTED)


pages = []

im = scene('cover.png')
d = ImageDraw.Draw(im)
d.text((38, 28), '二姐的独占时间', font=ft(66), fill=YELLOW, stroke_width=4, stroke_fill=INK)
speech(im, ['今天没人要抢你咯，', '专心陪着姐姐我哦。'], (1000, 190), (995, 466), 29)
d = ImageDraw.Draw(im)
d.text((60, 1780), '《二弟的休息日被全家预约了》 第二话', font=ft(25), fill=RED, stroke_width=2, stroke_fill=PAPER)
num(im)
im.save(OUT/'page-00-cover.png')
pages.append(im)

im = scene('shot-01.png')
speech(im, ['他们晚上才回来。', '电脑先关了，', '今天不许再忙工作。'], (350, 590), (610, 907), 29)
speech(im, ['……嗯。'], (1100, 690), (1045, 965), 29)
num(im, 1)
im.save(OUT/'page-01.png')
pages.append(im)

im = scene('shot-02.png')
speech(im, ['第一件事，', '帮我把内衣和袜子洗了。'], (300, 500), (418, 867), 29)
speech(im, ['……这就是', '你说的陪你？'], (1090, 555), (1045, 803), 28)
speech(im, ['你洗，我陪。'], (650, 735), (418, 867), 29)
num(im, 2)
im.save(OUT/'page-02.png')
pages.append(im)

im = scene('shot-03.png')
speech(im, ['水温别太高，', '袜子和内衣', '分开洗——'], (1100, 400), (1173, 1028), 29)
speech(im, ['到底谁洗？'], (320, 650), (514, 915), 29)
speech(im, ['你洗，', '我负责指挥。'], (810, 770), (1173, 1028), 28)
num(im, 3)
im.save(OUT/'page-03.png')
pages.append(im)

im = scene('shot-04.png')
speech(im, ['小时候你也这样', '指挥我？'], (300, 420), (642, 835), 29)
speech(im, ['小时候是我洗，', '你在旁边玩。', '现在换你照顾我，', '不行吗？'], (1080, 500), (1045, 900), 27)
num(im, 4)
im.save(OUT/'page-04.png')
pages.append(im)

im = scene('shot-05.png')
speech(im, ['知道了，妈——'], (250, 330), (650, 835), 29)
speech(im, ['你刚才', '叫我什么？'], (1100, 300), (1045, 900), 29)
speech(im, ['口误。'], (650, 500), (650, 835), 29)
speech(im, ['我不管，反正我听到了。', '再叫一次嘛。'], (1050, 585), (1045, 900), 27)
num(im, 5)
im.save(OUT/'page-05.png')
pages.append(im)

im = scene('shot-06.png')
speech(im, ['辛苦啦，奖励你', '陪姐姐午睡半小时。'], (250, 300), (642, 835), 29)
speech(im, ['到底是谁辛苦？'], (1200, 380), (996, 643), 29)
speech(im, ['我陪你也很辛苦呀。'], (220, 565), (642, 835), 28)
num(im, 6)
im.save(OUT/'page-06.png')
pages.append(im)

im = scene('shot-07.png')
speech(im, ['星野，别走。'], (700, 120), (884, 578), 29)
speech(im, ['睡吧，我不走。'], (1100, 120), (1092, 321), 29)
d = ImageDraw.Draw(im)
d.rounded_rectangle((50, 1785, 1130, 1870), radius=18, fill=INK)
d.text((75, 1804), '二姐睡了一个好觉，二弟陪她睡了一整个下午。', font=ft(25), fill=YELLOW)
num(im, 7)
im.save(OUT/'page-07.png')
pages.append(im)

pages[0].save(ROOT/'deliverables/第二话_二姐的独占时间.pdf', save_all=True,
              append_images=pages[1:], resolution=150)
vertical_pages = []
for source_path in sorted(OUT.glob('page-*.png')):
    source = Image.open(source_path).convert('RGB')
    assert source.size == (W, H), f'Unexpected page size: {source_path}: {source.size}'
    vertical = Image.new('RGB', VERTICAL_SIZE, PAPER)
    vertical.paste(source, (0, (VERTICAL_SIZE[1]-H)//2))
    vertical.save(VERTICAL_OUT/source_path.name)
    vertical_pages.append(vertical)
vertical_pages[0].save(ROOT/'deliverables/第二话_竖屏全页漫画.pdf', save_all=True,
                       append_images=vertical_pages[1:], resolution=150)
print('Built chapter 02 with measured elliptical speech balloons:', len(pages), 'pages')
print('Built reference-ratio vertical edition:', len(vertical_pages), 'pages', VERTICAL_SIZE)
