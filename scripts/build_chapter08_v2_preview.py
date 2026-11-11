"""第八话v2：复用未改变页，仅重排五张新生画。"""
from pathlib import Path
import io,sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text

if sys.argv[1:] not in (['--draft'], ['--draft','--update-04']): raise SystemExit('Use --draft or --draft --update-04')
update04 = '--update-04' in sys.argv
r=Path(__file__).resolve().parents[1]; out=r/'deliverables/review-chapter-08-v2'; pages=out/'pages';pages.mkdir(parents=True,exist_ok=True)
font=lambda n:ImageFont.truetype(str(r/'assets/fonts/NotoSansCJKsc-Bold.otf'),n)
plans={
3:[((210,115),(550,335),['会长：三个社团轮流','使用教室，各十分钟，','十二点十分开始。'],22),((665,115),(760,550),['委员：音乐社要在','十二点半前结束，绘画社','十二点二十后才到。'],21)],
4:[((195,105),(200,475),['辰希：音乐先、绘画','其次、手工最后，','每个社团十分钟。'],22),((680,100),(580,510),['委员：那我去通知','三个社团！'],22),((355,260),(370,570),['好友：我来画图标，','让大家看得更清楚。'],22)],
8:[((678,85),(680,300),['哥哥：回来了？'],24),((230,175),(360,410),['辰希：二哥！'],24)],
9:[((210,105),(420,445),['辰希：我今天一直想你，','好想快点回来抱抱你。'],23),((675,108),(500,355),['哥哥：那就','多抱一会儿。'],24),((205,250),(420,445),['辰希：我还和朋友','在学生会安排了活动！'],22),((685,250),(500,355),['哥哥：真厉害，','等会儿讲给我听。'],22)],
10:[((225,105),(430,570),['辰希：（轻轻吸气）','二哥，让我再靠一会儿。'],23),((670,105),(530,380),['哥哥：好，','慢慢跟我讲。'],24)]}

def overlaps(a,b):return a[0]<b[2] and b[0]<a[2] and a[1]<b[3] and b[1]<a[3]

def bubble(d,center,target,lines,size):
    f=font(size);lay=measure_speech_text(d,lines,center,f,size); x0,y0,x1,y1=lay['box']
    assert x0>=6 and y0>=6 and x1<=890 and y1<=1194,(center,lines,lay['box'])
    shape=oval_speech(center,lay['bubble_size'],target,tail_length=23,tail_width=17,bend=1)
    d.polygon(shape,fill='#fffdf6');d.line(shape+[shape[0]],fill='#34383a',width=2,joint='curve')
    for x,y,t in lay['positions']:d.text((x,y),t,font=f,fill='#242a2c')
    return lay['box']

for i in plans:
    if update04 and i != 4: continue
    name=f'scene-{i:02d}'+('-v2' if i==10 else '')+'.png'
    im=Image.open(r/'art/chapter-08-v2'/name).convert('RGB');assert im.size==(896,1200)
    d=ImageDraw.Draw(im);boxes=[]
    for c,t,lines,size in plans[i]:
        box=bubble(d,c,t,lines,size);assert not any(overlaps(box,b) for b in boxes),(i,lines,boxes,box);boxes.append(box)
    d.rounded_rectangle((842,1142,886,1191),radius=10,fill='#fffaf0',outline='#a09a8a',width=1)
    s=str(i);bb=d.textbbox((0,0),s,font=font(22));d.text((864-(bb[2]-bb[0])/2,1148),s,font=font(22),fill='#4f5656')
    im.save(pages/f'page-{i:02d}.png',optimize=True)

old=r/'deliverables/review-chapter-08-v1/pages'
paths=[(pages if i in plans else old)/f'page-{i:02d}.png' for i in range(11)]
titles=['封面','课堂解题','好友的笔记','学生会开会','一起安排','冷淡拒绝','想念哥哥','放学后','回到家','想了一天的拥抱','靠在哥哥胸前']
md=['# 第八话｜妹妹的学校日常（试排 v2）','','> 试排，非定稿。保留四人女生学生会；新增两位成员的区别形象，并加入回家后的亲情场景。标题、台词、形象与连续性仍待用户审阅。','', '[本轮复查](../../docs/第八话_v2_学生会与回家场景复查.md) · [新成员设计](../../art/角色形象区/学生会新成员_试案v1/README.md) · [旧版逐页](../review-chapter-08-v1/逐页看图.md)','']
for i,(p,t) in enumerate(zip(paths,titles)):
    rel=p.relative_to(out) if p.is_relative_to(out) else Path('../review-chapter-08-v1/pages')/p.name
    md += [f'## {"封面" if i==0 else f"第{i:02d}页"}｜{t}','','![第'+str(i)+'页]('+rel.as_posix()+')','']
(out/'逐页看图.md').write_text('\n'.join(md).rstrip()+'\n',encoding='utf8')
for lossless in (True,False):
    doc=pymupdf.open()
    for p in paths:
        page=doc.new_page(width=672,height=900)
        if lossless:page.insert_image(page.rect,filename=str(p))
        else:
            im=Image.open(p).convert('RGB');im.thumbnail((672,900),Image.Resampling.LANCZOS)
            buf=io.BytesIO();im.save(buf,'JPEG',quality=90,subsampling=0,optimize=True)
            page.insert_image(page.rect,stream=buf.getvalue())
    doc.set_metadata({'title':'第八话 妹妹的学校日常 试排v2'})
    doc.save(str(out/('第八话_试排v2_无损.pdf' if lossless else '第八话_试排v2_轻量.pdf')),garbage=4,deflate=True);doc.close()
print('v2',len(paths),'pages; changed',sorted(plans))
