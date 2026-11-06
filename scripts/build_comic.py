#!/usr/bin/env python3
"""Build the locked character sheets and chapter 1 four-panel comic.
Requires Pillow. All Chinese lettering is rendered here, never generated in-image.
"""
from pathlib import Path
import json
import math
import re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
FONT_PATH = ROOT / "assets/fonts/NotoSansCJKsc-Regular.otf"
CHAR_DIR = ROOT / "art/characters"
CUT_DIR = ROOT / "art/cutouts"
OUT = ROOT / "deliverables"
SHEETS = OUT / "character-sheets"
PAGES = OUT / "chapter-01"
for d in (CUT_DIR, SHEETS, PAGES):
    d.mkdir(parents=True, exist_ok=True)

INK = "#283037"
PAPER = "#FAF7F0"
CREAM = "#F4E9D5"
BLUE = "#496478"
MUTED = "#6B7376"
FONT_CACHE = {}

def font(size):
    if size not in FONT_CACHE:
        FONT_CACHE[size] = ImageFont.truetype(str(FONT_PATH), size)
    return FONT_CACHE[size]

def wrap(text, f, width):
    lines = []
    closing = "，。！？；：、）》】”’…"
    for para in text.split("\n"):
        if not para:
            lines.append("")
            continue
        line = ""
        tokens = re.findall(r"[A-Za-z0-9]+(?:[./-][A-Za-z0-9]+)*|.", para)
        for token in tokens:
            test = line + token
            if line and f.getlength(test) > width and token not in closing:
                lines.append(line)
                line = token
            else:
                line = test
        if line:
            lines.append(line)
    return lines

