"""第三话构建入口（开工版）。

当前只完成服装设定与分镜；封面和8页正片原画尚未生图。
本脚本在缺少已审查原画时明确失败，禁止用立绘、旧话原画或占位图冒充正片。
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text
from pdf_export import save_lossless_pdf

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
REQUIRED = ['cover.png'] + [f'shot-{i:02d}.png' for i in range(1, 9)]


def ft(size):
    return ImageFont.truetype(str(FONT), size)


def scene(name):
    path = SRC / name
    if not path.exists():
        raise FileNotFoundError(f'缺少已审查的第三话原画：{path}；不得用占位图或立绘替代。')
    return Image.open(path).convert('RGB').resize((W, H), Image.Resampling.LANCZOS)


def speech(im, lines, center, target, size=29):
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
    value = 'COVER' if n is None else f'{n:02d} / 08'
    d.text((1250, 1855), value, font=ft(18), fill=MUTED)


def main():
    missing = [name for name in REQUIRED if not (SRC / name).exists()]
    if missing:
        raise FileNotFoundError('第三话尚缺已审查原画：' + ', '.join(missing))
    OUT.mkdir(parents=True, exist_ok=True)
    VERTICAL_OUT.mkdir(parents=True, exist_ok=True)
    pages = []

    # 封面：主角妹妹，独立构图；标题不提前使用第7页指定句。
    im = scene('cover.png')
    d = ImageDraw.Draw(im)
    d.text((38, 28), '二弟的休息日被全家预约了', font=ft(58), fill=YELLOW, stroke_width=4, stroke_fill=INK)
    d.text((60, 1780), '第三话', font=ft(25), fill=RED, stroke_width=2, stroke_fill=PAPER)
    num(im)
    im.save(OUT/'page-00-cover.png')
    pages.append(im)

    # 以下坐标为开工预排，生图后必须按实际留白逐页目检调整；不得未看实际成图即交付。
    plans = [
        ('shot-01.png', [
            (['二哥，七点啦！', '说好今天陪我逛街的。'], (350, 300), (430, 760), 29),
            (['……起，', '给我两分钟。'], (1080, 380), (1010, 820), 29),
        ]),
        ('shot-02.png', [
            (['收拾好了，出发！'], (350, 260), (430, 720), 29),
            (['嗯，走吧。'], (1080, 330), (1010, 760), 29),
        ]),
        ('shot-03.png', [
            (['这件怎么样？'], (330, 250), (420, 700), 29),
            (['你先试，我看看。'], (1080, 300), (1010, 740), 29),
            (['那你不许敷衍我。'], (360, 520), (420, 700), 28),
        ]),
        ('shot-04.png', [
            (['这个好吃，你尝一口。'], (340, 260), (430, 720), 29),
            (['嗯，不错。'], (1080, 320), (1010, 760), 29),
            (['那再给我留一点。'], (360, 520), (430, 720), 28),
        ]),
        ('shot-05.png', [
            (['两头吸管，', '正好一起喝。'], (340, 280), (430, 760), 29),
            (['嗯，一起。'], (1080, 340), (1010, 780), 29),
        ]),
        ('shot-06.png', [
            (['靠近一点，看镜头！'], (340, 250), (430, 720), 29),
            (['这样？'], (1080, 310), (1010, 750), 29),
            (['对，笑一下嘛。'], (360, 520), (430, 720), 28),
        ]),
        ('shot-07.png', [
            (['这位是……？'], (1080, 260), (1030, 700), 29),
            (['这个是我男朋友。'], (380, 420), (470, 780), 30),
        ]),
        ('shot-08.png', [
            (['我才回来，', '位置就被你们占完了？'], (330, 260), (420, 720), 28),
            (['小叔，我也要！'], (1080, 330), (1010, 780), 29),
            (['走，小满，我们一起。'], (360, 540), (420, 720), 28),
        ]),
    ]
    for i, (name, bubbles) in enumerate(plans, start=1):
        im = scene(name)
        for lines, center, target, size in bubbles:
            speech(im, lines, center, target, size)
        num(im, i)
        im.save(OUT/f'page-{i:02d}.png')
        pages.append(im)

    save_lossless_pdf(pages, ROOT/'deliverables/第三话_妹妹的休息日.pdf', resolution=150)
    vertical_pages = []
    for source_path in sorted(OUT.glob('page-*.png')):
        source = Image.open(source_path).convert('RGB')
        assert source.size == (W, H), f'Unexpected page size: {source_path}: {source.size}'
        vertical = Image.new('RGB', VERTICAL_SIZE, PAPER)
        vertical.paste(source, (0, (VERTICAL_SIZE[1]-H)//2))
        vertical.save(VERTICAL_OUT/source_path.name)
        vertical_pages.append(vertical)
    save_lossless_pdf(vertical_pages, ROOT/'deliverables/第三话_竖屏全页漫画.pdf', resolution=150)
    print('Built chapter 03:', len(pages), 'pages')


if __name__ == '__main__':
    main()
