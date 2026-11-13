#!/usr/bin/env python3
"""Working typeset for Chapter 8. Preserves source images; not a final layout."""
from pathlib import Path
import re
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
V7 = ROOT / 'deliverables/章节/第八话/review-chapter-08-reset-v7/第八话_整话新版预览.md'
DEST = ROOT / 'deliverables/章节/第八话/review-chapter-08-reset-v8/typeset'
FONT = ROOT / 'assets/fonts/NotoSansCJKsc-Regular.otf'
BOLD = ROOT / 'assets/fonts/NotoSansCJKsc-Bold.otf'
old = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', V7.read_text(encoding='utf-8'))
assert len(old)==19
sources = [(V7.parent / p).resolve() for p in old]
sources[1] = ROOT/'art/chapter-08-reset-v8/01-class-front-b.png'
sources[2] = ROOT/'art/chapter-08-reset-v8/02-solution-board.png'
sources[3] = ROOT/'art/chapter-08-reset-v8/03-friend-help.png'
sources[4] = ROOT/'art/chapter-08-reset-v8/04-friend-practice-b.png'
# Plain identified bubbles, because images do not supply reliably positioned tails.
# Text is kept deliberately compact to preserve the approved illustrations.
dialogues = {
 1: [['老师：这道研究生题，', '我看你们谁能解出来！']],
 2: [['辰希：先把积分方程', '化成微分方程。'], ['老师：居然解出来了！', '大家看看她的思路。']],
 3: [['好友：为什么要求导？'], ['辰希：求两次导数，', '再看边界条件。']],
 4: [['好友：第二个特征值，', '我算出来了！'], ['辰希：对，是4/(9π²)。']],
 5: [['会长：三个社团各用十分钟，', '从十二点十分开始。'], ['委员：音乐十二点半前结束，', '绘画十二点二十之后才到。']],
 6: [['辰希：音乐先、手工第二，', '绘画最后就不冲突了。'], ['好友：我来把时间', '和标记整理清楚。']],
 7: [['会长：好，就按这个安排。'], ['委员：我去通知三个社团！']],
 8: [['男同学：放学后一起', '去买饮料吗？'], ['辰希：不了，我要回家。']],
 9: [['好友：你这么急着回去，', '是想见二哥了？'], ['辰希：嗯，今天特别想他。']],
 10: [['辰希发消息：二哥，', '你今天在家吗？'], ['二哥回复：在家。', '路上慢点，等你回来。'], ['好友：明天见，路上小心。'], ['辰希：嗯，明天见！']],
 11: [['哥哥：回来了？'], ['辰希：二哥！']],
 13: [['辰希：今天一直想二哥，', '好想快点回来抱抱你。'], ['哥哥：那就多抱一会儿。']],
 17: [['辰希：（轻轻吸气）', '二哥，让我再靠一会儿。'], ['哥哥：好。']],
 18: [['辰希：今天解出一道难题，', '还和朋友一起安排了学生会的事。'], ['哥哥：听起来很充实，', '慢慢讲给我听。'], ['辰希：好，不过先让我', '再靠一会儿。']],
}

def draw_bubbles(im, paragraphs, page):
    d = ImageDraw.Draw(im); w,h=im.size
    # Normalize layout to actual source dimensions, never resize source.
    cols = 2 if len(paragraphs)>1 else 1
    rows = (len(paragraphs)+cols-1)//cols
    margin = int(w*.025); gap = int(w*.022)
    availw = w-2*margin
    cellw = (availw-gap*(cols-1))//cols
    cellh = int(h*(.08 if page == 13 else (.108 if page != 10 else .088)))
    top = int(h*.012)
    for i, lines in enumerate(paragraphs):
        row,col=divmod(i,cols)
        x0=margin+col*(cellw+gap); y0=top+row*(cellh+int(h*.006))
        x1=x0+cellw; y1=y0+cellh
        font_size=max(17, min(24, round(w/36)))
        while font_size>=15:
            font=ImageFont.truetype(str(BOLD),font_size)
            widths=[d.textbbox((0,0),t,font=font)[2] for t in lines]
            if max(widths)<=cellw-30 and len(lines)*(font_size+8)<=cellh-12: break
            font_size-=1
        if font_size<15: raise ValueError(f'page {page} bubble overflow: {lines}')
        d.rounded_rectangle((x0,y0,x1,y1), radius=25, fill='#fffefb',outline='#353839',width=2)
        lineh=font_size+8; y=y0+(cellh-lenh(lines,lineh))//2-3
        for t in lines:
            d.text((x0+(cellw-d.textlength(t,font=font))/2,y),t,font=font,fill='#20282a')
            y+=lineh

def lenh(lines,lineh): return len(lines)*lineh

def board(im,page):
    d=ImageDraw.Draw(im)
    if page==1:
        font=ImageFont.truetype(str(FONT),26)
        lines=['f ∈ L²[0,1]，0 ≤ x ≤ 1', 'Kf(x) = ∫[0,1] min(x,t)f(t)dt', '求 K 的非零特征值与特征函数。']
        for y,t in zip((215,265,315),lines): d.text((230,y),t,font=font,fill='#f3f4df')
    if page==2:
        font=ImageFont.truetype(str(FONT),23)
        lines=['λf = Kf  ⇒  f″ + f/λ = 0', 'f(0) = 0，f′(1) = 0', 'λ(n) = 1/[(n−½)²π²]，n = 1, 2, …', 'f(n,x) = C sin[(n−½)πx]，C ≠ 0']
        for y,t in zip((331,368,405,442),lines): d.text((220,y),t,font=font,fill='#f4f5e5')

DEST.mkdir(parents=True,exist_ok=True)
for page,paragraphs in dialogues.items():
    if len(sys.argv) > 1 and page not in {int(x) for x in sys.argv[1:]}:
        continue
    with Image.open(sources[page]) as src: im=src.convert('RGB')
    if page in (1,2): board(im,page)
    draw_bubbles(im,paragraphs,page)
    out=DEST/f'{page:02}.png'; im.save(out,optimize=True)
    print(page, out.relative_to(ROOT), im.size)