def fit_cover(im, size, center=(0.5, 0.5)):
    w, h = size
    scale = max(w / im.width, h / im.height)
    nw, nh = round(im.width * scale), round(im.height * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = round((nw - w) * center[0])
    top = round((nh - h) * center[1])
    left = max(0, min(nw - w, left))
    top = max(0, min(nh - h, top))
    return im.crop((left, top, left + w, top + h))

def cutout(char_id, filename):
    target = CUT_DIR / filename
    if target.exists():
        return Image.open(target).convert("RGBA")
    im = Image.open(CHAR_DIR / filename).convert("RGBA")
    # The generated reference has a connected, almost-white studio background.
    # Flood only from the outer edges so white shirts inside ink outlines remain.
    seeds = [(0,0),(im.width-1,0),(0,im.height-1),(im.width-1,im.height-1),
             (im.width//2,0),(im.width//2,im.height-1),(0,im.height//2),(im.width-1,im.height//2)]
    for seed in seeds:
        if im.getpixel(seed)[3] != 0:
            ImageDraw.floodfill(im, seed, (255,255,255,0), thresh=48)
    alpha = im.getchannel("A").filter(ImageFilter.GaussianBlur(0.65))
    im.putalpha(alpha)
    # Trim using a meaningful alpha threshold; blurred fully-transparent pixels
    # must not leave hundreds of empty columns around the actual figure.
    solid = np.array(im.getchannel("A")) > 30
    # Ignore isolated background flecks when calculating the visual bounds.
    cols = np.flatnonzero(solid.sum(axis=0) > 10)
    rows = np.flatnonzero(solid.sum(axis=1) > 10)
    if len(cols) and len(rows):
        box = (int(cols[0]), int(rows[0]), int(cols[-1])+1, int(rows[-1])+1)
        im = im.crop(box)
    im.save(target)
    return im

CHARACTERS = json.loads((ROOT / "data/characters.json").read_text(encoding="utf-8"))["characters"]
CUTS = {c["id"]: cutout(c["id"], c["file"]) for c in CHARACTERS}

def place_char(panel, char_id, height, x, bottom, angle=0, flip=False):
    im = CUTS[char_id]
    if flip:
        im = ImageOps.mirror(im)
    w = round(im.width * height / im.height)
    im = im.resize((w, height), Image.Resampling.LANCZOS)
    if angle:
        im = im.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    panel.alpha_composite(im, (round(x-im.width/2), round(bottom-im.height)))

def line(d, xy, fill=INK, width=4):
    d.line(xy, fill=fill, width=width)

def background(kind, size):
    w,h = size
    im = Image.new("RGBA", size, "#F7F4EC")
    d = ImageDraw.Draw(im)
    # Deliberately quiet line-art scenery: neutral light, no bloom or orange filter.
    if kind in ("living", "entry", "kitchen"):
        d.rectangle((0,0,w,h), fill="#F4F1E9")
        d.rectangle((0,int(h*.72),w,h), fill="#E3E0D8")
        line(d,(0,int(h*.72),w,int(h*.72)),"#899094",4)
        if kind == "living":
            d.rectangle((45,170,320,570), fill="#E5F0F1", outline="#65757B", width=5)
            line(d,(182,170,182,570),"#879397",3); line(d,(45,365,320,365),"#879397",3)
            d.rectangle((25,140,65,600), fill="#DDD4C6"); d.rectangle((300,140,340,600), fill="#DDD4C6")
            d.rounded_rectangle((80,760,740,1030),25,fill="#D7D2C7",outline="#7B807E",width=5)
            line(d,(110,835,710,835),"#A09D96",3)
            d.rectangle((590,420,750,440),fill="#B8A991"); line(d,(610,440,610,720),"#8C8170",8); line(d,(730,440,730,720),"#8C8170",8)
            d.rectangle((612,315,728,420),fill="#ECE3D3",outline="#7F7B72",width=4)
        elif kind == "entry":
            d.rectangle((440,110,755,830),fill="#D9CBB7",outline="#736E66",width=6)
            d.rectangle((475,150,720,560),fill="#EEE9DE",outline="#8D867B",width=4)
            d.ellipse((690,590,710,610),fill="#5D5B55")
            d.rectangle((40,600,325,860),fill="#E2D8C7",outline="#827B70",width=5)
            for yy in (685,770): line(d,(40,yy,325,yy),"#A39A8C",3)
        else:
            d.rectangle((20,120,790,410),fill="#E4E0D6",outline="#888980",width=4)
            for xx in (210,410,610): line(d,(xx,120,xx,410),"#AAA69C",3)
            d.rectangle((0,610,w,770),fill="#D8C7AE",outline="#7B7469",width=5)
            d.rectangle((35,430,310,610),fill="#E8E3D9",outline="#8B8A82",width=4)
            d.ellipse((520,515,680,590),fill="#FAF8F2",outline="#85857E",width=4)
            d.ellipse((555,530,645,570),fill="#D9B77D")
    elif kind in ("office", "school"):
        d.rectangle((0,0,w,h),fill="#F1F2EE")
        d.rectangle((0,int(h*.76),w,h),fill="#DFE1DC")
        if kind == "office":
            d.rectangle((40,80,w-40,590),fill="#E4EFF0",outline="#687A80",width=5)
            for xx in (w//3,2*w//3): line(d,(xx,80,xx,590),"#91A0A2",3)
            for i,hh in enumerate((130,210,170,260,190)):
                x=70+i*135
                d.rectangle((x,590-hh,x+90,590),fill="#C5D4D5",outline="#91A4A7",width=2)
            d.polygon([(30,810),(790,810),(700,1050),(110,1050)],fill="#D8D0C3",outline="#7B7D78")
        else:
            d.rectangle((40,100,470,560),fill="#CBBBA4",outline="#746E65",width=7)
            for x,y in ((80,140),(250,170),(110,340),(300,350)):
                d.rectangle((x,y,x+130,y+140),fill="#F8F6EE",outline="#999387",width=2)
                for yy in range(y+35,y+120,22): line(d,(x+18,yy,x+110,yy),"#C4C0B7",2)
            for x in range(540,790,82):
                d.rectangle((x,250,x+75,800),fill="#D5DAD6",outline="#8B918C",width=3)
                line(d,(x+12,330,x+55,330),"#A4AAA5",3)
    else:
        d.rectangle((0,0,w,h),fill="#F2EFE7")
        for r in range(120,900,110):
            d.arc((w//2-r,h//2-r,w//2+r,h//2+r),200,340,fill="#DDD9D0",width=3)
    return im

def add_device(panel, char_id, box, phone=False):
    x0,y0,x1,y1=box
    d=ImageDraw.Draw(panel)
    radius=28 if phone else 14
    d.rounded_rectangle(box,radius,fill="#27333C",outline="#12191E",width=5)
    inner=(x0+12,y0+14,x1-12,y1-18)
    d.rounded_rectangle(inner,12,fill="#E8E3D8")
    im=CUTS[char_id]
    target_h=(y1-y0)-35
    target_w=(x1-x0)-30
    scale=max(target_w/im.width,target_h/im.height)
    im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
    crop=fit_cover(im,(target_w,target_h),(0.5,0.0))
    panel.alpha_composite(crop,(x0+15,y0+15))
    if phone:
        d.ellipse(((x0+x1)//2-5,y1-12,(x0+x1)//2+5,y1-2),fill="#8C989F")

def bubble(panel, spec):
    # spec: x, y, width, text, optional tail side
    x,y,bw,text,*rest=spec
    d=ImageDraw.Draw(panel)
    f=font(32)
    lines=wrap(text,f,bw-42)
    lh=45
    bh=max(76,len(lines)*lh+34)
    d.rounded_rectangle((x,y,x+bw,y+bh),28,fill="#FFFFFF",outline=INK,width=4)
    if rest and rest[0]:
        side=rest[0]
        if side=="left":
            pts=[(x+55,y+bh-3),(x+92,y+bh-3),(x+50,y+bh+36)]
        else:
            pts=[(x+bw-92,y+bh-3),(x+bw-55,y+bh-3),(x+bw-35,y+bh+36)]
        d.polygon(pts,fill="#FFFFFF")
        line(d,(pts[0],pts[2]),INK,4); line(d,(pts[2],pts[1]),INK,4)
    total=len(lines)*lh
    ty=y+(bh-total)//2-2
    for ln in lines:
        tw=f.getlength(ln)
        d.text((x+(bw-tw)/2,ty),ln,font=f,fill=INK)
        ty+=lh

def caption(panel,text,position="bottom"):
    if not text: return
    d=ImageDraw.Draw(panel)
    f=font(28)
    lines=wrap(text,f,panel.width-64)
    hh=len(lines)*40+28
    y=panel.height-hh-20 if position=="bottom" else 20
    d.rounded_rectangle((20,y,panel.width-20,y+hh),12,fill="#314753",outline="#314753")
    yy=y+12
    for ln in lines:
        d.text((38,yy),ln,font=f,fill="#FFFFFF")
        yy+=40

def panel_base(kind):
    return background(kind,(822,1085))

PANEL_W,PANEL_H=822,1085

def make_existing(filename,center,fit_mode="cover"):
    im=Image.open(ROOT/"art/chapter-01"/filename).convert("RGBA")
    if fit_mode in ("wide", "ensemble"):
        # Quiet paper bands are reserved for dialogue and captions. Ensemble
        # uses a slightly wider crop so every family member stays in frame.
        panel=Image.new("RGBA",(PANEL_W,PANEL_H),"#F5F2EA")
        if fit_mode == "ensemble":
            art=fit_cover(im,(PANEL_W,560),center)
            panel.alpha_composite(art,(0,205))
        else:
            art=fit_cover(im,(PANEL_W,690),center)
            panel.alpha_composite(art,(0,170))
        return panel
    return fit_cover(im,(PANEL_W,PANEL_H),center)

def compose(spec):
    if spec.get("existing"):
        p=make_existing(spec["existing"],spec.get("center",(.5,.5)),spec.get("fit","cover"))
    else:
        p=panel_base(spec.get("bg","plain"))
        if spec.get("device_back"):
            add_device(p,*spec["device_back"])
        for c in spec.get("chars",[]):
            place_char(p,*c)
        if spec.get("device"):
            add_device(p,*spec["device"])
        d=ImageDraw.Draw(p)
        for x,y in spec.get("accents",[]):
            d.line((x,y,x-22,y+45),fill="#61727A",width=4)
            d.line((x+12,y-5,x+2,y+42),fill="#61727A",width=4)
    d=ImageDraw.Draw(p)
    d.rectangle((0,0,p.width-1,p.height-1),outline=INK,width=6)
    for b in spec.get("bubbles",[]): bubble(p,b)
    caption(p,spec.get("caption",""),spec.get("caption_pos","bottom"))
    return p.convert("RGB")

# Character placement tuple: id, height, center-x, bottom-y, optional angle, optional flip.
CHAPTER = [
 {"title":"01｜外人眼里", "panels":[
  {"existing":"p01-panel1.png","center":(.64,.45),"caption":"姐姐｜SHJD博士，目前在上海就职","bubbles":[(35,40,390,"这份方案，麻烦您把关。","left"),(430,215,340,"好，交给我。","right")]},
  {"existing":"p01-panel2.png","center":(.70,.45),"caption":"妹妹｜CQ第一中学，准备去英国留学","bubbles":[(30,40,455,"SAT和AP都通过了，真厉害！","left"),(390,800,380,"接下来，还要准备留学。","right")]},
  {"existing":"p01-panel3.png","center":(.50,.40),"caption":"大哥｜常年在外地，G企项目总经理","bubbles":[(30,40,420,"总经理，会议准备好了。","left"),(490,235,265,"按计划开始。","right")]},
  {"bg":"living","caption":"二哥｜QH毕业，在家也能扛住大项目","chars":[("second-brother",900,460,1090)],"bubbles":[(35,35,365,"爸：这个项目，交给你了。","left"),(390,800,380,"放心，我会处理好。","right")]}
 ]},
 {"title":"02｜在家办公的人", "panels":[
  {"existing":"p02-panel1.png","fit":"wide","caption":"没有出门，不等于没有工作。","chars":[("second-brother",1050,500,1120)],"bubbles":[(35,45,390,"关键数据，再核一遍。","left")]},
  {"existing":"p02-panel2.png","fit":"wide","caption":"父亲很少回家，项目却放心交给他。","chars":[("second-brother",900,565,1090)],"device_back":("father",(55,380,330,740),False),"bubbles":[(35,35,395,"做得不错，后续按你的判断推进。","left"),(430,800,300,"明白，爸。","right")]},
  {"existing":"p02-panel3.png","fit":"wide","caption":"最后一项确认完毕。","chars":[("second-brother",860,450,1100,0,True)],"bubbles":[(55,45,350,"好，工作结束。","left")],"accents":[(675,250)]},
  {"existing":"p02-panel4.png","fit":"wide","center":(.58,.50),"caption":"就在这时——","chars":[("mother",840,280,1090),("second-brother",760,660,1090)],"bubbles":[(35,35,350,"妈：先别忙了，开饭啦！","left"),(500,800,230,"好——","right")]}
 ]},
 {"title":"03｜回家的开关", "panels":[
  {"existing":"p03-panel1.png","center":(.50,.40),"caption":"姐姐回家了。还是刚才那位职场精英。","chars":[("older-sister",910,360,1090)],"bubbles":[(45,40,300,"我回来了。","left")]},
  {"existing":"p03-panel2.png","center":(.64,.40),"caption":"看见弟弟的一瞬间，她先卸下了力气。","chars":[("second-brother",960,590,1110),("older-sister",900,280,1100,-7)],"bubbles":[(35,35,430,"弟弟，今天让我靠一会儿。","left"),(450,800,300,"辛苦了，姐。","right")]},
  {"existing":"p03-panel3.png","center":(.73,.40),"caption":"妹妹也回家了。","chars":[("younger-sister",900,355,1090)],"bubbles":[(40,40,390,"二哥，我也回来了。","left")]},
  {"existing":"p03-panel4.png","center":(.64,.40),"caption":"在外的从容，到家就暂时寄存在门口。","chars":[("second-brother",970,575,1110),("younger-sister",900,260,1100,6)],"bubbles":[(25,30,465,"今天很认真。现在……让我撒会儿娇。","left"),(510,800,250,"好，先坐。","right")]}
 ]},
 {"title":"04｜最后一个挂件", "panels":[
  {"bg":"entry","caption":"小侄女听见了二哥的声音。","chars":[("niece",630,290,1090),("second-brother",850,650,1090)],"bubbles":[(40,40,280,"小叔叔！","left"),(420,790,350,"慢点，别摔着。","right")]},
  {"bg":"living","caption":"从小抱到大的默契，不需要预告。","chars":[("second-brother",990,540,1110),("niece",690,250,1110,-8)],"bubbles":[(35,35,400,"今天也一直想着你！","left"),(390,790,390,"我这不是在这儿吗。","right")]},
  {"existing":"p04-panel3.png","fit":"wide","caption":"于是，刚收工的二哥成了全家的人形靠垫。","chars":[("second-brother",980,445,1120),("older-sister",790,150,1100,-5),("younger-sister",800,720,1100,5),("niece",530,440,1110)],"bubbles":[(30,30,395,"你们……让我先放下电脑。","left"),(470,800,280,"就一会儿。","right")],"accents":[(750,320)]},
  {"bg":"living","caption":"大哥的视频通话，偏偏在这时接通。","chars":[("second-brother",760,650,1100),("niece",450,330,1090)],"device":("eldest-brother",(35,240,345,810),True),"bubbles":[(35,30,510,"我不在家，你们就这么热闹？","left"),(520,800,230,"大哥？","right")]}
 ]},
 {"title":"05｜开饭以前", "panels":[
  {"bg":"living","caption":"大哥没有忘记正事。","chars":[("second-brother",900,590,1100)],"device_back":("eldest-brother",(45,345,340,780),True),"bubbles":[(35,35,400,"项目的事，爸夸你了。","left"),(330,780,450,"是大家一起配合得好。","right")]},
  {"bg":"living","caption":"姐姐依赖他，也同样信任他。","chars":[("second-brother",880,430,1110),("older-sister",780,150,1100),("younger-sister",770,710,1100)],"bubbles":[(25,30,420,"家里也一样，他一直很可靠。","left"),(480,800,280,"嗯，最可靠。","right")]},
  {"bg":"kitchen","caption":"母亲把最后一道菜放上桌。","chars":[("mother",820,520,1090)],"device_back":("eldest-brother",(35,390,300,770),True),"bubbles":[(35,35,360,"妈：开饭了，都过来吧。","left"),(450,800,300,"给我留个位置！","right")]},
  {"existing":"p05-panel4.png","fit":"ensemble","caption":"在外面，他们各自发光。\n回到家，只是彼此最亲的人。","chars":[("mother",700,100,1100),("older-sister",720,285,1100),("second-brother",790,490,1110),("younger-sister",690,710,1100),("niece",480,600,1110)],"device_back":("eldest-brother",(615,700,785,1020),True),"bubbles":[(25,30,390,"小叔叔，饭后给我讲故事！","left"),(470,790,290,"好，先吃饭。","right")]}
 ]}
]


def build_pages():
    page_files=[]
    for pi,page in enumerate(CHAPTER,1):
        canvas=Image.new("RGB",(1800,2546),PAPER)
        d=ImageDraw.Draw(canvas)
        d.text((64,30),"回家以后",font=font(54),fill=INK)
        d.text((370,48),"第一话｜外人眼里的他们",font=font(32),fill=MUTED)
        d.text((1510,48),page["title"],font=font(28),fill=BLUE)
        line(d,(64,130,1736,130),"#9EAAA9",3)
        positions=[(64,160),(914,160),(64,1273),(914,1273)]
        for spec,pos in zip(page["panels"],positions):
            p=compose(spec)
            canvas.paste(p,pos)
        d.text((64,2492),"四格短篇漫画 · 无语音版",font=font(24),fill=MUTED)
        footer=f"第一话{'·完' if pi == 5 else ''} · 第 {pi} / 5 页"
        tw=font(24).getlength(footer)
        d.text((1736-tw,2492),footer,font=font(24),fill=MUTED)
        path=PAGES/f"page-{pi:02d}.png"
        canvas.save(path,optimize=True)
        page_files.append(path)
    images=[Image.open(p).convert("RGB") for p in page_files]
    images[0].save(OUT/"回家以后_第一话.pdf",save_all=True,append_images=images[1:],resolution=220,quality=92)
    return page_files


def build_sheets():
    files=[]
    for idx,c in enumerate(CHARACTERS,1):
        im=Image.new("RGBA",(1800,1200),PAPER)
        d=ImageDraw.Draw(im)
        accent=c["accent"]
        d.rectangle((0,0,32,1200),fill=accent)
        d.text((78,56),"CHARACTER PROFILE",font=font(24),fill=MUTED)
        d.text((78,100),f"{idx:02d}",font=font(86),fill=accent)
        d.ellipse((90,815,625,1100),fill="#EFE9DE")
        cut=CUTS[c["id"]]
        hh=900 if c["id"] == "second-brother" else 990
        center_x=300 if c["id"] == "second-brother" else 360
        ww=round(cut.width*hh/cut.height)
        portrait=cut.resize((ww,hh),Image.Resampling.LANCZOS)
        im.alpha_composite(portrait,(center_x-ww//2,1110-hh))
        d.text((720,75),c["name"],font=font(68),fill=INK)
        d.text((725,175),"设定原文锁定 · 不作改写",font=font(28),fill=accent)
        line(d,(720,240,1715,240),"#B5B8B3",3)
        y=285
        body=font(37)
        for bullet in c["settings"]:
            lines=wrap(bullet,body,925)
            d.ellipse((728,y+16,742,y+30),fill=accent)
            for ln in lines:
                d.text((765,y),ln,font=body,fill=INK)
                y+=55
            y+=28
        box_top=max(y+15,865)
        d.rounded_rectangle((715,box_top,1718,1085),18,fill="#F0EBE1",outline="#D2CCC0",width=2)
        d.text((745,box_top+24),"视觉锚点",font=font(28),fill=accent)
        yy=box_top+77
        for ln in wrap(c["visual"],font(31),900):
            d.text((745,yy),ln,font=font(31),fill=MUTED); yy+=46
        d.text((720,1130),"《回家以后》 · 全员人设",font=font(23),fill=MUTED)
        path=SHEETS/f"{idx:02d}-{c['id']}.png"
        im.convert("RGB").save(path,optimize=True)
        files.append(path)
    images=[Image.open(p).convert("RGB") for p in files]
    images[0].save(OUT/"全员人设图.pdf",save_all=True,append_images=images[1:],resolution=180,quality=92)
    return files


def write_script_doc():
    lines=["# 《回家以后》第一话分镜与对白","","规格：5页，每页4格，共20格；无语音。","人设文字不在剧情中改写，故事仅组织已确定的关系与能力。",""]
    for pi,page in enumerate(CHAPTER,1):
        lines.extend([f"## 第{pi}页：{page['title'].split('｜')[-1]}",""])
        for gi,spec in enumerate(page["panels"],1):
            lines.append(f"### {pi}-{gi}")
            lines.append(f"- 旁白/字幕：{spec.get('caption','无').replace(chr(10),' / ')}")
            for b in spec.get("bubbles",[]):
                lines.append(f"- 对白：{b[3]}")
            lines.append("")
    (ROOT/"docs/第一话分镜与对白.md").write_text("\n".join(lines),encoding="utf-8")

if __name__ == "__main__":
    build_sheets()
    build_pages()
    write_script_doc()
    print(f"Built {len(list(SHEETS.glob('*.png')))} character sheets and {len(list(PAGES.glob('*.png')))} comic pages in {OUT}")
