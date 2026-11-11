"""A quiet humming-note alternative; preserve both neighbouring pages and the v3 option."""
from pathlib import Path
import io, os, sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
from speech_bubble_geometry import oval_speech
if sys.argv[1:] != ['--draft']:
    raise SystemExit('Only --draft is allowed')
r=Path(__file__).resolve().parents[1]
out=r/'deliverables/review-xiaoman-short-01-humming-v4'; (out/'pages').mkdir(parents=True,exist_ok=True)
v3=r/'deliverables/review-xiaoman-short-01-dialogue-v3/pages/page-01.png'
v2=r/'deliverables/review-xiaoman-short-01-blanket-v2/pages'
with Image.open(v2/'page-02.png') as src: page=src.convert('RGB')
d=ImageDraw.Draw(page);center=(1110,330);shape=oval_speech(center,(118,98),(1020,860),tail_length=35,tail_width=28,bend=2)
d.polygon(shape,fill='#F8F4EB');d.line(shape+[shape[0]],fill='#292B2C',width=3,joint='curve')
f=ImageFont.truetype(str(r/'assets/fonts/NotoSansCJKsc-Bold.otf'),52)
box=d.textbbox((0,0),'♪',font=f);x=center[0]-(box[0]+box[2])/2;y=center[1]-(box[1]+box[3])/2
d.text((round(x),round(y)),'♪',font=f,fill='#292B2C')
page.save(out/'pages/page-02.png',optimize=True)
images=[v3,out/'pages/page-02.png',v2/'page-03.png']
md=['# 小满短篇｜等小叔睡醒（音符试排v4）','','> 第1张保留用户指定的“跟我一起玩”；第2张气泡加一个音符，表示轻声哼歌，是否采用待用户确认。其他画面沿用前版，非第八话。','','## 第1张：盖被子','',f'![小满盖被子]({os.path.relpath(images[0],out)})','','## 第2张：画画','','![小满轻声哼歌画画](pages/page-02.png)','','## 第3张：等小叔睡醒','',f'![小满等小叔]({os.path.relpath(images[2],out)})','']
(out/'逐页看图.md').write_text('\n'.join(md),encoding='utf8')
pdf=pymupdf.open()
for p in images:
    with Image.open(p) as im: preview=im.convert('RGB').resize((720,960),Image.Resampling.LANCZOS)
    buf=io.BytesIO();preview.save(buf,'JPEG',quality=90,subsampling=0,optimize=True)
    pdf.new_page(width=691.2,height=921.6).insert_image(pymupdf.Rect(0,0,691.2,921.6),stream=buf.getvalue())
pdf.set_metadata({'title':'小满三图短篇 音符试排v4'});pdf.save(out/'小满三图短篇_音符试排v4.pdf',garbage=4,deflate=True);pdf.close()
