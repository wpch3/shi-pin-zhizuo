from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables" / "人物资料/历史图源/visual-review"
OUT.mkdir(parents=True, exist_ok=True)
FONT = ROOT / "assets" / "fonts" / "NotoSansCJKsc-Regular.otf"
W, H = 1800, 2400
BG = "#F8F5EF"
INK = "#403C39"
MUTED = "#81786F"
ACCENT = "#A77C80"
PAGES = []


def font(size):
    return ImageFont.truetype(str(FONT), size)


def page(title, subtitle=""):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((100, 82), title, fill=INK, font=font(64))
    if subtitle:
        d.text((102, 174), subtitle, fill=MUTED, font=font(28))
    d.line((100, 238, 1700, 238), fill="#D8CEC4", width=2)
    return im, d


def contain(im, path, box):
    src = Image.open(path).convert("RGB")
    x, y, w, h = box
    scale = min(w / src.width, h / src.height)
    nw, nh = round(src.width * scale), round(src.height * scale)
    src = src.resize((nw, nh), Image.Resampling.LANCZOS)
    im.paste(src, (x + (w - nw) // 2, y + (h - nh) // 2))


def cover(im, path, box):
    src = Image.open(path).convert("RGB")
    x, y, w, h = box
    scale = max(w / src.width, h / src.height)
    nw, nh = round(src.width * scale), round(src.height * scale)
    src = src.resize((nw, nh), Image.Resampling.LANCZOS)
    left, top = (nw - w) // 2, (nh - h) // 2
    src = src.crop((left, top, left + w, top + h))
    im.paste(src, (x, y))


def wrap(draw, text, xy, max_width, fnt, fill=INK, line_gap=18):
    x, y = xy
    line = ""
    for ch in text:
        trial = line + ch
        if draw.textbbox((0, 0), trial, font=fnt)[2] > max_width and line:
            draw.text((x, y), line, fill=fill, font=fnt)
            y += fnt.size + line_gap
            line = ch
        else:
            line = trial
    if line:
        draw.text((x, y), line, fill=fill, font=fnt)
        y += fnt.size + line_gap
    return y


def save(im, filename):
    path = OUT / filename
    im.save(path)
    PAGES.append(im)


# 1. Selected normal-proportion niece
im, d = page("小满｜小侄女", "已选正比形象 · 原有人设与彩虹裙视觉锚点保留")
contain(im, ROOT / "art/characters/niece-beautified.png", (80, 280, 1640, 1740))
d.text((100, 2110), "精致五官、通透栗色眼睛、分层短发与自然提裙动作。", fill=INK, font=font(32))
d.text((100, 2170), "不再使用此前被否决的普通儿童插画形象。", fill=MUTED, font=font(28))
save(im, "01_小侄女_正比.png")

# 2. Selected chibi niece
im, d = page("小满｜Q版", "已选Q版形象 · 用动作和表情放大黏小叔叔的娇憨感")
contain(im, ROOT / "art/chibi/niece-final.png", (80, 280, 1640, 1740))
d.text((100, 2110), "头身压缩，但保留栗色眼睛、空气刘海和彩虹裙。", fill=INK, font=font(32))
d.text((100, 2170), "Q版只负责情绪反差，不改小侄女的身份、关系或戏份。", fill=MUTED, font=font(28))
save(im, "02_小侄女_Q版.png")

# 3. Normal vs Q comparison
im, d = page("正比与Q版｜撒娇反差样张", "同类家庭互动使用两种视觉层次")
d.text((100, 290), "正比：现实动作、身体接触与生活细节", fill=INK, font=font(36))
cover(im, ROOT / "art/style-samples/natural-family-spoiling.png", (100, 365, 1600, 820))
d.text((100, 1260), "Q版：压缩头身，集中表现依赖与二哥的无奈", fill=INK, font=font(36))
cover(im, ROOT / "art/style-samples/q-family-final.png", (100, 1335, 1600, 820))
save(im, "03_正比与Q版反差.png")

# 4. Naming and anti-AI drawing rules
im, d = page("命名与画风执行方案", "本页是命名提案；在确认前不回写故事正文")
d.text((100, 305), "作品名", fill=ACCENT, font=font(30))
d.text((100, 360), "《星辰落进灯火里》", fill=INK, font=font(54))
d.text((100, 475), "角色命名", fill=ACCENT, font=font(30))
names = [
    ("父亲", "江怀川"), ("母亲", "沈静宜"), ("大哥", "江昭远"),
    ("姐姐", "江望舒"), ("二哥", "江星野"), ("妹妹", "江辰希"),
    ("小侄女", "小满（乳名）"),
]
y = 540
for role, name in names:
    d.text((110, y), role, fill=MUTED, font=font(32))
    d.text((390, y - 5), name, fill=INK, font=font(40))
    y += 82
d.line((100, 1140, 1700, 1140), fill="#D8CEC4", width=2)
d.text((100, 1200), "降低AI画风的固定规则", fill=ACCENT, font=font(30))
rules = [
    "线条：保留粗细变化、局部断线、衣褶速写线和少量排线，不做塑料般光滑的描边。",
    "五官：避免所有角色共用同一种大眼、同一弧度的微笑；用眉眼高低、视线和嘴角差异区分情绪。",
    "构图：减少正面排排站，采用侧视角、遮挡、远近层次和不完全对称的身体接触。",
    "生活痕迹：用滑落的鞋、半杯茶、压皱的毯子、便签和翻旧的书页替代无意义光斑。",
    "色彩：低饱和平涂加轻微纸张颗粒，不使用泛滥的粉色辉光、过曝逆光与装饰性闪点。",
    "一致性：正比场景连续复用已确认角色锚点；Q版只在撒娇、争位和二哥无奈等情绪镜头出现。",
]
y = 1270
for i, rule in enumerate(rules, 1):
    d.text((105, y), f"{i:02d}", fill=ACCENT, font=font(28))
    y = wrap(d, rule, (175, y), 1500, font(30), line_gap=14) + 24
save(im, "04_命名与画风规则.png")

pdf_path = ROOT / "deliverables" / "历史资料/样张与提案/视觉与命名提案.pdf"
PAGES[0].save(pdf_path, save_all=True, append_images=PAGES[1:], resolution=150)
print(pdf_path)
