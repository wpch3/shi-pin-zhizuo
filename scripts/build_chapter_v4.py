from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
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


USER_FINAL = ROOT / 'art/user-final/chapter-01'
USER_MANIFEST = json.loads((USER_FINAL / 'manifest.json').read_text(encoding='utf-8'))


def user_final_page(page, size):
    """用户定稿只读适配：完整contain、不裁切、不拉伸、不改字、不重排。

    第五页阅读版与竖屏版沿用中央原画规则；第六页用户原图本身为53:79，
    竖屏版直接从原图适配，避免二次扩边缩小画面。原图永远只读。
    """
    spec = next(p for p in USER_MANIFEST['pages'] if p['page'] == page)
    path = USER_FINAL / spec['original']
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != spec['sha256']:
        raise RuntimeError(f'用户定稿原图哈希不符，禁止覆盖或替换: {path}')
    source = Image.open(path).convert('RGB')
    if list(source.size) != spec['original_size']:
        raise RuntimeError(f'用户定稿原图尺寸不符: {path}: {source.size}')
    fitted = ImageOps.contain(source, size, Image.Resampling.LANCZOS)
    fitted = fitted.filter(ImageFilter.UnsharpMask(radius=0.65, percent=38, threshold=3))
    result = Image.new('RGB', size, PAPER)
    result.paste(fitted, ((size[0]-fitted.width)//2, (size[1]-fitted.height)//2))
    return result


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
    """把正面排好的文字层按明确角点顺序映射到纸面，保留正常书写的小字块与空白。"""
    # quad依次对应正面文字层的左上、右上、右下、左下；两页原画纸张朝向不同，
    # 不能用同一组角点名称强行规定阅读轴，必须分别按原画和参考图确认。
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

# 用户最终定稿：不得再调用旧原画、气泡、纸色或日程透视流程。
im = user_final_page('05', (W, H))
im.save(OUT/'page-05.png')
pages.append(im)

im = user_final_page('06', (W, H))
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
              append_images=pages[1:], resolution=150, quality=95, subsampling=0)
vertical_pages = []
for source_path in sorted(OUT.glob('page-*.png')):
    source = Image.open(source_path).convert('RGB')
    assert source.size == (W, H), f'Unexpected approved page size: {source_path}: {source.size}'
    if source_path.name == 'page-06.png':
        vertical = user_final_page('06', VERTICAL_SIZE)
    else:
        vertical = Image.new('RGB', VERTICAL_SIZE, PAPER)
        vertical.paste(source, (0, (VERTICAL_SIZE[1]-H)//2))
    vertical.save(VERTICAL_OUT/source_path.name)
    vertical_pages.append(vertical)
vertical_pages[0].save(ROOT/'deliverables/第一话_竖屏全页漫画.pdf', save_all=True,
                       append_images=vertical_pages[1:], resolution=150, quality=95, subsampling=0)
print('Built chapter 1 with measured elliptical speech balloons:', len(pages), 'pages')
print('Built reference-ratio vertical edition:', len(vertical_pages), 'pages', VERTICAL_SIZE)
