from pathlib import Path
import hashlib
import json
import sys
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageFilter, ImageOps
import numpy as np
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text
from pdf_export import save_lossless_pdf_from_paths

ROOT = Path(__file__).resolve().parents[1]
# 当前重绘尚未验收；避免误覆盖旧正式交付。
if sys.argv[1:] != ['--draft']:
    raise SystemExit('第一话重绘仍在制作中；仅可用 --draft 生成隔离试排，禁止覆盖正式交付。')
DRAFT = ROOT / 'deliverables/drafts/chapter-01'
W, H = 1440, 1920
SRC = ROOT / 'art/chapter-01-v4'
OUT = DRAFT / 'reading'
OUT.mkdir(parents=True, exist_ok=True)
VERTICAL_OUT = DRAFT / 'vertical'
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


def verify_user_final_archive():
    """用户第5/6页定稿归档：文件与哈希只读保留，但2026-11-09起不再作为正式图源。

    整话重绘并轨后，第5/6页改用 art/chapter-01-v4/shot-05.png、shot-06.png 新原画，
    中文日程表／气泡／页码全部由本脚本精确绘制（禁止AI生成中文）。此函数只校验
    归档原件与replacement的SHA-256及尺寸，确保旧定稿未被覆盖或改动，不读取其像素。
    """
    for spec in USER_MANIFEST['pages']:
        original = USER_FINAL / spec['original']
        if hashlib.sha256(original.read_bytes()).hexdigest() != spec['sha256']:
            raise RuntimeError(f'用户定稿归档原件哈希不符，禁止覆盖: {original}')
        replacement = spec.get('replacement')
        if replacement:
            path = USER_FINAL / replacement['path']
            if hashlib.sha256(path.read_bytes()).hexdigest() != replacement['sha256']:
                raise RuntimeError(f'用户定稿归档replacement哈希不符: {path}')
            if list(Image.open(path).size) != replacement['size']:
                raise RuntimeError(f'用户定稿归档尺寸不符: {path}')
    return True


verify_user_final_archive()


def schedule_card(im, box, rows, title='星野的日程表', title_size=46, row_size=38,
                  row_step=92, margin=34, tilt=0):
    """脚本精确绘制中文日程卡：白底细边框＋逐字排版，可轻微倾斜，绝不交给AI写中文。"""
    x0, y0, x1, y1 = box
    w, h = x1-x0, y1-y0
    card = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rectangle((0, 0, w-1, h-1), fill=(250, 247, 240, 255), outline=(70, 66, 62, 255), width=2)
    d.text((margin, 26), title, font=ft(title_size), fill=RED)
    y = 26 + title_size + 42
    for row in rows:
        d.text((margin, y), row, font=ft(row_size), fill=INK)
        y += row_step
    assert y < h - 16, '日程卡文字超出安全区'
    if tilt:
        card = card.rotate(tilt, resample=Image.Resampling.BICUBIC, expand=True)
        x0 -= (card.width-w)//2
        y0 -= (card.height-h)//2
    im.paste(card, (x0, y0), card)
    return (x0, y0, x0+card.width, y0+card.height)


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


def save_png_if_changed(im, path):
    """草稿逐像素不变即复用，避免无谓的 PNG 编码；不改正式目录。"""
    if path.exists():
        with Image.open(path) as existing:
            old = existing.convert('RGB')
        if old.size == im.size and ImageChops.difference(old, im.convert('RGB')).getbbox() is None:
            return False
    tmp = path.with_name(path.name + '.tmp')
    try:
        im.convert('RGB').save(tmp, format='PNG')
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)
    return True


def file_sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def ensure_draft_pdf(paths, pdf_path, previous):
    """页图和 PDF 自身哈希都一致才复用；先写临时文件再原子替换。"""
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode('utf-8'))
        digest.update(bytes.fromhex(file_sha256(path)))
    source = digest.hexdigest()
    if (pdf_path.exists() and previous.get('source') == source
            and previous.get('pdf') == file_sha256(pdf_path)):
        return {'source': source, 'pdf': previous['pdf']}, False
    tmp = pdf_path.with_name(pdf_path.name + '.tmp')
    try:
        save_lossless_pdf_from_paths(paths, tmp, resolution=150)
        tmp.replace(pdf_path)
    finally:
        tmp.unlink(missing_ok=True)
    return {'source': source, 'pdf': file_sha256(pdf_path)}, True


pages = []
reading_changed = 0

im = scene('cover.png')
d = ImageDraw.Draw(im)
cover_title(d, '休假回来的姐姐……')
speech(im, ['星野，这次长假，', '先陪我，好不好？'], (520, 220), (910, 465), 30)
d = ImageDraw.Draw(im)
d.text((60, 1780), '《二弟的休息日被全家预约了》 第一话', font=ft(25), fill=RED, stroke_width=2, stroke_fill=PAPER)
num(im)
reading_changed += save_png_if_changed(im, OUT/'page-00-cover.png')
pages.append(im)

