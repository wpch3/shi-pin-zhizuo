import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data/characters.json").read_text(encoding="utf-8"))
FONT = ROOT / "assets/fonts/NotoSansCJKsc-Regular.otf"
W, H = 1440, 2560
OUT_COMIC = ROOT / "deliverables/vertical-chapter-01"
OUT_CARDS = ROOT / "deliverables/complete-character-sheets"
OUT_COMIC.mkdir(parents=True, exist_ok=True)
OUT_CARDS.mkdir(parents=True, exist_ok=True)
BG = "#F8F5EF"
INK = "#383533"
MUTED = "#7C746D"


def ft(size):
    return ImageFont.truetype(str(FONT), size)


def fit(im, size):
    return im.resize(size, Image.Resampling.LANCZOS)


def wrap_lines(draw, text, fnt, width):
    lines, line = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(line)
            line = ""
            continue
        trial = line + ch
        if draw.textbbox((0, 0), trial, font=fnt)[2] > width and line:
            lines.append(line)
            line = ch
        else:
            line = trial
    if line:
        lines.append(line)
    return lines


def text_block(draw, text, box, size=44, fill=INK, spacing=16, align="left"):
    x, y, w, h = box
    fnt = ft(size)
    lines = wrap_lines(draw, text, fnt, w)
    for line in lines:
        lw = draw.textbbox((0, 0), line, font=fnt)[2]
        tx = x if align == "left" else x + (w - lw) / 2
        draw.text((tx, y), line, fill=fill, font=fnt)
        y += size + spacing
    return y


def bubble(im, speaker, text, box, accent="#786B62", tail="bottom"):
    d = ImageDraw.Draw(im)
    x, y, w, _ = box
    name_f, body_f = ft(27), ft(43)
    lines = wrap_lines(d, text, body_f, w - 72)
    h = 62 + len(lines) * 61 + 34
    d.rounded_rectangle((x, y, x + w, y + h), radius=38, fill="#FFFEFB", outline=accent, width=4)
    if tail == "bottom":
        d.polygon(((x + 105, y + h - 3), (x + 150, y + h - 3), (x + 116, y + h + 42)), fill="#FFFEFB")
        d.line((x + 105, y + h, x + 116, y + h + 42, x + 150, y + h), fill=accent, width=4)
    d.text((x + 36, y + 22), speaker, fill=accent, font=name_f)
    ty = y + 72
    for line in lines:
        d.text((x + 36, ty), line, fill=INK, font=body_f)
        ty += 61
    return y + h


def scene_page(index):
    src = Image.open(ROOT / f"art/vertical-chapter-01/shot-{index:02d}.png").convert("RGB")
    im = fit(src, (W, H))
    d = ImageDraw.Draw(im)
    if index == 1:
        d.rounded_rectangle((60, 55, 1380, 360), radius=42, fill="#FFFDF8E8")
        d.text((100, 82), "第一话", fill="#8A6C64", font=ft(34))
        text_block(d, "我姐休假回来，直接把我预约了", (100, 140, 1240, 190), size=66, spacing=12)
        bubble(im, "江星野", "项目搞定！从今天起，我是家里蹲。", (90, 440, 1130, 0), "#72806B")
    elif index == 2:
        bubble(im, "江望舒", "这次我会待很久，先把以前少陪你的时间补回来。", (90, 180, 1200, 0), "#8A6C64")
    elif index == 3:
        bubble(im, "江辰希", "二哥，今天先陪我！", (70, 90, 780, 0), "#8C697A")
        bubble(im, "江望舒", "我刚回来，今天先归我。", (550, 440, 810, 0), "#8A6C64")
    elif index == 4:
        # Remove the source image's empty speech balloon before typesetting.
        d.rectangle((0, 0, W, 640), fill="#FAF8F2")
        bubble(im, "小满", "小叔先陪我搭城堡！", (180, 160, 1080, 0), "#B07D78")
    elif index == 5:
        bubble(im, "江星野", "别抢，我把时间都排好了。", (120, 170, 1160, 0), "#72806B")
        d.rounded_rectangle((110, 480, 770, 650), radius=30, fill="#FFFDF8E8")
        d.text((150, 505), "姐姐　妹妹　小满", fill=INK, font=ft(45))
        d.text((150, 575), "一个一个来，都有时间。", fill=MUTED, font=ft(30))
    elif index == 6:
        d.rounded_rectangle((65, 55, 1375, 795), radius=42, fill="#FFFEFB", outline="#A48867", width=4)
        d.text((110, 90), "江星野的日程表", fill="#72806B", font=ft(44))
        rows = [("陪姐姐散步", INK), ("陪妹妹挑书", INK), ("陪小满搭城堡、讲三遍故事", INK), ("二弟睡觉", "#A55F5F")]
        y = 180
        for i, (txt, color) in enumerate(rows):
            d.text((125, y), f"{i + 1:02d}", fill="#A48867", font=ft(31))
            d.text((230, y - 7), txt, fill=color, font=ft(43 if i != 2 else 39))
            y += 112
        d.text((1030, 710), "——妈妈补上", fill="#A55F5F", font=ft(28))
        bubble(im, "沈静宜", "安排得很好，先把他的休息排上。", (65, 855, 940, 0), "#A48867")
        bubble(im, "江星野", "我也有自己的行程啊？", (510, 1130, 850, 0), "#72806B")
    elif index == 7:
        d.rounded_rectangle((75, 70, 1365, 270), radius=38, fill="#EFF3F0", outline="#72806B", width=3)
        d.text((115, 100), "江昭远", fill="#526D91", font=ft(30))
        d.text((115, 157), "老二，项目结束就好，别熬夜。", fill=INK, font=ft(39))
        bubble(im, "小满", "小叔休息好，就陪我讲故事！", (105, 355, 1190, 0), "#B07D78")
        d.rounded_rectangle((95, 2190, 1345, 2395), radius=45, fill="#FFFDF8ED")
        d.text((145, 2230), "二弟被预约的第一天，正式开始。", fill=INK, font=ft(48))
        d.text((145, 2310), "《星辰落进灯火里》· 第一话 完", fill=MUTED, font=ft(28))
    d = ImageDraw.Draw(im)
    d.text((1240, 2480), f"{index:02d} / 07", fill="#6F6862", font=ft(24))
    return im


