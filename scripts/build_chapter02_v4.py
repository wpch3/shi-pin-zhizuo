from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

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


def quad_point(p0, p1, p2, t):
    return ((1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0],
            (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1])


def speech(im, lines, center, target, size=29):
    """按真实文字测量椭圆，画面内对白不写姓名标签；尾巴指向说话者嘴部方向。"""
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

    dx, dy = target[0]-cx, target[1]-cy
    rx, ry = bw/2, bh/2
    scale = 1/math.sqrt((dx/rx)**2+(dy/ry)**2)
    edge = (cx+dx*scale, cy+dy*scale)
    length = math.hypot(dx, dy)
    ux, uy = dx/length, dy/length
    base = (edge[0]-ux*8, edge[1]-uy*8)
    tip = (edge[0]+(target[0]-edge[0])*0.68,
           edge[1]+(target[1]-edge[1])*0.68)
    px, py = -uy*14, ux*14
    p0, p2 = (base[0]+px, base[1]+py), (base[0]-px, base[1]-py)
    c0 = (edge[0]+(tip[0]-edge[0])*0.35+px*0.35,
          edge[1]+(tip[1]-edge[1])*0.35+py*0.35)
    c1 = (edge[0]+(tip[0]-edge[0])*0.35-px*0.35,
          edge[1]+(tip[1]-edge[1])*0.35-py*0.35)
    tail = [quad_point(p0, c0, tip, i/12) for i in range(13)]
    tail += [quad_point(tip, c1, p2, i/12) for i in range(1, 13)]
    d.polygon(tail, fill=PAPER)
    d.line(tail+[tail[0]], fill=INK, width=3, joint='curve')
    d.ellipse(box, fill=PAPER, outline=INK, width=3)

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
d.text((60, 1780), '第二话', font=ft(25), fill=RED)
num(im)
im.save(OUT/'page-00-cover.png')
pages.append(im)

im = scene('shot-01.png')
speech(im, ['他们晚上才回来。', '电脑先关了，', '今天不许忙工作。'], (350, 590), (610, 907), 29)
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
speech(im, ['水温别太高，', '袜子和内衣', '分开——'], (1100, 400), (1173, 1028), 29)
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
speech(im, ['辛苦啦，奖励你', '陪姐姐睡半小时。'], (250, 300), (642, 835), 29)
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