im = scene('shot-01.png')
speech(im, ['项目搞定！', '从今天起，我是家里蹲。'], (390, 110), (735, 400), 30)
num(im, 1)
reading_changed += save_png_if_changed(im, OUT/'page-01.png')
pages.append(im)

im = scene('shot-02.png')
speech(im, ['这次我会多住一阵子，', '以前没时间陪你的，', '慢慢补回来。'],
       (255, 335), (510, 750), 28)
num(im, 2)
reading_changed += save_png_if_changed(im, OUT/'page-02.png')
pages.append(im)

im = scene('shot-03.png')
speech(im, ['我刚回来，', '今天先归我。'], (230, 180), (336, 480), 30)
speech(im, ['二哥，', '今天先陪我！'], (1120, 400), (1008, 704), 30)
num(im, 3)
reading_changed += save_png_if_changed(im, OUT/'page-03.png')
pages.append(im)

im = scene('shot-04.png')
speech(im, ['小满，', '连你也来抢呀？'], (1130, 200), (1176, 624), 28)
speech(im, ['小叔先陪我', '搭城堡啦。'], (200, 680), (368, 912), 28)
num(im, 4)
reading_changed += save_png_if_changed(im, OUT/'page-04.png')
pages.append(im)

# 第5/6页：2026-11-09 整话重绘并轨，正式图源改为新原画；中文全部由脚本精确绘制。
# 旧用户定稿文件与哈希只读归档（verify_user_final_archive），不再作为图源。
im = scene('shot-05.png')
schedule_card(im, (55, 45, 585, 535),
              ['1. 陪姐姐玩', '2. 陪妹妹玩', '3. 陪小满玩'],
              title_size=46, row_size=39, row_step=96, tilt=-3)
# 纸上笔迹单独按实际纸张透视排版，避免AI假字；此页的手位仍须放大复核。
perspective_schedule(im, '星野的日程表', ['1. 陪姐姐玩', '2. 陪妹妹玩', '3. 陪小满玩'],
                     ((660, 1195), (775, 1150), (880, 1225), (770, 1275)),
                     (360, 360), title_size=34, row_size=27, row_step=65,
                     title_y=8, start_y=70, margin=14)
speech(im, ['别抢啦，', '我把时间', '都排好了。'], (1270, 155), (1190, 520), 27)
num(im, 5)
reading_changed += save_png_if_changed(im, OUT/'page-05.png')
pages.append(im)

im = scene('shot-06.png')
schedule_card(im, (585, 270, 910, 700),
              ['1. 陪姐姐玩', '2. 陪妹妹玩', '3. 陪小满玩', '4. 睡觉休息'],
              title_size=29, row_size=25, row_step=68, margin=25)
# 母亲面向纸张，纸面补充项倒置于观看方向，完整可读的第四项也保留在上方日程卡。
perspective_schedule(im, '星野的日程表',
                     ['1. 陪姐姐玩', '2. 陪妹妹玩', '3. 陪小满玩', '4. 睡觉休息'],
                     ((825, 1285), (740, 1285), (740, 1230), (825, 1230)),
                     (300, 220), title_size=25, row_size=22, row_step=38,
                     title_y=5, start_y=42, margin=8)
speech(im, ['我也有自己的', '行程啊？'], (300, 150), (450, 420), 27)
speech(im, ['安排得挺好，', '不过得先把他', '休息的时间排上。'], (1080, 150), (1050, 520), 27)
num(im, 6)
reading_changed += save_png_if_changed(im, OUT/'page-06.png')
pages.append(im)

im = scene('shot-07.png')
caption(im, '妈妈转述', ['你哥哥跟你说，项目结束就好，', '早点休息，别熬夜。'], (55, 55), 27)
speech(im, ['小叔，等你休息好了，', '再陪我讲故事嘛。'], (300, 1510), (930, 1290), 27)
d = ImageDraw.Draw(im)
d.rounded_rectangle((50, 1795, 585, 1870), radius=18, fill=INK)
d.text((75, 1815), '二弟被预约的第一天，正式开始。', font=ft(22), fill=YELLOW)
num(im, 7)
reading_changed += save_png_if_changed(im, OUT/'page-07.png')
pages.append(im)

# 指定固定页序，不将旧草稿目录中额外的 PNG 意外打包。
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
    reading_paths, DRAFT/'chapter-01-draft-reading.pdf', previous.get('reading', {}))
cache['vertical'], vertical_pdf_changed = ensure_draft_pdf(
    vertical_paths, DRAFT/'chapter-01-draft-vertical.pdf', previous.get('vertical', {}))
cache_tmp = cache_path.with_name(cache_path.name + '.tmp')
try:
    cache_tmp.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')
    cache_tmp.replace(cache_path)
finally:
    cache_tmp.unlink(missing_ok=True)
print(f'UNAPPROVED DRAFT chapter 1: {len(pages)} pages; PNG changed: {reading_changed} reading / {vertical_changed} vertical; PDF rebuilt: {reading_pdf_changed} / {vertical_pdf_changed}')
