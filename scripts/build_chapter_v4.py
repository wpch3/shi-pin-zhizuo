from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text

ROOT = Path(__file__).resolve().parents[1]
W, H = 1440, 1920
SRC = ROOT / 'art/chapter-01-v4'
OUT = ROOT / 'deliverables/full-v4/chapter-01'
OUT.mkdir(parents=True, exist_ok=True)
VERTICAL_OUT = ROOT / 'deliverables/full-v4-vertical/chapter-01'
VERTICAL_OUT.mkdir(parents=True, exist_ok=True)
VERTICAL_SIZE = (1440, 2146)
FONT = ROOT / 'assets/fonts/NotoSansCJKsc-Bold.otf'
PAPER = '#F8F4EB'
INK = '#292B2C'
RED = '#92504C'
YELLOW = '#E9BD4F'
MUTED = '#746E67'


def ft(n):
    return ImageFont.truetype(str(FONT), n)


def scene(name):
    return Image.open(SRC / name).convert('RGB').resize((W, H), Image.Resampling.LANCZOS)


def cover_title(d, s, size=66):
    d.text((38, 28), s, font=ft(size), fill=YELLOW, stroke_width=4, stroke_fill=INK)


def speech(im, lines, center, target, size=30):
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


def caption(im, title, lines, xy, size=27):
    """画外转述caption：明确来源、无尾巴，与普通对白椭圆区分。"""
    d = ImageDraw.Draw(im)
    f, label_f = ft(size), ft(20)
    widths = [d.textbbox((0, 0), line, font=f)[2] for line in lines]
    w = max(widths + [d.textbbox((0, 0), title, font=label_f)[2]]) + 52
    h = 48 + len(lines)*(size+10) + 20
    x, y = xy
    d.rounded_rectangle((x, y, x+w, y+h), radius=18, fill=INK, outline=INK, width=3)
    d.text((x+24, y+14), title, font=label_f, fill=YELLOW)
    ty = y+51
    for line in lines:
        d.text((x+26, ty), line, font=f, fill=PAPER)
        ty += size+10
    return (x, y, x+w, y+h)


def num(im, n=None):
    d = ImageDraw.Draw(im)
    s = 'COVER' if n is None else f'{n:02d} / 07'
    d.text((1250, 1855), s, font=ft(18), fill=MUTED)


def unify_schedule_paper(im, quad, delta=(-5, -11, -25)):
    """仅调整纸内近白低色度像素，保留纸张明暗、手、笔与桌面颜色。"""
    mask_im = Image.new('L', im.size)
    ImageDraw.Draw(mask_im).polygon(quad, fill=255)
    pixels = np.asarray(im).copy()
    mask = np.asarray(mask_im) > 0
    chroma = pixels.max(axis=2).astype(int) - pixels.min(axis=2).astype(int)
    paper = mask & (pixels.min(axis=2) > 180) & (chroma < 35)
    adjusted = np.clip(pixels.astype(int) + np.asarray(delta), 0, 255).astype(np.uint8)
    pixels[paper] = adjusted[paper]
    im.paste(Image.fromarray(pixels, 'RGB'), (0, 0))


