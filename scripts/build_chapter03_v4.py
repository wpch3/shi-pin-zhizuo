"""第三话构建入口：封面 + 11页正片 = 12页。

2026-11-08 第三次返修（v7 原画），按用户五张截图的意见：
1. 第4页哥哥"张掌像发誓"改为真实摸头（右手轻拍妹妹头顶）。
2. 第5页锁定台词由与第2页重复的"嗯，走吧。"改为用户裁定的"……嗯。别看了。"，
   哥哥同步画成耳根泛红、视线避开，表演与台词一致。
3. 第8页巴菲共食页用户指出 v7.0 仍有**三条手臂／三条袖管**（不是「看起来像」）：
   局部重绘 4 次均失败，最终按用户要求整张弃用、纯文本重新生成，改为四只手全部在
   桌面以上、桌下不画任何手／袖管，每人恰好 2 条袖管 2 只手、全画面两把长勺。
   详见 `docs/第三话_v7.1_纠错与新增铁律.md`，本段推翻此前「已修三只手」的写法。
4. 第7页拉袖的手真正捏住袖口；看板为图标化简笔，杯中两根斜插长柄餐具、不画勺碗，无字
   （v7.2 按 4 倍放大实图更正：既不是「直棍改勺头」，也不是「本来就有椭圆勺头」）。
5. 购物袋按场景状态机：第7、10页站立行走且哥哥有空手 → **哥哥右手实际提在手上**
   （shot-07／shot-10 已重新生成并删掉地面重复袋）；第5、6页静态试衣／坐下进食、
   双手被占用 → 落地；第8、9、11页坐下／进机／回家 → 画外。第2页软布托特包不是纸袋。
6. 保留巴菲共食，不回退双头吸管：第7页已补足"为什么两人共食一份"的前置动机。
7. 增量构建：源图＋脚本哈希短路；save_png 先像素比对，未变化页跳过 level-9 编码
   （实测 6.70s/页 → 0.104s/页）；派生 PDF／ZIP／轻量预览按输入哈希短路。

2026-11-08 第二次返修（v6 原画），按用户当轮意见扩到12页：
1. 试衣夸奖时序：旧版哥哥在妹妹只把开衫比在身前时就夸"很好看"，缺一个"穿上之后"的镜头。
   现在第3页只到"那你不许敷衍我"，新增第4页妹妹真的穿上开衫走出来，哥哥才说出锁定的夸奖句。
2. 一起喝 → 一起吃巴菲：新增第7页店内活动前置（巨型巴菲＋两人共食＝送限定挂件），
   给出"为什么要两人共食一份"的动机；第8页道具由饮料改为一份巨型圣代巴菲＋两把长勺，
   台词从描述道具（"两头吸管，正好一起喝。"）改为承载害羞情绪（"一人一半……你不许笑我。"）。
3. 大头照页问答顺序修正：必须是 妹"靠近一点，看镜头！"→哥"这样？"→妹"对，笑一下嘛。"
   上一轮把妹的第二句排在哥提问之前，属问答倒置，本轮按Z序重排。
4. 补齐上一轮额度用尽的遗留手部：第6页哥哥搭柜台的手、第10页女同学抬手，均已局部重绘。

沿用上一轮返修成果：原画四边铺满、scene() 用 ImageOps.fit 不贴纸底、页码按背景亮度反色描边、
气泡全部落在真实场景负空间。缺少已审查原画时明确失败，禁止占位图冒充正片。
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
SRC = ROOT / 'art/chapter-03-v7'
OUT = ROOT / 'deliverables/full-v4/chapter-03'
VERTICAL_OUT = ROOT / 'deliverables/full-v4-vertical/chapter-03'
FONT = ROOT / 'assets/fonts/NotoSansCJKsc-Bold.otf'
PAPER = '#F8F4EB'
INK = '#292B2C'
RED = '#92504C'
YELLOW = '#E9BD4F'
MUTED = '#746E67'
LAST = 11
REQUIRED = ['cover.png'] + [f'shot-{i:02d}.png' for i in range(1, LAST + 1)]


def ft(size):
    return ImageFont.truetype(str(FONT), size)


def scene(name):
    """四边铺满：只做0.4%画幅归一化裁切，绝不贴纸底、绝不保留生图自带纸边。"""
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
    value = 'COVER' if n is None else f'{n:02d} / {LAST}'
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


# ---- 增量构建 ---------------------------------------------------------------
# 实测（2026-11-08）：1440x1920 页 `optimize=True, compress_level=9` 编码 6.70s/页，
# 而 ImageChops.difference 像素比对仅 0.104s/页。旧流程每轮把 12 阅读页 + 12 竖屏页
# 全部重编码 = 24 * 6.70 ≈ 161s，正是 build 耗时 2m32s 的全部来源；脚本 PASS 与
# 未改动页的重新编码都属于多余工作。现在只有内容真的变化才落盘。
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


CACHE = ROOT / 'deliverables/.build-cache.json'
CACHE_KEY_FILES = [Path(__file__).resolve(), ROOT / 'scripts/pdf_export.py']


def _digest(paths):
    h = hashlib.sha256()
    for p in paths:
        h.update(str(p).encode())
        h.update(Path(p).read_bytes())
    return h.hexdigest()


CURRENT_SOURCE_DIGEST = _digest([SRC / n for n in REQUIRED] + CACHE_KEY_FILES)
PREVIOUS = json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}


def write_cache():
    CACHE.write_text(json.dumps({
        'source_digest': CURRENT_SOURCE_DIGEST,
        'written': BUILD_STATS['written'],
        'unchanged': BUILD_STATS['unchanged'],
    }, ensure_ascii=False, indent=2), encoding='utf-8')


missing = [name for name in REQUIRED if not (SRC / name).exists()]
if missing:
    raise FileNotFoundError('第三话尚缺已审查原画：' + ', '.join(missing))

# 全无变化时的极速短路：连 12 页绘制与 24 次像素比对都不做。
_EXPECTED_OUTPUTS = (
    [OUT / 'page-00-cover.png'] + [OUT / f'page-{i:02d}.png' for i in range(1, LAST + 1)]
    + [VERTICAL_OUT / 'page-00-cover.png']
    + [VERTICAL_OUT / f'page-{i:02d}.png' for i in range(1, LAST + 1)]
    + [ROOT / 'deliverables/第三话_妹妹的休息日.pdf',
       ROOT / 'deliverables/第三话_竖屏全页漫画.pdf']
)
if (PREVIOUS.get('source_digest') == CURRENT_SOURCE_DIGEST
        and all(p.exists() for p in _EXPECTED_OUTPUTS)):
    print('增量构建：源图与构建脚本哈希均未变化，12页成品与两份PDF全部复用，跳过全部重编码。')
    sys.exit(0)

OUT.mkdir(parents=True, exist_ok=True)
VERTICAL_OUT.mkdir(parents=True, exist_ok=True)
pages = []

# 封面：主角妹妹全身独立构图，双脚完整在画内；标题压在天空/雨棚实景区。
im = scene('cover.png')
d = ImageDraw.Draw(im)
d.text((38, 28), '说好今天陪我的呦', font=ft(66), fill=YELLOW, stroke_width=4, stroke_fill=INK)
d.text((60, 1780), '《二弟的休息日被全家预约了》 第三话', font=ft(25), fill=RED, stroke_width=2, stroke_fill=PAPER)
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

# 第3页：只到"不许敷衍我"。夸奖移到第4页，等妹妹真的穿上之后再夸。
im = scene('shot-03.png')
speech(im, ['这件怎么样？'], (300, 150), (480, 700), 28)
speech(im, ['你先试，我看看。'], (1080, 150), (970, 610), 28)
speech(im, ['那你不许敷衍我。'], (300, 390), (480, 700), 28)
num(im, 3)
save_png(im, OUT / 'page-03.png')
pages.append(im)

# 第4页（新增）：妹妹穿上开衫从试衣间出来，哥哥才给出锁定的真心夸奖。
im = scene('shot-04.png')
speech(im, ['换好了。'], (300, 230), (480, 690), 29)
speech(im, ['没敷衍。', '很好看，这颜色很衬你。'], (1080, 250), (960, 545), 28)
speech(im, ['……那我要这件。'], (300, 450), (480, 690), 28)
num(im, 4)
save_png(im, OUT / 'page-04.png')
pages.append(im)

# 第5页：哥哥正装试穿，妹妹被惊艳。正装只是试穿，后续外出服连续。
# 用户裁定：删掉与第2页重复、且没接住夸奖的"嗯，走吧。"，改"……嗯。别看了。"
# 画面同步给哥哥耳根泛红、视线转向镜子不看她，让台词有表演依据。
im = scene('shot-05.png')
speech(im, ['哇……二哥，', '你穿正装这么帅的吗？'], (330, 300), (420, 610), 29)
speech(im, ['……嗯。别看了。'], (1060, 240), (880, 440), 28)
num(im, 5)
save_png(im, OUT / 'page-05.png')
pages.append(im)

# 第6页：小吃摊。哥哥搭柜台的手已局部重绘修正。
im = scene('shot-06.png')
speech(im, ['这个好吃，你尝一口。'], (330, 190), (470, 830), 29, tail=80)
speech(im, ['嗯，不错。'], (1100, 200), (960, 730), 29)
speech(im, ['那再给我留一点。'], (330, 410), (470, 830), 28, tail=70)
num(im, 6)
save_png(im, OUT / 'page-06.png')
pages.append(im)

# 第7页（新增）：店内活动前置。看板只画图不写字：巨型巴菲＋两人＋箭头＋限定挂件。
im = scene('shot-07.png')
speech(im, ['两个人一起吃完，', '就送这个挂件！'], (330, 230), (720, 690), 29, tail=70)
speech(im, ['……所以你才拉我来。'], (1090, 200), (1060, 480), 28)
num(im, 7)
save_png(im, OUT / 'page-07.png')
pages.append(im)

# 第8页：一份巨型圣代巴菲＋两把长勺。台词承载害羞强撑，不再描述道具。
im = scene('shot-08.png')
speech(im, ['一人一半……', '你不许笑我。'], (300, 200), (470, 690), 29)
speech(im, ['……嗯，不笑。'], (1120, 190), (960, 620), 29)
num(im, 8)
save_png(im, OUT / 'page-08.png')
pages.append(im)

# 第9页：大头照。问答顺序 妹→哥→妹，按Z序：左上→右上→左下。
im = scene('shot-09.png')
speech(im, ['靠近一点，看镜头！'], (330, 190), (520, 700), 28)
speech(im, ['这样？'], (1180, 230), (1000, 620), 28)
speech(im, ['对，笑一下嘛。'], (330, 400), (520, 700), 28)
num(im, 9)
save_png(im, OUT / 'page-09.png')
pages.append(im)

# 第10页：女同学在左先问，妹妹在右答指定句；哥哥不接话。抬手已局部重绘修正。
im = scene('shot-10.png')
speech(im, ['小希，这位是？'], (300, 200), (400, 620), 29)
speech(im, ['这个是我男朋友。'], (830, 300), (830, 660), 30)
num(im, 10)
save_png(im, OUT / 'page-10.png')
pages.append(im)

# 第11页：姐姐带小满爬上床，哥哥掀被容纳。三泡纵向分层保证阅读顺序。
im = scene('shot-11.png')
speech(im, ['我才回来，', '位置就被你们占完了？'], (350, 190), (540, 660), 28)
speech(im, ['小叔，我也要！'], (1080, 330), (1030, 1110), 29, tail=110)
speech(im, ['走，小满，我们一起。'], (220, 900), (530, 670), 28)
num(im, 11)
save_png(im, OUT / 'page-11.png')
pages.append(im)

READING_PDF = ROOT / 'deliverables/第三话_妹妹的休息日.pdf'
VERTICAL_PDF = ROOT / 'deliverables/第三话_竖屏全页漫画.pdf'
# 阅读版落盘变化数，用来判断派生 PDF 是否需要重写（72MB 无谓重写同样属于多余工作）。
reading_written = BUILD_STATS['written']
# PDF 只由这些 PNG 的字节生成：像素全部未变时 PDF 必然相同，不因脚本注释/文档改动而
# 无谓重写 72MB。判定只依据「本轮是否真的落盘了新页」，不依据脚本哈希差异。
reading_changed = reading_written > 0
if reading_changed or not READING_PDF.exists():
    save_lossless_pdf_from_paths(sorted(OUT.glob('page-*.png')), READING_PDF, resolution=150)
vertical_pages = []
for source_path in sorted(OUT.glob('page-*.png')):
    source = Image.open(source_path).convert('RGB')
    assert source.size == (W, H), f'Unexpected page size: {source_path}: {source.size}'
    vertical = Image.new('RGB', VERTICAL_SIZE, PAPER)
    vertical.paste(source, (0, (VERTICAL_SIZE[1] - H) // 2))
    save_png(vertical, VERTICAL_OUT / source_path.name)
    vertical_pages.append(vertical)
vertical_changed = BUILD_STATS['written'] > reading_written or not VERTICAL_PDF.exists()
if vertical_changed or not VERTICAL_PDF.exists():
    save_lossless_pdf_from_paths(sorted(VERTICAL_OUT.glob('page-*.png')), VERTICAL_PDF, resolution=150)
write_cache()
print('Built chapter 03:', len(pages), 'pages (cover + 11 story pages)')
print(f'增量构建：新编码 {BUILD_STATS["written"]} 页，跳过未变化 {BUILD_STATS["unchanged"]} 页；'
      f'阅读PDF {"重写" if reading_changed else "复用"}，竖屏PDF {"重写" if vertical_changed else "复用"}')
