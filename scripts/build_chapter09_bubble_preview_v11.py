"""Chapter 9 non-final speech-bubble layout study; preserves all source art."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from speech_bubble_geometry import oval_speech
from pdf_export import _pdf_from_png_streams
import math, json, os
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'deliverables/章节/第九话/第九话气泡试排v11'
D=OUT/'逐页'; D.mkdir(parents=True,exist_ok=True)
# Specs: relative (x,y) centers and tail targets; reading sequence top-to-bottom.
pages=[
('封面','art/chapter-09-continuation-v5/cover-重画.png',[]),
('01','art/chapter-09-continuation-v6/01-重画.png',[
 (['我要给 Cos 配件','选颜色，你帮我看看！'],(.76,.12),(.85,.49),'speech'),
 (['好，进来慢慢看。'],(.38,.30),(.25,.27),'speech')]),
('02','art/chapter-09-redesign-v2/02.png',[
 (['猜猜我喜欢哪一个？','猜错可要再陪我选！'],(.25,.21),(.30,.43),'speech')]),
('02a','art/chapter-09-dialogue-preview-v10/02a-普通脱鞋重画.png',[]),
('03','art/chapter-09-dialogue-preview-v10/03-补底座.png',[
 (['都好看！','我也能选吗？'],(.78,.08),(.60,.43),'speech'),
 (['可以，但先让他猜！'],(.23,.42),(.28,.54),'speech')]),
('04','art/chapter-09-continuation-v4/04.png',[
 (['这是装布结的地方，','颜色可以换。'],(.25,.20),(.34,.42),'speech')]),
('05','art/chapter-09-continuation-v5/05.png',[
 (['还没猜我的呢！','先看我嘛。'],(.62,.10),(.57,.43),'speech')]),
('06','art/chapter-09-continuation-v5/06.png',[
 (['我猜深红。','这个颜色很适合你。'],(.73,.07),(.75,.39),'speech')]),
('07','art/chapter-09-continuation-v4/07-重画.png',[
 (['哼，你只是运气好吧！'],(.26,.22),(.32,.45),'speech')]),
('07a','art/chapter-09-dialogue-preview-v8/07a-放回红结重画.png',[]),
('08','art/chapter-09-continuation-v4/08.png',[
 (['只是在确认配色，','别突然紧张。'],(.77,.18),(.72,.43),'thought')]),
('09','art/chapter-09-continuation-v5/09.png',[
 (['姐姐，你刚才','怎么不说话了？'],(.24,.075),(.29,.43),'speech'),
 (['……在想颜色。'],(.77,.12),(.73,.40),'speech'),
 (['我刚刚是不是','反应太明显了？'],(.75,.205),(.73,.40),'thought')]),
('10','art/chapter-09-dialogue-preview-v10/10-连续站位.png',[
 (['深红这个，像小恶魔','的蝴蝶结！'],(.25,.17),(.25,.67),'speech'),
 (['这个形状','确实很合适。'],(.75,.25),(.72,.43),'speech')]),
('11','art/chapter-09-correction-v7/11-重画.png',[
 (['好吧，那就选深红。','姐姐做的底座','也挺好看的。'],(.78,.10),(.32,.52),'speech'),
 (['边上的小褶子','很用心。'],(.24,.26),(.22,.24),'speech'),
 (['嗯。'],(.90,.29),(.77,.46),'speech')]),
('12','art/chapter-09-dialogue-preview-v10/12-不用袋子收拾.png',[
 (['做好之后你也要','第一个看！'],(.77,.075),(.25,.51),'speech'),
 (['好。'],(.24,.25),(.25,.17),'speech'),
 (['我也想看！'],(.70,.325),(.66,.25),'speech')]),
]
font=ImageFont.truetype(str(ROOT/'assets/fonts/chapter08-handwriting/MaShanZheng-Regular.ttf'),30)
records=[]; pngs=[]; md=['# 第九话｜气泡台词试排 v11','', '基于v10未验收图像的工作试排，非定稿。部分气泡（尤其10–12页）说话归属不清，仍需返修；详见[检查与待修](检查与待修.md)。','']
for idx,(label,src,specs) in enumerate(pages):
 im=Image.open(ROOT/src).convert('RGB'); w=1000; h=round(im.height*w/im.width); im=im.resize((w,h),Image.Resampling.LANCZOS); dr=ImageDraw.Draw(im)
 boxes=[]
 for lines,(cx,cy),(tx,ty),kind in specs:
  cx=int(cx*w);cy=int(cy*h);tx=int(tx*w);ty=int(ty*h)
  bb=[dr.textbbox((0,0),s,font=font) for s in lines]
  bw=max(b[2]-b[0] for b in bb)+80; bh=len(lines)*39+44
  box=(round(cx-bw/2),round(cy-bh/2),round(cx+bw/2),round(cy+bh/2))
  assert box[0]>=5 and box[1]>=5 and box[2]<w-5 and box[3]<h-5,(label,box,w,h)
  for b in boxes: assert box[2]<b[0] or b[2]<box[0] or box[3]<b[1] or b[3]<box[1],(label,box,b)
  boxes.append(box)
  if kind=='speech':
   points=oval_speech((cx,cy),(bw,bh),(tx,ty),tail_length=23,tail_width=22,bend=2)
   dr.polygon(points,fill='white');dr.line(points+[points[0]],fill='#252525',width=3,joint='curve')
  else:
   dr.ellipse(box,fill='#fffefa');rx=bw/2;ry=bh/2
   for j in range(0,120,4):
    angles=[2*math.pi*(j+k)/120 for k in range(3)];pts=[(cx+rx*math.cos(a),cy+ry*math.sin(a)) for a in angles];dr.line(pts,fill='#444444',width=2)
   # Small thought bubbles in direction of character, kept outside the main oval.
   theta=math.atan2((ty-cy)/ry,(tx-cx)/rx); ex=cx+rx*math.cos(theta);ey=cy+ry*math.sin(theta);vx=math.cos(theta);vy=math.sin(theta)
   for dist,r in [(12,5),(26,3)]:
    x=ex+vx*dist;y=ey+vy*dist;dr.ellipse((x-r,y-r,x+r,y+r),fill='white',outline='#444',width=2)
  ink_h=len(lines)*39-7; y=cy-ink_h/2
  for text,bbx in zip(lines,bb):
   width=bbx[2]-bbx[0];dr.text((round(cx-width/2-bbx[0]),round(y-bbx[1])),text,font=font,fill='#171717');y+=39
  records.append({'page':label,'text':' / '.join(lines),'kind':kind,'box':box,'target':(tx,ty)})
 file=D/f'{idx:02d}-{label}.png';im.save(file,optimize=True);pngs.append(file.read_bytes());md.extend([f'## {label}','',f'![{label}](逐页/{file.name})',''])
_pdf_from_png_streams(pngs,OUT/'第九话_气泡台词试排v11_无损.pdf')
(OUT/'逐页看图.md').write_text('\n'.join(md),encoding='utf8')
(OUT/'气泡坐标.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
print('pages',len(pages),'bubbles',len(records),'output',OUT)
