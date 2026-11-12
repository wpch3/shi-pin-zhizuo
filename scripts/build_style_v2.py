from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables/style-v2"
OUT.mkdir(parents=True, exist_ok=True)
FONT = ROOT / "assets/fonts/NotoSansCJKsc-Bold.otf"
W, H = 1440, 1920
YELLOW = "#FFD832"
INK = "#151114"
RED = "#A62838"


def ft(size):
    return ImageFont.truetype(str(FONT), size)


def lines_for(draw, text, font, width):
    lines, line = [], ""
    for ch in text:
        trial = line + ch
        if draw.textbbox((0, 0), trial, font=font)[2] > width and line:
            lines.append(line)
            line = ch
        else:
            line = trial
    if line:
        lines.append(line)
    return lines


def title(draw, text, size=76, y=35):
    draw.text((45, y), text, font=ft(size), fill=YELLOW, stroke_width=7, stroke_fill=INK)


def bubble(im, speaker, text, box, dark=False, size=40):
    d = ImageDraw.Draw(im)
    x, y, w, h = box
    fill = INK if dark else "#FFFFFF"
    body = "#FFFFFF" if dark else INK
    outline = RED if dark else INK
    d.rounded_rectangle((x, y, x+w, y+h), radius=36, fill=fill, outline=outline, width=5)
    d.polygon(((x+70, y+h-3), (x+112, y+h-3), (x+82, y+h+35)), fill=fill)
    d.line((x+70, y+h, x+82, y+h+35, x+112, y+h), fill=outline, width=5)
    d.text((x+28, y+18), speaker, font=ft(25), fill=YELLOW if dark else RED)
    fnt = ft(size)
    lines = lines_for(d, text, fnt, w-56)
    ty = y+65
    for line in lines:
        d.text((x+28, ty), line, font=fnt, fill=body)
        ty += size+14


def scene(filename):
    return Image.open(ROOT / "art/vertical-v2" / filename).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)


pages = []

im = scene("01-sister-cover.png")
d = ImageDraw.Draw(im)
title(d, "休假回来的姐姐……", size=82, y=35)
bubble(im, "江望舒", "星野，这次长假，先陪我。", (45, 410, 610, 235), dark=True, size=39)
pages.append(im)

im = scene("02-sister-lean.png")
d = ImageDraw.Draw(im)
title(d, "姐姐休假回来，第一件事——", size=67, y=30)
bubble(im, "江望舒", "这次我会待很久，先把以前少陪你的时间补回来。", (45, 175, 1010, 285), size=43)
pages.append(im)

im = scene("03-sisters-compete.png")
d = ImageDraw.Draw(im)
title(d, "刚回家，就开始抢人……", size=72, y=25)
bubble(im, "江辰希", "二哥，今天先陪我！", (35, 150, 480, 205), size=37)
bubble(im, "江望舒", "我刚回来，今天先归我。", (930, 150, 475, 245), size=36)
pages.append(im)

for i, page in enumerate(pages, 1):
    d = ImageDraw.Draw(im) if False else ImageDraw.Draw(page)
    d.text((1280, 1860), f"{i:02d} / 03", font=ft(21), fill="#7B7370")
    page.save(OUT / f"page-{i:02d}.png")
pages[0].save(ROOT / "deliverables/历史资料/样张与提案/三页风格样张_V2.pdf", save_all=True, append_images=pages[1:], resolution=150)


def trim_white(im):
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    mask = np.min(a, axis=2) < 238
    rows = np.flatnonzero(mask.sum(axis=1) > 8)
    cols = np.flatnonzero(mask.sum(axis=0) > 8)
    if len(rows) and len(cols):
        return im.crop((int(cols[0]), int(rows[0]), int(cols[-1])+1, int(rows[-1])+1))
    return im


cards = []
for i, (fid, name, role) in enumerate([
    ("older-sister", "江望舒", "姐姐｜博士学位 · 职场精英 · 回家就犯懒"),
    ("younger-sister", "江辰希", "妹妹｜优等生 · 对外从容 · 见二哥就撒娇"),
    ("second-brother", "江星野", "二弟｜自信帅气 · 作息不规律 · 认真可靠"),
], 1):
    card = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(card)
    d.text((55, 45), name, font=ft(74), fill=INK)
    d.text((60, 150), role, font=ft(28), fill=RED)
    d.line((55, 215, 1385, 215), fill=INK, width=4)
    src = trim_white(Image.open(ROOT / "art/character-v2" / f"{fid}.png").convert("RGB"))
    scale = min(1240/src.width, 1450/src.height)
    src = src.resize((round(src.width*scale), round(src.height*scale)), Image.Resampling.LANCZOS)
    card.paste(src, ((W-src.width)//2, 250+(1450-src.height)//2))
    d.text((60, 1790), "角色标准图 V2｜高对比线条 · 明确表情 · 统一肤色阴影", font=ft(25), fill="#6C6360")
    d.text((1260, 1840), f"{i:02d} / 03", font=ft(21), fill="#7B7370")
    card.save(OUT / f"standard-{i:02d}-{fid}.png")
    cards.append(card)
cards[0].save(ROOT / "deliverables/核心角色标准图_V2.pdf", save_all=True, append_images=cards[1:], resolution=150)
print("Built 3 style pages and 3 character standards at 1440x1920")