def portrait_crop(path):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    corners = np.concatenate((a[:20, :20].reshape(-1, 3), a[:20, -20:].reshape(-1, 3), a[-20:, :20].reshape(-1, 3), a[-20:, -20:].reshape(-1, 3)))
    bg = np.median(corners, axis=0)
    diff = np.max(np.abs(a - bg), axis=2)
    mask = diff > 22
    rows = (mask.sum(axis=1) > max(8, im.width * 0.008))
    cols = (mask.sum(axis=0) > max(8, im.height * 0.008))
    ys, xs = np.where(rows)[0], np.where(cols)[0]
    if len(xs) and len(ys):
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        pad_x, pad_y = int((x1 - x0) * 0.12), int((y1 - y0) * 0.06)
        x0, x1 = max(0, x0 - pad_x), min(im.width, x1 + pad_x)
        y0, y1 = max(0, y0 - pad_y), min(im.height, y1 + pad_y)
        im = im.crop((x0, y0, x1, y1))
    return im


def character_card(c, index):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    accent = c["accent"]
    d.rectangle((0, 0, 24, H), fill=accent)
    d.text((90, 80), c["role"], fill=accent, font=ft(36))
    d.text((85, 145), c["name"], fill=INK, font=ft(86))
    d.text((90, 275), "《星辰落进灯火里》角色设定", fill=MUTED, font=ft(28))
    d.line((90, 340, 1350, 340), fill=accent, width=3)
    d.rounded_rectangle((70, 390, 1370, 1390), radius=45, fill="#F1ECE5")
    portrait = portrait_crop(ROOT / "art/characters" / c["file"])
    max_w, max_h = 1170, 940
    scale = min(max_w / portrait.width, max_h / portrait.height)
    portrait = portrait.resize((round(portrait.width * scale), round(portrait.height * scale)), Image.Resampling.LANCZOS)
    im.paste(portrait, ((W - portrait.width) // 2, 420 + (940 - portrait.height) // 2))
    d = ImageDraw.Draw(im)
    d.text((90, 1460), "人物介绍", fill=accent, font=ft(34))
    y = 1535
    for item in c["settings"]:
        d.ellipse((95, y + 17, 107, y + 29), fill=accent)
        y = text_block(d, item, (130, y, 1180, 0), size=31, spacing=12) + 24
    d.line((90, 2390, 1350, 2390), fill="#D8CEC4", width=2)
    d.text((90, 2430), c["visual"], fill=MUTED, font=ft(26))
    d.text((1250, 2480), f"{index:02d} / 08", fill=MUTED, font=ft(24))
    return im


def family_card():
    src = Image.open(ROOT / "art/family/group-portrait.png").convert("RGB")
    im = fit(src, (W, H))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((55, 45, 1385, 275), radius=40, fill="#FFFDF8ED")
    d.text((95, 70), "星辰落进灯火里", fill=INK, font=ft(66))
    d.text((100, 175), "全员合照｜江怀川 · 沈静宜 · 江昭远 · 江望舒 · 江星野 · 江辰希 · 小满", fill=MUTED, font=ft(25))
    d.rounded_rectangle((250, 2350, 1190, 2465), radius=35, fill="#FFFDF8ED")
    d.text((310, 2380), "灯火亮着的时候，家人就在这里。", fill=INK, font=ft(35))
    return im


comic_pages = []
for i in range(1, 8):
    page = scene_page(i)
    page.save(OUT_COMIC / f"page-{i:02d}.png")
    comic_pages.append(page)
comic_pages[0].save(ROOT / "deliverables/第一话_竖屏全页漫画.pdf", save_all=True, append_images=comic_pages[1:], resolution=150)

card_pages = []
for i, c in enumerate(DATA["characters"], 1):
    page = character_card(c, i)
    page.save(OUT_CARDS / f"{i:02d}-{c['id']}.png")
    card_pages.append(page)
family = family_card()
family.save(OUT_CARDS / "08-family.png")
card_pages.append(family)
card_pages[0].save(ROOT / "deliverables/完整人设与合照.pdf", save_all=True, append_images=card_pages[1:], resolution=150)
print("Built", len(comic_pages), "comic pages and", len(card_pages), "character/family pages")
