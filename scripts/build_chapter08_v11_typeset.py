#!/usr/bin/env python3
"""Chapter 8 speech trial: clean artwork -> measured, single-outline balloons.
Original approved images remain untouched. Requires Pillow/fonttools.
"""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables/章节/第八话/review-chapter-08-reset-v11/typeset'
# v11 is user-approved. Do not let this historical one-off overwrite any pages.
if OUT.exists() and any(OUT.glob('*.png')):
    raise SystemExit('第八话 v11 已有页面；为保护确认版，禁止原地重建。请复制脚本并使用新的输出目录。')

import sys
from PIL import Image, ImageDraw, ImageFont, ImageChops
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text
import build_chapter08_v9_typeset as old

OUT.mkdir(parents=True,exist_ok=True)
FONT=ROOT/'assets/fonts/NotoSansCJKsc-Regular.otf'
# center, target mouth, lines. Coordinates are specific to each unscaled source.
PAGES={
0:('art/chapter-08-reset-v7/cover-walking-conversation.png', [((220,145),(345,380),['下课后，','一起看看笔记吧。']),((650,205),(625,390),['嗯，一起看。'])]),
1:('art/chapter-08-reset-v8/01-class-front-b.png', [((175,95),(158,320),['这道研究生题，','我看你们谁能解出来！'])]),
2:('art/chapter-08-reset-v8/02-solution-board.png', [((540,165),(540,620),['先把积分方程','化成微分方程。']),((170,250),(145,540),['居然解出来了！','大家看看她的思路。'])]),
3:('art/chapter-08-reset-v10/03-help-style-candidate.png', [((558,475),(550,765),['为什么要求导？']),((205,550),(260,765),['求两次导数，','再看边界条件。'])]),
4:('art/chapter-08-reset-v9/04-practice-classroom.png', [((625,370),(635,680),['第二个特征值，','我算出来了！']),((210,430),(335,680),['对，是4/(9π²)。'])]),
5:('art/chapter-08-reset-v1/04-council-discuss.png', [((450,195),(578,482),['三个社团各用','十分钟，十二点','十分开始。']),((705,195),(721,488),['音乐十二点半前','结束，绘画十二点','二十之后才到。'])]),
6:('art/chapter-08-reset-v2/06-council-solution.png', [((205,270),(168,601),['音乐先、手工第二，','绘画最后就不冲突了。']),((365,385),(346,607),['我来把时间','整理清楚。'])]),
7:('art/chapter-08-reset-v3/07-council-close.png', [((440,245),(575,482),['好，就这么定了。']),((700,245),(720,486),['我去通知三个社团！'])]),
8:('art/chapter-08-reset-v2/08-refusal.png', [((650,175),(650,500),['放学后一起','去买饮料吗？']),((342,290),(440,565),['不了，我要回家。'])]),
9:('art/chapter-08-reset-v3/09-friends.png', [((200,235),(266,586),['你这么急着回去，','是想见二哥了？']),((553,305),(520,530),['嗯，今天特别想他。'])]),
10:('art/chapter-08-reset-v4/10-goodbye.png', [((205,180),(333,450),['二哥在家！','明天见！']),((627,250),(573,468),['明天见，路上小心。'])]),
11:('art/chapter-08-reset-v1/09-entrance.png', [((650,78),(635,295),['回来了？']),((275,180),(310,418),['二哥！'])]),
12:('art/chapter-08-reset-v3/11-change-shoes.png', [((655,90),(640,300),['慢慢来，别着急。'])]),
13:('art/chapter-08-reset-v2/12-standing-hug.png', [((180,145),(425,388),['今天一直想你，','好想快点回来抱抱你。']),((695,155),(475,235),['那就多抱一会儿。'])]),
14:('art/chapter-08-reset-v5/14-koala-clear.png', [((690,130),(486,225),['抱稳了。'])]),
15:('art/chapter-08-reset-v6/15-lowering-transition.png', [((650,80),(480,220),['我们去沙发坐吧。'])]),
16:('art/chapter-08-reset-v6/16-sitting-transition.png', [((215,210),(343,467),['嗯！我还有好多事','想告诉你。'])]),
17:('art/chapter-08-reset-v3/13-cheek-chest-c.png', [((270,250),(483,540),['（轻轻吸气）','二哥，让我再靠一会儿。']),((730,315),(533,380),['好。'])]),
18:('art/chapter-08-reset-v3/14-share-day.png', [((220,150),(344,460),['今天解出一道难题，','还和朋友一起安排了','学生会的事。']),((710,150),(530,380),['听起来很充实，','慢慢讲给我听。'])]),
}

def bubble(im,center,target,lines,size=22,tail_length=45):
    # Measure on source-sized page, then supersample a unified outline for crisp curves.
    font=ImageFont.truetype(str(FONT),size); d=ImageDraw.Draw(im)
    layout=measure_speech_text(d,lines,center,font,size)
    box=layout['box']; w,h=im.size
    if box[0]<15 or box[1]<15 or box[2]>w-15 or box[3]>h-15: raise ValueError((box,im.size))
    pts=oval_speech(center,layout['bubble_size'],target,tail_length=tail_length,tail_width=22,bend=1)
    s=3; layer=Image.new('RGBA',(w*s,h*s)); pen=ImageDraw.Draw(layer)
    poly=[(round(x*s),round(y*s)) for x,y in pts]
    pen.polygon(poly,fill=(255,254,249,255)); pen.line(poly+[poly[0]],fill=(49,50,47,255),width=2*s,joint='curve')
    im.alpha_composite(layer.resize((w,h),Image.Resampling.LANCZOS))
    d=ImageDraw.Draw(im)
    for x,y,t in layout['positions']:d.text((x,y),t,font=font,fill='#202524')
    mask=Image.new('1',(w,h)); ImageDraw.Draw(mask).polygon([(round(x),round(y)) for x,y in pts],fill=1)
    return box,mask

for n,(src,dialogue) in PAGES.items():
    im=Image.open(ROOT/src).convert('RGBA')
    if n in (1,2): old.board(im,n)
    if n==4: old.notebook(im,4)
    # 03 has a different source size; use a brief hand-written note at the book's left page.
    if n==3:
        d=ImageDraw.Draw(im); old.mixed(d,414,915,'λ > 0',12,color='#464646')
    if n in (6,7):old.schedule(im,n)
    boxes=[]; masks=[]
    for c,t,lines in dialogue:
        box,mask=bubble(im,c,t,lines,tail_length=25 if n==1 else 45)
        for other in masks:
            if ImageChops.logical_and(mask,other).getbbox():raise ValueError(f'page {n}: balloon outlines overlap')
        masks.append(mask)
        for a in boxes:
            if box[0]<a[2] and a[0]<box[2] and box[1]<a[3] and a[1]<box[3]:raise ValueError(f'page {n} bubble overlap {a} {box}')
        boxes.append(box)
    im.convert('RGB').save(OUT/f'{n:02}.png',optimize=True)
    print(n,boxes)
