"""Three-image experimental short; user-requested blanket sequence, originals retained."""
from pathlib import Path
import io, os, sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text
if sys.argv[1:] != ['--draft']:
    raise SystemExit('Only --draft is allowed')
r=Path(__file__).resolve().parents[1]
out=r/'deliverables/短篇与个人回/小满盖被/review-xiaoman-short-01-blanket-v2'; (out/'pages').mkdir(parents=True,exist_ok=True)
images=[]
for n in (1,2,3):
    p=r/'art/xiaoman-short-01/blanket-v2'/('scene-03-v2.png' if n == 3 else f'scene-0{n}-v1.png')
    with Image.open(p) as img:
        assert img.size==(896,1200),img.size
        im=img.convert('RGB').resize((1440,1920),Image.Resampling.LANCZOS)
    if n==3:
        d=ImageDraw.Draw(im); font=ImageFont.truetype(str(r/'assets/fonts/NotoSansCJKsc-Bold.otf'),34)
        center=(260,950); lines=['等小叔睡醒，','我再讲给他听。']
        lay=measure_speech_text(d,lines,center,font,34)
        shape=oval_speech(center,lay['bubble_size'],(880,970),tail_length=38,tail_width=28,bend=2)
        d.polygon(shape,fill='#F8F4EB');d.line(shape+[shape[0]],fill='#292B2C',width=3,joint='curve')
        for x,y,text in lay['positions']:d.text((x,y),text,font=font,fill='#292B2C')
        print('bubble box',lay['box'])
    dest=out/'pages'/f'page-0{n}.png';im.save(dest,optimize=True);images.append(dest)
md=['# 小满短篇｜等小叔睡醒（三图返修试排）','','> 独立小短篇，非第八话；第1张小满给小叔盖被子，后两张他仍盖着。普通画风、非Q版；台词及整版待用户确认。','','## 第1张：盖被子','','![小满给小叔盖被子](pages/page-01.png)','','## 第2张：画画','','![小满画画](pages/page-02.png)','','## 第3张：等小叔睡醒','','![小满等小叔](pages/page-03.png)','']
(out/'逐页看图.md').write_text('\n'.join(md))
pdf=pymupdf.open()
for p in images:
    with Image.open(p) as im: preview=im.convert('RGB').resize((720,960),Image.Resampling.LANCZOS)
    buf=io.BytesIO();preview.save(buf,'JPEG',quality=90,subsampling=0,optimize=True)
    page=pdf.new_page(width=691.2,height=921.6);page.insert_image(page.rect,stream=buf.getvalue())
pdf.set_metadata({'title':'小满三图短篇 返修试排'});pdf.save(out/'小满三图短篇_轻量试排.pdf',garbage=4,deflate=True);pdf.close()
