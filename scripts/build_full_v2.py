import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data/characters.json").read_text(encoding="utf-8"))
FONT = ROOT / "assets/fonts/NotoSansCJKsc-Bold.otf"
W, H = 1440, 1920
OUT = ROOT / "deliverables/full-v2"
COUT, OOUT = OUT / "characters", OUT / "chapter-01"
COUT.mkdir(parents=True, exist_ok=True)
OOUT.mkdir(parents=True, exist_ok=True)
INK = "#151114"
RED = "#A62838"
YELLOW = "#FFD832"


def ft(n): return ImageFont.truetype(str(FONT), n)


def lines(d, text, f, width):
    out, line = [], ""
    for ch in text:
        if ch == "\n":
            out.append(line); line = ""; continue
        t = line + ch
        if d.textbbox((0, 0), t, font=f)[2] > width and line:
            out.append(line); line = ch
        else: line = t
    if line: out.append(line)
    return out


def text(d, text, xy, width, size=32, fill=INK, gap=12):
    x, y = xy; f = ft(size)
    for line in lines(d, text, f, width):
        d.text((x, y), line, font=f, fill=fill)
        y += size + gap
    return y


def title(d, s, size=70):
    d.text((42, 30), s, font=ft(size), fill=YELLOW, stroke_width=7, stroke_fill=INK)


def bubble(im, speaker, s, box, size=39, dark=False):
    d = ImageDraw.Draw(im); x, y, w, h = box
    fill = INK if dark else "white"; body = "white" if dark else INK
    d.rounded_rectangle((x, y, x+w, y+h), radius=34, fill=fill, outline=RED if dark else INK, width=5)
    d.polygon(((x+65, y+h-3), (x+110, y+h-3), (x+78, y+h+32)), fill=fill)
    d.text((x+26, y+17), speaker, font=ft(24), fill=YELLOW if dark else RED)
    yy = y+62
    for line in lines(d, s, ft(size), w-52):
        d.text((x+26, yy), line, font=ft(size), fill=body); yy += size+13


def trim(im):
    a = np.asarray(im.convert("RGB"))
    mask = np.min(a, axis=2) < 240
    rows = np.flatnonzero(mask.sum(axis=1) > 8); cols = np.flatnonzero(mask.sum(axis=0) > 8)
    if len(rows) and len(cols): return im.crop((int(cols[0]), int(rows[0]), int(cols[-1])+1, int(rows[-1])+1))
    return im


def scene(path):
    return Image.open(path).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)


