"""第四话《陪小满》构建入口：封面 + 9 页正片 = 10 页。

2026-11-08 依据 `docs/第四话_正式分镜与台词.md`：
- 兑现第一话结尾「小叔叔，饭后给我讲故事！」与第三话结尾「小叔，我也要！」。
- 主轴搭城堡 + 讲故事；细化塌塔重来、玩偶过家家、洗澡后五线索、讲三遍、
  脸颊晚安亲亲、大人哄睡式环抱、床头城堡回扣。
- 幼童场景边界：只画洗澡事后暗示（门缝水汽 / 小粉拖鞋 / 小黄鸭 / 换下裙子 /
  睡衣湿发 / 卷袖干毛巾），不画浴室内部与身体；亲亲是道谢式脸颊晚安亲亲，
  不画嘴唇相触；入睡是哄睡式环抱，被子盖到肩，不画亲密同床构图。
- 称呼：小满按人物关系叫「小叔／小叔叔」，用户所写「gege」指二哥本人。

画风铁律（AGENTS.md:21 / PROJECT_MEMORY.md:29 / 长期记录）：从零生成也必传
`art/chapter-03-v7/shot-01.png` 画风锚点；本话每次生图另传小满形象参考。
标题候选须用户裁定后再定稿，COVER_TITLE 为推荐值，改一行即可。

工程铁律（用户 2026-11-08「不做多余的事情」）：源图 + 脚本哈希短路；
save_png 先像素比对，未变化页跳过 level-9 编码；派生 PDF 只在真的落盘新页时重写。
源图尺寸强制 896x1200，防止 p7 那类 848x1264 混入后被 ImageOps.fit 悄悄裁掉内容。
"""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text
from pdf_export import save_lossless_pdf_from_paths

ROOT = Path(__file__).resolve().parents[1]
W, H = 1440, 1920
VERTICAL_SIZE = (1440, 2146)
SRC_SIZE = (896, 1200)
SRC = ROOT / 'art/chapter-04-v1'
OUT = ROOT / 'deliverables/full-v4/chapter-04'
VERTICAL_OUT = ROOT / 'deliverables/full-v4-vertical/chapter-04'
FONT = ROOT / 'assets/fonts/NotoSansCJKsc-Bold.otf'
PAPER = '#F8F4EB'
INK = '#292B2C'
RED = '#92504C'
YELLOW = '#E9BD4F'
LAST = 9
REQUIRED = ['cover.png'] + [f'shot-{i:02d}.png' for i in range(1, LAST + 1)]

# 2026-11-08 B 站视频页/搜索页调研后的新推荐（用户否掉了旧推荐「今晚轮到小满……」）。
# 用户裁定后只需改这一行，不需要动其余构建逻辑。
COVER_TITLE = '今晚小叔归我啦'
SERIES_LINE = '《二弟的休息日被全家预约了》 第四话'
# v7.2/v7.3 铁律：标题及「是否补封面台词气泡」必须用户裁定后才写入。
# 第三话最终未补封面气泡（新增台词需用户裁定），本话默认沿用「不补」；
# 用户裁定要补时把它改成 True，只重建封面页与派生交付。
COVER_TITLE_APPROVED = True  # 用户 2026-11-09 裁定：今晚小叔归我啦
# 用户若要补封面气泡，把它改 True 并在封面处取消注释那一行 speech(...)。
COVER_BUBBLE_APPROVED = False


def ft(size):
    return ImageFont.truetype(str(FONT), size)


def scene(name):
    """四边铺满：只做画幅归一化裁切，绝不贴纸底、绝不保留生图自带纸边。"""
    path = SRC / name
    if not path.exists():
        raise FileNotFoundError(f'缺少已审查的第四话原画：{path}；不得用占位图或立绘替代。')
    source = Image.open(path).convert('RGB')
    if source.size != SRC_SIZE:
        raise ValueError(
            f'{path.name} 源画尺寸 {source.size} != {SRC_SIZE}；'
            '必须整张带锚点重新生成，禁止靠 ImageOps.fit 悄悄裁切或局部拉伸。')
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
    """页码：按所在背景亮度自动取反色并加同底描边。"""
    d = ImageDraw.Draw(im)
    value = 'COVER' if n is None else f'{n:02d} / {LAST}'
    pos = (1250, 1855)
    f = ft(18)
    box = d.textbbox(pos, value, font=f)
    pad = 6
    region = np.asarray(im.crop((max(0, box[0] - pad), max(0, box[1] - pad),
                                 min(W, box[2] + pad), min(H, box[3] + pad)))).mean()
    fill, stroke = (PAPER, INK) if region < 150 else (INK, PAPER)
    d.text(pos, value, font=f, fill=fill, stroke_width=2, stroke_fill=stroke)


