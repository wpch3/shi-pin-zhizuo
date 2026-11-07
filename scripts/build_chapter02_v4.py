from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

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


def wrap(draw, value, font, width):
    lines, line = [], ''
    for ch in value:
        if draw.textbbox((0, 0), line + ch, font=font)[2] > width and line:
            lines.append(line)
            line = ch
        else:
            line += ch
    if line:
        lines.append(line)
    return lines


def text(draw, value, xy, width, size=32, fill=INK, gap=12):
    x, y = xy
    font = ft(size)
    for line in wrap(draw, value, font, width):
        draw.text((x, y), line, font=font, fill=fill)
        y += size + gap
    return y


def bubble(im, speaker, value, box, size=30, tail='left'):
    """统一暖白圆角对白；尾巴只描两侧，接口不多横线。"""
    draw = ImageDraw.Draw(im)
    x, y, w, h = box
    points = None
    if tail == 'left':
        points = ((x + 60, y + h - 3), (x + 105, y + h - 3), (x + 76, y + h + 27))
    elif tail == 'right':
        points = ((x + w - 105, y + h - 3), (x + w - 60, y + h - 3), (x + w - 76, y + h + 27))
    if points:
        draw.polygon(points, fill=PAPER)
        draw.line((points[0], points[2], points[1]), fill=INK, width=3, joint='curve')
    draw.rounded_rectangle((x, y, x + w, y + h), radius=28, fill=PAPER, outline=INK, width=3)
    draw.text((x + 24, y + 15), speaker, font=ft(21), fill=RED)
    text(draw, value, (x + 24, y + 55), w - 48, size=size, gap=9)


def scene(name):
    path = SRC / name
    if not path.exists():
        raise FileNotFoundError(f'缺少已审查的第二话原画：{path}')
    return Image.open(path).convert('RGB').resize((W, H), Image.Resampling.LANCZOS)


def num(im, n=None):
    draw = ImageDraw.Draw(im)
    value = 'COVER' if n is None else f'{n:02d} / 07'
    draw.text((1250, 1855), value, font=ft(18), fill=MUTED)


pages = []

im = scene('cover.png')
draw = ImageDraw.Draw(im)
draw.text((38, 28), '二姐的独占时间', font=ft(66), fill=YELLOW, stroke_width=4, stroke_fill=INK)
bubble(im, '江望舒', '今天没人要抢你咯，专心陪着姐姐我哦。', (55, 140, 650, 170), 29, tail='right')
draw = ImageDraw.Draw(im)
draw.text((60, 1780), '第二话', font=ft(25), fill=RED)
num(im)
im.save(OUT / 'page-00-cover.png')
pages.append(im)

im = scene('shot-01.png')
bubble(im, '江望舒', '他们晚上才回来。电脑先关了，今天不许忙工作。', (55, 55, 820, 180), 29, tail='left')
bubble(im, '江星野', '……嗯。', (1040, 70, 280, 135), 29, tail='right')
num(im, 1)
im.save(OUT / 'page-01.png')
pages.append(im)

im = scene('shot-02.png')
bubble(im, '江望舒', '第一件事，帮我把内衣和袜子洗了。', (55, 50, 850, 175), 29, tail='left')
bubble(im, '江望舒', '你洗，我陪。', (55, 265, 420, 145), 29, tail='left')
bubble(im, '江星野', '……这就是你说的陪你？', (790, 50, 540, 155), 28, tail='right')
num(im, 2)
im.save(OUT / 'page-02.png')
pages.append(im)

im = scene('shot-03.png')
bubble(im, '江望舒', '水温别太高，袜子和内衣分开——', (55, 50, 880, 170), 29, tail='right')
bubble(im, '江星野', '到底谁洗？', (55, 260, 470, 140), 29, tail='left')
bubble(im, '江望舒', '你洗，我负责指挥。', (650, 260, 680, 145), 28, tail='right')
num(im, 3)
im.save(OUT / 'page-03.png')
pages.append(im)

im = scene('shot-04.png')
bubble(im, '江星野', '小时候你也这样指挥我？', (55, 50, 690, 155), 29, tail='left')
bubble(im, '江望舒', '小时候是我洗，你在旁边玩。现在换你照顾我，不行吗？', (55, 245, 1010, 175), 28, tail='right')
num(im, 4)
im.save(OUT / 'page-04.png')
pages.append(im)

im = scene('shot-05.png')
bubble(im, '江星野', '知道了，妈——', (55, 50, 540, 145), 29, tail='left')
bubble(im, '江望舒', '你刚才叫我什么？', (930, 50, 390, 145), 29, tail='right')
bubble(im, '江星野', '口误。', (55, 260, 330, 135), 29, tail='left')
bubble(im, '江望舒', '我不管，反正我听到了。再叫一次嘛。', (540, 250, 790, 170), 28, tail='right')
num(im, 5)
im.save(OUT / 'page-05.png')
pages.append(im)

im = scene('shot-06.png')
bubble(im, '江望舒', '辛苦啦，奖励你陪姐姐睡半小时。', (55, 50, 850, 170), 29, tail='left')
bubble(im, '江星野', '到底是谁辛苦？', (850, 50, 450, 140), 29, tail='right')
bubble(im, '江望舒', '我陪你也很辛苦呀。', (55, 260, 620, 145), 29, tail='left')
num(im, 6)
im.save(OUT / 'page-06.png')
pages.append(im)

im = scene('shot-07.png')
bubble(im, '江望舒', '星野，别走。', (55, 55, 450, 145), 29, tail='left')
bubble(im, '江星野', '睡吧，我不走。', (800, 55, 500, 145), 29, tail='right')
draw = ImageDraw.Draw(im)
draw.rounded_rectangle((50, 1785, 1130, 1870), radius=18, fill=INK)
# 第三人称结尾，不使用“我陪姐姐”等第一人称旁白。
draw.text((75, 1804), '二姐睡了一个好觉，二弟陪她睡了一整个下午。', font=ft(25), fill=YELLOW)
num(im, 7)
im.save(OUT / 'page-07.png')
pages.append(im)

pages[0].save(ROOT / 'deliverables/第二话_二姐的独占时间.pdf', save_all=True, append_images=pages[1:], resolution=150)
vertical_pages = []
for source_path in sorted(OUT.glob('page-*.png')):
    source = Image.open(source_path).convert('RGB')
    vertical = Image.new('RGB', VERTICAL_SIZE, PAPER)
    vertical.paste(source, (0, (VERTICAL_SIZE[1] - H) // 2))
    vertical.save(VERTICAL_OUT / source_path.name)
    vertical_pages.append(vertical)
vertical_pages[0].save(ROOT / 'deliverables/第二话_竖屏全页漫画.pdf', save_all=True, append_images=vertical_pages[1:], resolution=150)
print('Built chapter 02:', len(pages), 'reading pages and', len(vertical_pages), 'vertical pages')