def cutout(fid):
    im = Image.open(ROOT / "art/character-v2" / f"{fid}.png").convert("RGBA")
    seeds = [(0,0),(im.width-1,0),(0,im.height-1),(im.width-1,im.height-1),
             (im.width//2,0),(0,im.height//2),(im.width-1,im.height//2)]
    for seed in seeds:
        ImageDraw.floodfill(im, seed, (255,255,255,0), thresh=46)
    im.putalpha(im.getchannel("A"))
    return trim(im)


def place(im, fid, x, y, h):
    src = cutout(fid)
    w = round(src.width*h/src.height)
    src = src.resize((w,h), Image.Resampling.LANCZOS)
    im.paste(src,(x,y),src)


def page_num(im, n):
    ImageDraw.Draw(im).text((1250,1855),f"{n:02d} / 07",font=ft(22),fill="#756B68")


pages = []
# Selected V2 cover.
cover = scene(ROOT / "deliverables/style-v2/page-01.png")
ImageDraw.Draw(cover).rectangle((1190,1815,1440,1920),fill="white")
cover.save(OOUT / "page-00-cover.png"); pages.append(cover)

im = scene(ROOT / "art/vertical-v2/shot-01.png"); d=ImageDraw.Draw(im)
title(d,"项目刚结束，他想躺平……")
bubble(im,"江星野","项目搞定！从今天起，我是家里蹲。",(45,180,1040,220))
page_num(im,1); im.save(OOUT/"page-01.png"); pages.append(im)

# V2 sister lean and competition samples become shots 2 and 3.
for i in (2,3):
    im=scene(ROOT/f"deliverables/style-v2/page-{i:02d}.png")
    ImageDraw.Draw(im).rectangle((1190,1815,1440,1920),fill="white")
    page_num(im,i); im.save(OOUT/f"page-{i:02d}.png"); pages.append(im)

im = scene(ROOT / "art/vertical-v2/shot-04.png")
# Remove generator-added vertical writing in the far-right margin.
d=ImageDraw.Draw(im); d.rectangle((1210,0,1440,1040),fill="white")
title(d,"三个人，都想先约他……")
bubble(im,"小满","小叔先陪我搭城堡！",(80,165,900,205))
page_num(im,4); im.save(OOUT/"page-04.png"); pages.append(im)

im = scene(ROOT / "art/vertical-v2/shot-05.png"); d=ImageDraw.Draw(im)
title(d,"二弟决定，亲自安排……")
bubble(im,"江星野","别抢，我把时间都排好了。",(45,165,1060,210))
page_num(im,5); im.save(OOUT/"page-05.png"); pages.append(im)

# Shot 6: same V2 character standards composed into a complete schedule scene.
im=Image.new("RGB",(W,H),"white")
place(im,"older-sister",-40,610,780)
place(im,"second-brother",440,490,920)
place(im,"mother",1010,620,760)
place(im,"younger-sister",980,920,660)
place(im,"niece",30,1180,540)
d=ImageDraw.Draw(im); title(d,"妈妈的安排，永远多一项……",size=64)
d.rounded_rectangle((280,1260,1320,1775),radius=25,fill="white",outline=INK,width=6)
d.text((330,1300),"江星野的日程表",font=ft(38),fill=RED)
rows=["陪姐姐散步","陪妹妹挑书","陪小满搭城堡、讲三遍故事","二弟睡觉"]
y=1380
for i,s in enumerate(rows):
    d.text((350,y),f"{i+1}. {s}",font=ft(33 if i!=2 else 29),fill=RED if i==3 else INK); y+=88
bubble(im,"沈静宜","安排得很好，先把他的休息排上。",(35,145,850,220),size=35)
bubble(im,"江星野","我也有自己的行程啊？",(850,390,540,205),size=34)
page_num(im,6); im.save(OOUT/"page-06.png"); pages.append(im)

# Shot 7: resting composition using the same standards.
im=Image.new("RGB",(W,H),"white")
d=ImageDraw.Draw(im)
place(im,"mother",520,590,650)
place(im,"older-sister",-30,690,850)
place(im,"second-brother",420,630,920)
place(im,"younger-sister",980,730,800)
place(im,"niece",60,1240,470)
d=ImageDraw.Draw(im); title(d,"休息，也被安排得明明白白……",size=62)
d.rounded_rectangle((50,140,1390,290),radius=30,fill=INK)
d.text((80,165),"江昭远：老二，项目结束就好，别熬夜。",font=ft(35),fill="white")
bubble(im,"小满","小叔休息好，就陪我讲故事！",(110,350,1130,210),size=38)
d.rounded_rectangle((120,1775,1320,1875),radius=28,fill=INK)
d.text((165,1800),"二弟被预约的第一天，正式开始。",font=ft(39),fill=YELLOW)
page_num(im,7); im.save(OOUT/"page-07.png"); pages.append(im)

pdf_comic=ROOT/"deliverables/第一话_竖屏全页漫画.pdf"
pages[0].save(pdf_comic,save_all=True,append_images=pages[1:],resolution=150)
pages[0].save(ROOT/"deliverables/第一话_V2_完整重制.pdf",save_all=True,append_images=pages[1:],resolution=150)

# Full character cards with names and complete introductions.
cards=[]
for i,c in enumerate(DATA["characters"],1):
    im=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(im)
    d.text((50,35),c["name"],font=ft(68),fill=INK)
    d.text((55,130),c["role"],font=ft(28),fill=RED)
    d.line((50,190,1390,190),fill=INK,width=4)
    src=Image.open(ROOT/"art/character-v2"/f"{c['id']}.png").convert("RGB")
    if c["id"]=="eldest-brother":
        src=src.crop((0,0,round(src.width*.22),src.height))
    src=trim(src)
    scale=min(1050/src.width,760/src.height)
    src=src.resize((round(src.width*scale),round(src.height*scale)),Image.Resampling.LANCZOS)
    im.paste(src,((W-src.width)//2,220+(760-src.height)//2))
    d=ImageDraw.Draw(im); d.text((55,1010),"人物介绍",font=ft(30),fill=RED)
    y=1070
    for item in c["settings"]:
        d.ellipse((58,y+12,70,y+24),fill=RED)
        y=text(d,item,(90,y),1260,size=27,gap=10)+15
    d.text((55,1830),c["visual"],font=ft(22),fill="#6D6561")
    d.text((1240,1860),f"{i:02d} / 08",font=ft(21),fill="#756B68")
    im.save(COUT/f"{i:02d}-{c['id']}.png"); cards.append(im)

im=scene(ROOT/"art/family-v2/group.png"); d=ImageDraw.Draw(im)
d.rounded_rectangle((35,30,1405,210),radius=32,fill="white",outline=INK,width=5)
d.text((70,55),"星辰落进灯火里",font=ft(62),fill=INK)
d.text((75,150),"全员合照｜江怀川 · 沈静宜 · 江昭远 · 江望舒 · 江星野 · 江辰希 · 小满",font=ft(23),fill=RED)
im.save(COUT/"08-family.png"); cards.append(im)
cards[0].save(ROOT/"deliverables/完整人设与合照.pdf",save_all=True,append_images=cards[1:],resolution=150)
cards[0].save(ROOT/"deliverables/完整人设与合照_V2.pdf",save_all=True,append_images=cards[1:],resolution=150)
print("Built",len(pages),"comic pages and",len(cards),"character/family pages")