# ---- 增量构建 ---------------------------------------------------------------
BUILD_STATS = {'written': 0, 'unchanged': 0}


def save_png(im, path):
    """像素未变则跳过昂贵的 level-9 PNG 编码；返回是否落盘。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        try:
            old = Image.open(path).convert('RGB')
            if old.size == im.size and ImageChops.difference(old, im.convert('RGB')).getbbox() is None:
                BUILD_STATS['unchanged'] += 1
                return False
        except (OSError, ValueError):
            pass
    im.save(path, optimize=True, compress_level=9)
    BUILD_STATS['written'] += 1
    return True


CACHE = ROOT / 'deliverables/.chapter04-build-cache.json'
CACHE_KEY_FILES = [Path(__file__).resolve(), ROOT / 'scripts/pdf_export.py']
READING_PDF = ROOT / 'deliverables/第四话_陪小满.pdf'
VERTICAL_PDF = ROOT / 'deliverables/第四话_竖屏全页漫画.pdf'


def _digest(paths):
    h = hashlib.sha256()
    for p in paths:
        h.update(str(p).encode())
        h.update(Path(p).read_bytes())
    h.update(COVER_TITLE.encode())
    h.update(SERIES_LINE.encode())
    return h.hexdigest()


missing = [name for name in REQUIRED if not (SRC / name).exists()]
if missing:
    raise FileNotFoundError('第四话尚缺已审查原画：' + ', '.join(missing))

CURRENT_SOURCE_DIGEST = _digest([SRC / n for n in REQUIRED] + CACHE_KEY_FILES)
PREVIOUS = json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}


def write_cache():
    CACHE.write_text(json.dumps({
        'source_digest': CURRENT_SOURCE_DIGEST,
        'written': BUILD_STATS['written'],
        'unchanged': BUILD_STATS['unchanged'],
    }, ensure_ascii=False, indent=2), encoding='utf-8')


_EXPECTED_OUTPUTS = (
    [OUT / 'page-00-cover.png'] + [OUT / f'page-{i:02d}.png' for i in range(1, LAST + 1)]
    + [VERTICAL_OUT / 'page-00-cover.png']
    + [VERTICAL_OUT / f'page-{i:02d}.png' for i in range(1, LAST + 1)]
    + [READING_PDF, VERTICAL_PDF]
)
if (PREVIOUS.get('source_digest') == CURRENT_SOURCE_DIGEST
        and all(p.exists() for p in _EXPECTED_OUTPUTS)):
    print('增量构建：源图与构建脚本哈希均未变化，10页成品与两份PDF全部复用，跳过全部重编码。')
    sys.exit(0)

OUT.mkdir(parents=True, exist_ok=True)
VERTICAL_OUT.mkdir(parents=True, exist_ok=True)
pages = []

# 封面：小满抱积木桶＋绘本站在小叔房门口，双脚完整在画内；标题压在左上暖色留白。
if not COVER_TITLE_APPROVED:
    raise SystemExit('封面标题尚未由用户裁定：请在文档第五节四选一或另给一句，'
                     '然后设置 COVER_TITLE 与 COVER_TITLE_APPROVED=True 再构建；'
                     '禁止把推荐值当成已定稿自动生成。')
im = scene('cover.png')
d = ImageDraw.Draw(im)
d.text((38, 28), COVER_TITLE, font=ft(66), fill=YELLOW, stroke_width=4, stroke_fill=INK)
d.text((60, 1780), SERIES_LINE, font=ft(25), fill=RED, stroke_width=2, stroke_fill=PAPER)
# 封面台词气泡暂不写入：默认沿用第三话 v7.3 定稿「不补」。
# 用户裁定要补时，在此加回一行
#   speech(im, ['小叔叔，今天轮到我啦！'], (350, 250), (420, 900), 29, tail=80)
# 并把 COVER_BUBBLE_APPROVED 改 True；静态气泡审计会对它一并复检。
num(im)
save_png(im, OUT / 'page-00-cover.png')
pages.append(im)

# 第1页：兑现第一话伏笔，小叔合上电脑。
im = scene('shot-01.png')
speech(im, ['小叔，说好的故事！'], (330, 200), (450, 900), 29, tail=70)
speech(im, ['……记得，先搭城堡。'], (1080, 250), (980, 640), 28)
num(im, 1)
save_png(im, OUT / 'page-01.png')
pages.append(im)

# 第2页：一起搭城堡，小满双手递积木，小叔搭底座。
im = scene('shot-02.png')
speech(im, ['这里要最高的塔！'], (330, 190), (460, 900), 29, tail=70)
speech(im, ['行，你扶着。'], (1100, 210), (1000, 640), 29)
num(im, 2)
save_png(im, OUT / 'page-02.png')
pages.append(im)

# 第3页：塌了一角，小满鼓腮护短，小叔用硬壳绘本垫平地基。
im = scene('shot-03.png')
speech(im, ['……它自己倒的。'], (300, 180), (440, 900), 28, tail=70)
speech(im, ['地基没放平。', '再来一次。'], (1090, 210), (990, 640), 28)
num(im, 3)
save_png(im, OUT / 'page-03.png')
pages.append(im)

# 第4页：城堡完成＋玩偶过家家，窗外天色转暗。
im = scene('shot-04.png')
speech(im, ['骑士要住最高的房间！'], (300, 180), (420, 860), 28, tail=70)
speech(im, ['那这一层归他。'], (1100, 210), (1010, 640), 29)
num(im, 4)
save_png(im, OUT / 'page-04.png')
pages.append(im)

# 第5页：洗澡后五线索暗示页（画面外部处理，不画浴室内部）。
im = scene('shot-05.png')
# 用户指定：小满主动提出一起睡，给第9页「抱着一起睡」前置动机，不凭空发生。
speech(im, ['洗香香啦！', '今晚我想跟小叔一起睡。'], (320, 210), (470, 1000), 27, tail=90)
speech(im, ['……嗯。先讲故事。'], (1090, 220), (980, 600), 28)
num(im, 5)
save_png(im, OUT / 'page-05.png')
pages.append(im)

# 第6页：睡前故事（一）。小满在右侧被子里，用长尾保持左上→右下的阅读顺序。
im = scene('shot-06.png')
speech(im, ['这里！', '小熊找到家了吗？'], (330, 190), (900, 1020), 28, tail=130)
speech(im, ['找到了，别急。'], (1110, 220), (700, 660), 28, tail=100)
num(im, 6)
save_png(im, OUT / 'page-06.png')
pages.append(im)

# 第7页：讲三遍，小满揉眼强撑，小叔轻轻合书。
im = scene('shot-07.png')
speech(im, ['再讲一遍嘛……'], (320, 190), (930, 900), 29, tail=120)
speech(im, ['第三遍了。', '说好最后一遍。'], (1100, 230), (680, 640), 28, tail=100)
num(im, 7)
save_png(im, OUT / 'page-07.png')
pages.append(im)

# 第8页：晚安亲亲（脸颊、道谢式，小叔愣住后无奈笑）。
im = scene('shot-08.png')
# 用户指定：亲的时候说「小满最喜欢小叔了」。
speech(im, ['小满最喜欢小叔了！'], (300, 180), (620, 900), 28, tail=80)
speech(im, ['……嗯，晚安。'], (1110, 220), (900, 620), 28)
num(im, 8)
save_png(im, OUT / 'page-08.png')
pages.append(im)

# 第9页：被小叔抱着一起睡。无台词，安静收尾。
im = scene('shot-09.png')
num(im, 9)
save_png(im, OUT / 'page-09.png')
pages.append(im)

reading_written = BUILD_STATS['written']
reading_changed = reading_written > 0
if reading_changed or not READING_PDF.exists():
    save_lossless_pdf_from_paths(sorted(OUT.glob('page-*.png')), READING_PDF, resolution=150)
for source_path in sorted(OUT.glob('page-*.png')):
    source = Image.open(source_path).convert('RGB')
    assert source.size == (W, H), f'Unexpected page size: {source_path}: {source.size}'
    vertical = Image.new('RGB', VERTICAL_SIZE, PAPER)
    vertical.paste(source, (0, (VERTICAL_SIZE[1] - H) // 2))
    save_png(vertical, VERTICAL_OUT / source_path.name)
vertical_changed = BUILD_STATS['written'] > reading_written or not VERTICAL_PDF.exists()
if vertical_changed or not VERTICAL_PDF.exists():
    save_lossless_pdf_from_paths(sorted(VERTICAL_OUT.glob('page-*.png')), VERTICAL_PDF, resolution=150)
write_cache()
print('Built chapter 04:', len(pages), 'pages (cover + 9 story pages)')
print(f'增量构建：新编码 {BUILD_STATS["written"]} 页，跳过未变化 {BUILD_STATS["unchanged"]} 页；'
      f'阅读PDF {"重写" if reading_changed else "复用"}，竖屏PDF {"重写" if vertical_changed else "复用"}')
