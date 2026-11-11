"""第八话紧凑初版：10幅原画＋确定性叠字。仅供剧情/画面审阅，不是正式定稿。"""
from pathlib import Path
import io, sys
import fitz
from PIL import Image, ImageDraw, ImageFont
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text

if sys.argv[1:] != ['--draft']: raise SystemExit('Only --draft')
root=Path(__file__).resolve().parents[1]
source=root/'art/chapter-08-v1'; out=root/'deliverables/review-chapter-08-v1'; pages=out/'pages'; pages.mkdir(parents=True,exist_ok=True)
fontpath=root/'assets/fonts/NotoSansCJKsc-Bold.otf'
font=lambda size: ImageFont.truetype(str(fontpath),size)
# Ordered left-to-right / top-to-bottom. Explicit named speakers avoid ambiguous tails.
plans={
 1:[((670,100),(750,405),['老师：这道题，','谁有思路？'],23),((235,120),(430,390),['辰希：用恒等式','变形，答案是十八。'],23)],
 2:[((665,100),(580,500),['好友：这道同类题','我自己做出来了！'],23),((220,170),(330,445),['辰希：答案对了，','你的图解也很清楚。'],23)],
 3:[((210,119),(450,350),['会长：三个社团轮流','使用教室，各十分钟，','十二点十分开始。'],22),((665,119),(770,810),['委员：音乐社要在','十二点半前结束，绘画社','十二点二十后才到。'],21)],
 4:[((210,114),(220,400),['辰希：音乐先、绘画','其次、手工最后，','每个社团十分钟。'],22),((668,117),(230,650),['好友：我来画图标，','大家看表就更清楚了。'],22)],
 5:[((675,100),(655,430),['男同学：放学后，','一起去买饮料吗？'],23),((215,165),(230,580),['辰希：不了，','我要回家。'],23)],
 6:[((675,100),(710,545),['好友：急着回家，','是想见哥哥吧？'],23),((215,165),(310,510),['辰希：嗯，今天','特别想他。'],23),((330,305),(310,500),['心想：好想快点','回去抱抱二哥……'],22)],
 7:[((215,112),(365,480),['辰希发消息：','二哥，你今天在家吗？'],23),((670,112),(365,480),['哥哥回复：在家。','路上慢点，等你回来。'],23),((672,270),(575,550),['好友：明天见，','路上小心。'],22)],
 8:[((680,85),(650,280),['哥哥：回来了？'],24),((250,170),(370,520),['辰希：二哥！'],24)],
 9:[((210,105),(360,410),['辰希：我今天一直想你，','好想快点回来抱抱你。'],23),((672,108),(520,285),['哥哥：那就','多抱一会儿。'],24),((200,255),(360,410),['辰希：我还和朋友','在学生会安排了活动！'],22),((694,255),(520,285),['哥哥：真厉害，','等会儿讲给我听。'],22)]}

def bubble(d, center, target, lines, size):
    f=font(size); layout=measure_speech_text(d,lines,center,f,size)
    x0,y0,x1,y1=layout['box']; assert x0>=6 and y0>=6 and x1<=890 and y1<=1194,(layout['box'],lines)
    shape=oval_speech(center,layout['bubble_size'],target,tail_length=23,tail_width=17,bend=1)
    d.polygon(shape,fill='#fffdf6'); d.line(shape+[shape[0]],fill='#34383a',width=2,joint='curve')
    for x,y,text in layout['positions']: d.text((x,y),text,font=f,fill='#242a2c')
    return layout['box']

def overlaps(a,b): return a[0]<b[2] and b[0]<a[2] and a[1]<b[3] and b[1]<a[3]
images=[]
for i in range(10):
    src=source/('cover.png' if i==0 else f'scene-{i:02d}.png')
    im=Image.open(src).convert('RGB'); assert im.size==(896,1200)
    d=ImageDraw.Draw(im)
    if i==0:
        # Candidate title, not a finalized title. No painted panel or fake text.
        d.text((32,40),'妹妹的学校日常',font=font(52),fill='#fff9dd',stroke_width=5,stroke_fill='#9e702e')
        d.text((34,1120),'第八话 · 试排',font=font(22),fill='#fffdf6',stroke_width=3,stroke_fill='#67594c')
    else:
        boxes=[]
        for center,target,lines,size in plans[i]:
            box=bubble(d,center,target,lines,size)
            assert not any(overlaps(box,b) for b in boxes),(i,lines,boxes,box)
            boxes.append(box)
        if i==1:
            # Exact underlying problem in legible horizontal overlay (board only).
            sf=font(20)
            for j,t in enumerate(['x+y+z=6','xy+yz+zx=11','求 x³+y³+z³−3xyz']):
                d.text((22,215+j*29),t,font=sf,fill='#f7f6e8',stroke_width=0)
        d.rounded_rectangle((842,1142,886,1191),radius=10,fill='#fffaf0',outline='#a09a8a',width=1)
        s=str(i); bb=d.textbbox((0,0),s,font=font(22)); d.text((864-(bb[2]-bb[0])/2,1148),s,font=font(22),fill='#4f5656')
    dest=pages/f'page-{i:02d}.png';im.save(dest,optimize=True);images.append(dest)

md=['# 第八话｜妹妹的学校日常（紧凑初版试排）','','> 封面标题为候选；为先看全话节奏，将v4草案压缩为封面＋9页。画面、对白及衔接均待用户审阅，非定稿。已知事项见复查记录。','', '[人物和剧情来源](../../docs/第八话_妹妹学校日常_剧情草案v4.md) · [四页人物设定](../新人物设定试案v1/逐页看图.md) · [复查记录](../../docs/第八话_初版试排复查.md)','','## 封面','', '![封面](pages/page-00.png)','']
titles=['课堂解题','好友的笔记','学生会开会','一起安排','冷淡拒绝','想念哥哥','放学后','回到家','想了一天的拥抱']
for i,t in enumerate(titles,1):md.extend([f'## 第{i:02d}页｜{t}','','![第'+str(i)+'页](pages/page-'+f'{i:02d}'+'.png)','',''])
(out/'逐页看图.md').write_text('\n'.join(md).rstrip()+'\n',encoding='utf8')
for lossless in (True,False):
    doc=fitz.open()
    for p in images:
        page=doc.new_page(width=672,height=900)
        if lossless: page.insert_image(page.rect,filename=str(p))
        else:
            img=Image.open(p).convert('RGB');img.thumbnail((672,900),Image.Resampling.LANCZOS)
            buf=io.BytesIO();img.save(buf,'JPEG',quality=90,subsampling=0,optimize=True)
            page.insert_image(page.rect,stream=buf.getvalue())
    doc.set_metadata({'title':'第八话 妹妹的学校日常 初版试排'})
    doc.save(str(out/('第八话_初版试排_无损.pdf' if lossless else '第八话_初版试排_轻量.pdf')),garbage=4,deflate=True);doc.close()
print('Built',len(images),'pages')