def perspective_schedule(im, title_s, rows, quad, source_size, title_size=58, row_size=46,
                         row_step=96, title_y=25, start_y=125, margin=42):
    """整张文字层按纸面四角透视映射；所有文字先留纸内安全边距，再三倍渲染降采样。"""
    # 这两页纸张均为菱形视角：阅读起点必须是上尖角，而非左尖角。
    assert quad[0][1] == min(p[1] for p in quad), '纸张阅读起点必须是上尖角'
    assert quad[1][0] == max(p[0] for p in quad), '纸张第二角必须是右尖角'
    assert quad[2][1] == max(p[1] for p in quad), '纸张第三角必须是下尖角'
    assert quad[3][0] == min(p[0] for p in quad), '纸张第四角必须是左尖角'
    sw, sh = source_size
    ss = 3
    layer = Image.new('RGBA', (sw*ss, sh*ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text((margin*ss, title_y*ss), title_s, font=ft(title_size*ss), fill=RED)
    y = start_y*ss
    for row in rows:
        d.text((margin*ss, y), row, font=ft(row_size*ss), fill=INK)
        y += row_step*ss
    assert y <= (sh-20)*ss, 'Schedule exceeds source paper safety area'
    src = ((0, 0), (sw*ss, 0), (sw*ss, sh*ss), (0, sh*ss))
    a, b = [], []
    for (x, y), (u, v) in zip(quad, src):
        x *= ss
        y *= ss
        a.extend(([x, y, 1, 0, 0, 0, -u*x, -u*y],
                  [0, 0, 0, x, y, 1, -v*x, -v*y]))
        b.extend((u, v))
    coeffs = np.linalg.solve(np.asarray(a, dtype=float), np.asarray(b, dtype=float))
    warped = layer.transform((W*ss, H*ss), Image.Transform.PERSPECTIVE,
                             coeffs, Image.Resampling.BICUBIC)
    warped = warped.resize((W, H), Image.Resampling.LANCZOS)
    im.paste(warped, (0, 0), warped)


pages = []

im = scene('cover.png')
d = ImageDraw.Draw(im)
cover_title(d, '休假回来的姐姐……')
speech(im, ['星野，这次长假，', '先陪我，好不好？'], (520, 220), (910, 465), 30)
d = ImageDraw.Draw(im)
d.text((60, 1780), '《二弟的休息日被全家预约了》 第一话', font=ft(25), fill=RED, stroke_width=2, stroke_fill=PAPER)
num(im)
im.save(OUT/'page-00-cover.png')
pages.append(im)

im = scene('shot-01.png')
speech(im, ['项目搞定！', '从今天起，我是家里蹲。'], (390, 110), (735, 400), 30)
num(im, 1)
im.save(OUT/'page-01.png')
pages.append(im)

im = scene('shot-02.png')
speech(im, ['这次我会多住一阵子，', '以前没时间陪你的，', '慢慢补回来。'],
       (255, 335), (510, 750), 28)
num(im, 2)
im.save(OUT/'page-02.png')
pages.append(im)

im = scene('shot-03.png')
speech(im, ['我刚回来，', '今天先归我。'], (230, 180), (336, 480), 30)
speech(im, ['二哥，', '今天先陪我！'], (1120, 400), (1008, 704), 30)
num(im, 3)
im.save(OUT/'page-03.png')
pages.append(im)

im = scene('shot-04.png')
speech(im, ['小满，', '连你也来抢呀？'], (1130, 340), (1176, 624), 28)
speech(im, ['小叔先陪我', '搭城堡啦。'], (200, 680), (368, 912), 28)
num(im, 4)
im.save(OUT/'page-04.png')
pages.append(im)

im = scene('shot-05.png')
speech(im, ['别抢啦，', '我把时间都排好了。'], (1220, 235), (760, 330), 28)
# 四角必须按阅读方向排列：纸上→纸右→纸下→纸左；纸色与第6页统一。
schedule_05_quad = ((951, 1056), (1104, 1128), (781, 1360), (601, 1179))
unify_schedule_paper(im, schedule_05_quad)
perspective_schedule(
    im, '星野的日程表',
    ['1. 陪姐姐散步', '2. 陪妹妹挑书', '3. 陪小满搭城堡，', '   再讲三遍故事'],
    schedule_05_quad,
    (650, 500), title_size=42, row_size=36, row_step=68,
    title_y=60, start_y=130, margin=230)
num(im, 5)
im.save(OUT/'page-05.png')
pages.append(im)

im = scene('shot-06.png')
speech(im, ['安排得挺好，', '不过得先把他', '休息的时间排上。'], (950, 130), (760, 510), 28)
speech(im, ['我也有自己的', '行程啊？'], (450, 235), (584, 760), 30)
perspective_schedule(
    im, '星野的日程表',
    ['1. 陪姐姐散步', '2. 陪妹妹挑书', '3. 陪小满搭城堡，', '   再讲三遍故事', '4. 二弟睡觉'],
    ((937, 1142), (1297, 1206), (932, 1579), (562, 1419)),
    (600, 760), title_size=48, row_size=40, row_step=60,
    title_y=380, start_y=440, margin=32)
num(im, 6)
im.save(OUT/'page-06.png')
pages.append(im)

im = scene('shot-07.png')
caption(im, '妈妈转述', ['你哥哥跟你说，项目结束就好，', '早点休息，别熬夜。'], (55, 55), 27)
speech(im, ['小叔，等你休息好了，', '再陪我讲故事嘛。'], (220, 835), (390, 1070), 27)
d = ImageDraw.Draw(im)
d.rounded_rectangle((50, 1795, 585, 1870), radius=18, fill=INK)
d.text((75, 1815), '二弟被预约的第一天，正式开始。', font=ft(22), fill=YELLOW)
num(im, 7)
im.save(OUT/'page-07.png')
pages.append(im)

pages[0].save(ROOT/'deliverables/第一话_V4_精细化重制.pdf', save_all=True,
              append_images=pages[1:], resolution=150)
vertical_pages = []
for source_path in sorted(OUT.glob('page-*.png')):
    source = Image.open(source_path).convert('RGB')
    assert source.size == (W, H), f'Unexpected approved page size: {source_path}: {source.size}'
    vertical = Image.new('RGB', VERTICAL_SIZE, PAPER)
    vertical.paste(source, (0, (VERTICAL_SIZE[1]-H)//2))
    vertical.save(VERTICAL_OUT/source_path.name)
    vertical_pages.append(vertical)
vertical_pages[0].save(ROOT/'deliverables/第一话_竖屏全页漫画.pdf', save_all=True,
                       append_images=vertical_pages[1:], resolution=150)
print('Built chapter 1 with measured elliptical speech balloons:', len(pages), 'pages')
print('Built reference-ratio vertical edition:', len(vertical_pages), 'pages', VERTICAL_SIZE)
