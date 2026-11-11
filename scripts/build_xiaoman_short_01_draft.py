"""Two-image experimental short; original illustrations kept intact."""
from pathlib import Path
import io, os, sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text
if sys.argv[1:] != ['--draft']:
    raise SystemExit('Only --draft is allowed')
r=Path(__file__).resolve().parents[1]
out=r/'deliverables/review-xiaoman-short-01'; (out/'pages').mkdir(parents=True,exist_ok=True)
images=[]
for n in (1,2):
    p=r/f'art/xiaoman-short-01/scene-0{n}-v1.png'
    with Image.open(p) as img:
        assert img.size==(896,1200),img.size
        im=img.convert('RGB').resize((1440,1920),Image.Resampling.LANCZOS)
    if n==2:
        d=ImageDraw.Draw(im); font=ImageFont.truetype(str(r/'assets/fonts/NotoSansCJKsc-Bold.otf'),34)
        center=(260,950); lines=['等小叔睡醒，','我再讲给他听。']
        lay=measure_speech_text(d,lines,center,font,34)
        shape=oval_speech(center,lay['bubble_size'],(880,970),tail_length=38,tail_width=28,bend=2)
        d.polygon(shape,fill='#F8F4EB');d.line(shape+[shape[0]],fill='#292B2C',width=3,joint='curve')
        for x,y,text in lay['positions']:d.text((x,y),text,font=font,fill='#292B2C')
        print('bubble box',lay['box'])
    dest=out/'pages'/f'page-0{n}.png';im.save(dest,optimize=True);images.append(dest)
md=['# 小满两图短篇｜等小叔睡醒（试排）','','> 独立小短篇，非第八话；普通画风非Q版。第1张无对白，第2张小满轻声说话；文字和成图待用户确认。','','## 第1张','','![小满画画](pages/page-01.png)','','## 第2张','','![小满等小叔](pages/page-02.png)','']
(out/'逐页看图.md').write_text('\n'.join(md))
pdf=pymupdf.open()
for p in images:
    with Image.open(p) as im: preview=im.convert('RGB').resize((720,960),Image.Resampling.LANCZOS)
    buf=io.BytesIO();preview.save(buf,'JPEG',quality=90,subsampling=0,optimize=True)
    page=pdf.new_page(width=691.2,height=921.6);page.insert_image(page.rect,stream=buf.getvalue())
pdf.set_metadata({'title':'小满两图短篇 试排'});pdf.save(out/'小满两图短篇_轻量试排.pdf',garbage=4,deflate=True);pdf.close()
