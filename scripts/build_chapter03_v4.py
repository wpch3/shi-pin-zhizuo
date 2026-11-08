"""第三话构建入口：封面 + 9页正片 = 10页。

2026-11-08 返修版（v5 原画）：
- 用户第三次指出“无意义空白 + 黑边”，根因是旧 scene() 用 ImageOps.contain 把生图自带的
  纸边/画内框线/顶部空白格原样贴进纸底，且气泡被排进那个空白格。现在原画已重绘为真正
  四边铺满，scene() 改用 ImageOps.fit 做 0.4% 画幅归一化，保证成品无任何纸色外边距。
- 第6页改为“妹妹害羞强撑、哥哥也害羞”，并把两根独立吸管改回锁定道具“一根Y形两头吸管”。
- 第9页重绘锚定 shot-01 画风，修复线条/上色/脸型漂移，并补足“姐姐带小满爬上床、哥哥掀被容纳”。
- 页码改为按背景亮度自动取反色并描边，修复深色背景上页码不可见。
- 气泡坐标全部按 v5 新构图的真实场景负空间重排，不沿用旧坐标。

用户已确认把“买衣服试衣服”拆成两个镜头；原锁定第7个事件（女同学问答）在10页版中为第8页。
台词和禁止项不变。缺少已审查原画时明确失败，禁止用立绘、旧话原画或占位图冒充正片。
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text
from pdf_export import save_lossless_pdf_from_paths

ROOT = Path(__file__).resolve().parents[1]
W, H = 1440, 1920
VERTICAL_SIZE = (1440, 2146)
SRC = ROOT / 'art/chapter-03-v5'
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
    """四边铺满：只做 0.4% 画幅归一化裁切，绝不贴纸底、绝不保留生图自带纸边。"""
    path = SRC / name
    if not path.exists():
        raise FileNotFoundError(f'缺少已审查的第三话原画：{path}；不得用占位图或立绘替代。')
    source = Image.open(path).convert('RGB')
    return ImageOps.fit(source, (W, H), Image.Resampling.LANCZOS, centering=(0.5, 0.5))


def speech(im, lines, center, target, size=29, tail=30):
    """tail 可加长：说话者与气泡距离远时，长尾指向本人，避免误判归属。"""
    d = ImageDraw.Draw(im)
    f = ft(size)
    layout = measure_speech_text(d, lines, center, f, size)
    bw, bh = layout['bubble_size']
    outline = oval_speech(center, (bw, bh), target, tail_length=tail, tail_width=28, bend=2)
    d.polygon(outline, fill=PAPER)
    d.line(outline + [outline[0]], fill=INK, width=3, joint='curve')
    for x, y, line in layout['positions']:
        d.text((x, y), line, font=f, fill=INK)
    return layout['box']


def num(im, n=None):
    """页码：按所在背景亮度自动取反色并加同底描边，深底浅底都保证可读。"""
    d = ImageDraw.Draw(im)
    value = 'COVER' if n is None else f'{n:02d} / 09'
    pos = (1250, 1855)
    f = ft(18)
    box = d.textbbox(pos, value, font=f)
    pad = 6
    region = np.asarray(im.crop((max(0, box[0] - pad), max(0, box[1] - pad),
                                 min(W, box[2] + pad), min(H, box[3] + pad)))).mean()
    if region < 150:
        fill, stroke = PAPER, INK
    else:
        fill, stroke = INK, PAPER
    d.text(pos, value, font=f, fill=fill, stroke_width=2, stroke_fill=stroke)


def save_png(im, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, optimize=True, compress_level=9)


missing = [name for name in REQUIRED if not (SRC / name).exists()]
if missing:
    raise FileNotFoundError('第三话尚缺已审查原画：' + ', '.join(missing))
OUT.mkdir(parents=True, exist_ok=True)
VERTICAL_OUT.mkdir(parents=True, exist_ok=True)
pages = []

# 封面：主角妹妹全身独立构图，双脚完整在画内；标题压在天空/雨棚实景区，不是留白带。
im = scene('cover.png')
d = ImageDraw.Draw(im)
d.text((40, 45), '二弟的休息日被全家预约了', font=ft(56), fill=YELLOW, stroke_width=4, stroke_fill=INK)
d.text((40, 135), '第三话', font=ft(32), fill=PAPER, stroke_width=3, stroke_fill=INK)
num(im)
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

# 第4页：哥哥正装试穿，妹妹被惊艳。气泡落在店内天花板/墙面实景，不是自带空白格。
im = scene('shot-04.png')
speech(im, ['哇……二哥，', '你穿正装这么帅的吗？'], (330, 300), (420, 610), 29)
speech(im, ['嗯，走吧。'], (1090, 230), (880, 440), 29)
num(im, 4)
save_png(im, OUT / 'page-04.png')
pages.append(im)

# 第5页：小吃摊。招牌只画食物图与色块，无乱码假字。
im = scene('shot-05.png')
speech(im, ['这个好吃，你尝一口。'], (330, 190), (470, 830), 29, tail=80)
speech(im, ['嗯，不错。'], (1100, 200), (960, 730), 29)
speech(im, ['那再给我留一点。'], (330, 410), (470, 830), 28, tail=70)
num(im, 5)
save_png(im, OUT / 'page-05.png')
pages.append(im)

# 第6页：害羞强撑。一根Y形两头吸管；两人都脸红耳根、视线躲闪。
im = scene('shot-06.png')
speech(im, ['两头吸管，', '正好一起喝。'], (300, 200), (470, 690), 29)
speech(im, ['嗯，一起。'], (1120, 190), (960, 620), 29)
num(im, 6)
save_png(im, OUT / 'page-06.png')
pages.append(im)

# 第7页：大头照。阅读顺序 妹→妹→哥，靠纵向分层保证。
im = scene('shot-07.png')
speech(im, ['靠近一点，看镜头！'], (330, 180), (520, 700), 28)
speech(im, ['对，笑一下嘛。'], (300, 400), (520, 700), 28)
speech(im, ['这样？'], (1230, 430), (1000, 620), 28)
num(im, 7)
save_png(im, OUT / 'page-07.png')
pages.append(im)

# 第8页：女同学在左先问，妹妹在右答指定句；哥哥不接话。
im = scene('shot-08.png')
speech(im, ['这位是……？'], (300, 200), (400, 620), 29)
speech(im, ['这个是我男朋友。'], (830, 300), (830, 660), 30)
num(im, 8)
save_png(im, OUT / 'page-08.png')
pages.append(im)

# 第9页：姐姐带小满爬上床，哥哥掀被容纳。三泡纵向分层保证阅读顺序。
im = scene('shot-09.png')
speech(im, ['我才回来，', '位置就被你们占完了？'], (350, 190), (540, 660), 28)
speech(im, ['小叔，我也要！'], (1080, 330), (1030, 1110), 29, tail=110)
speech(im, ['走，小满，我们一起。'], (220, 900), (530, 670), 28)
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
