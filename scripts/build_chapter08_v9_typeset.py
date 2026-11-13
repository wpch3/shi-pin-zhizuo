#!/usr/bin/env python3
"""Working typeset, drawn on copies; requires Pillow and fonttools."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'deliverables/章节/第八话/review-chapter-08-reset-v9/typeset'
HAND = ROOT/'assets/fonts/chapter08-handwriting/PatrickHand-Regular.ttf'
CHINESE = ROOT/'assets/fonts/chapter08-handwriting/MaShanZheng-Regular.ttf'
FALLBACK = ROOT/'assets/fonts/NotoSansCJKsc-Regular.otf'
BOLD = ROOT/'assets/fonts/NotoSansCJKsc-Bold.otf'
CMAPS = {p:set(TTFont(p).getBestCmap()) for p in (HAND, CHINESE, FALLBACK)}
FONTS = {}
def font(p, size):
    key=(p,size)
    if key not in FONTS: FONTS[key]=ImageFont.truetype(str(p),size)
    return FONTS[key]
def mixed(draw,x,baseline,text,size=32,color='#f4f2de',preferred=HAND):
    for char in text:
        if char.isspace():
            x+=font(preferred,size).getlength(char); continue
        candidates=(preferred,FALLBACK)
        chosen=next((p for p in candidates if ord(char) in CMAPS[p]),None)
        if chosen is None: raise ValueError(f'No glyph for {char!r}')
        f=font(chosen,size)
        draw.text((round(x),round(baseline)),char,font=f,anchor='ls',fill=color)
        x+=f.getlength(char)
    return x

def board(im,page):
    d=ImageDraw.Draw(im)
    if page==1:
        x=mixed(d,230,247,'f ∈ L²[0,1],  0 ≤ x ≤ 1',34)
        assert x<795
        x=mixed(d,230,302,'Kf(x) = ',36)
        x=mixed(d,x,302,'∫',39)
        # Stacked bounds use normal handwritten digits, not unsupported glyphs.
        d.text((round(x-1),270),'1',font=font(HAND,18),fill='#f4f2de')
        d.text((round(x-1),296),'0',font=font(HAND,18),fill='#f4f2de')
        x=mixed(d,x+13,302,' min(x,t) f(t) dt',36)
        assert x<795, x
        x=mixed(d,230,355,'求 K 的非零特征值与特征函数。',31,preferred=CHINESE)
        assert x<795, x
    elif page==2:
        x=mixed(d,220,360,"λf = Kf  ⇒  f'' + f/λ = 0",31)
        assert x<749, x
        x=mixed(d,220,392,"f(0) = 0,   f'(1) = 0",31)
        assert x<749, x
        x=mixed(d,220,424,'λ',31)
        x=mixed(d,x,430,'n',20)
        x=mixed(d,x+2,424,' = 1/[(n−½)²π²],   n = 1, 2, ...',31)
        assert x<749, x
        x=mixed(d,220,456,'f',31)
        x=mixed(d,x,462,'n',20)
        x=mixed(d,x+2,456,'(x) = C sin[(n−½)πx],   C ≠ 0',31)
        assert x<749, x

def bubbles(im,lines):
    d=ImageDraw.Draw(im); w,h=im.size
    margin=int(w*.025); gap=int(w*.022); n=len(lines); cols=2 if n>1 else 1
    cellw=(w-2*margin-gap*(cols-1))//cols; cellh=int(h*.108); top=int(h*.012)
    for i,words in enumerate(lines):
        row,col=divmod(i,cols); x=margin+col*(cellw+gap); y=top+row*(cellh+int(h*.006))
        size=min(24,round(w/36))
        while size>=15:
            f=font(BOLD,size)
            if max(d.textlength(t,font=f) for t in words)<=cellw-30 and len(words)*(size+8)<=cellh-12: break
            size-=1
        if size<15: raise ValueError('Bubble overflow')
        d.rounded_rectangle((x,y,x+cellw,y+cellh),radius=25,fill='#fffefb',outline='#353839',width=2)
        lh=size+8; ty=y+(cellh-len(words)*lh)//2-3
        for t in words:
            d.text((x+(cellw-d.textlength(t,font=f))/2,ty),t,font=f,fill='#20282a'); ty+=lh

def notebook(im,page):
    # Sparse, accurate note on the left page; avoids the drawn fingers and pencil.
    # Render large then downsample for legible antialiasing in the tiny paper area.
    from PIL import Image as PILImage
    scale=4
    layer=PILImage.new('RGBA',(320,80),(0,0,0,0))
    d=ImageDraw.Draw(layer)
    if page==3:
        mixed(d,10,55,'λ > 0',56,color='#464646')
    else:
        mixed(d,10,55,'n = 2',56,color='#464646')
    layer=layer.rotate(12,resample=PILImage.Resampling.BICUBIC,expand=True)
    layer=layer.resize((round(layer.width/scale),round(layer.height/scale)),PILImage.Resampling.LANCZOS)
    im.paste(layer,(463,755),layer)

def schedule(im,page):
    # The sheet is tiny: only the three start times are put on it. The order
    # of clubs is already stated in the dialogue; avoid illegible microprint.
    layer=Image.new('RGBA',(640,110),(0,0,0,0))
    d=ImageDraw.Draw(layer)
    text='12:10' if page==6 else '12:10   12:20   12:30'
    mixed(d,4,54,text,44,color='#4a4742')
    layer=layer.rotate(4,resample=Image.Resampling.BICUBIC,expand=True)
    layer=layer.resize((round(layer.width/4),round(layer.height/4)),Image.Resampling.LANCZOS)
    im.paste(layer,(365,781),layer)

# Input images unchanged, only new output copies receive board and dialogue.
pages={
1:('art/chapter-08-reset-v8/01-class-front-b.png', [['老师：这道研究生题，','我看你们谁能解出来！']]),
2:('art/chapter-08-reset-v8/02-solution-board.png', [['辰希：先把积分方程','化成微分方程。'],['老师：居然解出来了！','大家看看她的思路。']]),
3:('art/chapter-08-reset-v9/03-help-classroom-b.png', [['好友：为什么要求导？'],['辰希：求两次导数，','再看边界条件。']]),
4:('art/chapter-08-reset-v9/04-practice-classroom.png', [['好友：第二个特征值，','我算出来了！'],['辰希：对，是4/(9π²)。']]),
6:('deliverables/章节/第八话/review-chapter-08-reset-v8/typeset/06.png',None),
7:('deliverables/章节/第八话/review-chapter-08-reset-v8/typeset/07.png',None),
}
if __name__ == "__main__":
    OUT.mkdir(parents=True,exist_ok=True)
    for page,(source,dialogue) in pages.items():
        with Image.open(ROOT/source) as src: im=src.convert('RGB')
        if page in (1,2): board(im,page)
        if page in (3,4): notebook(im,page)
        if page in (6,7): schedule(im,page)
        if dialogue is not None: bubbles(im,dialogue)
        im.save(OUT/f'{page:02}.png',optimize=True)
        print('typeset',page,im.size)
