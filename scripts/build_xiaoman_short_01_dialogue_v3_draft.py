"""Retain v2 artwork and two later pages; place user's proposed line on page one."""
from pathlib import Path
import io, os, sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text
if sys.argv[1:] != ['--draft']:
    raise SystemExit('Only --draft is allowed')
r=Path(__file__).resolve().parents[1]
out=r/'deliverables/短篇与个人回/小满盖被/review-xiaoman-short-01-dialogue-v3'; (out/'pages').mkdir(parents=True,exist_ok=True)
old=r/'deliverables/短篇与个人回/小满盖被/review-xiaoman-short-01-blanket-v2/pages'
with Image.open(old/'page-01.png') as img: page=img.convert('RGB')
d=ImageDraw.Draw(page); font=ImageFont.truetype(str(r/'assets/fonts/NotoSansCJKsc-Bold.otf'),34)
center=(1050,165); lines=['小叔又没盖被子，','感冒了就不能','跟我一起玩了。']
lay=measure_speech_text(d,lines,center,font,34)
shape=oval_speech(center,lay['bubble_size'],(1100,640),tail_length=38,tail_width=28,bend=2)
d.polygon(shape,fill='#F8F4EB');d.line(shape+[shape[0]],fill='#292B2C',width=3,joint='curve')
for x,y,text in lay['positions']: d.text((x,y),text,font=font,fill='#292B2C')
page.save(out/'pages/page-01.png',optimize=True)
print('bubble box',lay['box'])
images=[out/'pages/page-01.png',old/'page-02.png',old/'page-03.png']
md=['# 小满短篇｜等小叔睡醒（三图对白试排v3）','','> 独立短篇，非第八话。第1张加用户提出的对白，后两张沿用盖被子版；成图及台词待用户确认。','','## 第1张：盖被子','','![小满给小叔盖被子](pages/page-01.png)','','## 第2张：画画','','![小满画画]('+os.path.relpath(images[1],out)+')','','## 第3张：等小叔睡醒','','![小满等小叔]('+os.path.relpath(images[2],out)+')','']
(out/'逐页看图.md').write_text('\n'.join(md),encoding='utf8')
pdf=pymupdf.open()
for p in images:
    with Image.open(p) as im: preview=im.convert('RGB').resize((720,960),Image.Resampling.LANCZOS)
    buf=io.BytesIO();preview.save(buf,'JPEG',quality=90,subsampling=0,optimize=True)
    pdf.new_page(width=691.2,height=921.6).insert_image(pymupdf.Rect(0,0,691.2,921.6),stream=buf.getvalue())
pdf.set_metadata({'title':'小满三图短篇 对白试排v3'});pdf.save(out/'小满三图短篇_对白试排v3.pdf',garbage=4,deflate=True);pdf.close()
