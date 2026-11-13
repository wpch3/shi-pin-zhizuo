"""Re-layout chapter six page 3 with explicit speaker labels; preserve everything else."""
from pathlib import Path
import io, os, sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
from speech_bubble_geometry import oval_speech
from speech_text_layout import measure_speech_text

if sys.argv[1:] != ['--draft']:
    raise SystemExit('仅允许 --draft')
root = Path(__file__).resolve().parents[1]
old = root/'deliverables/章节/第六话/review-chapter-06-aquarium/pages'
out = root/'deliverables/章节/第六话/review-chapter-06-aquarium-dialogue'
pages_dir=out/'pages'; pages_dir.mkdir(parents=True, exist_ok=True)
font_path=root/'assets/fonts/NotoSansCJKsc-Bold.otf'
with Image.open(root/'art/chapter-05-aquarium-v2/shot-03.png') as source:
    if source.size != (896,1200): raise ValueError('源图尺寸异常')
    im=source.convert('RGB').resize((1440,1920),Image.Resampling.LANCZOS)
draw=ImageDraw.Draw(im); font=ImageFont.truetype(str(font_path),29)
boxes=[]
for lines, center, target in [
    (['妹妹：','有两个女人这么喜欢你，','二哥是不是很幸福呀？'], (1145,290), (1150,880)),
    (['姐姐：明明是三个。'], (260,520), (380,780)),
    (['小满：还有小满！'], (1130,700), (840,530)),
]:
    layout=measure_speech_text(draw,lines,center,font,29)
    box=layout['box']
    for prev in boxes:
        if not (box[2] <= prev[0] or prev[2] <= box[0] or box[3] <= prev[1] or prev[3] <= box[1]):
            raise ValueError(f'气泡重叠: {box} {prev}')
    boxes.append(box)
    shape=oval_speech(center,layout['bubble_size'],target,tail_length=30,tail_width=28,bend=2)
    draw.polygon(shape,fill='#F8F4EB'); draw.line(shape+[shape[0]],fill='#292B2C',width=3,joint='curve')
    for x,y,line in layout['positions']: draw.text((x,y),line,font=font,fill='#292B2C')
draw.text((1290,1860),'03 / 09',font=ImageFont.truetype(str(font_path),20),fill='#F8F4EB',stroke_width=2,stroke_fill='#292B2C')
im.save(pages_dir/'page-03.png',optimize=True)
for n in range(10):
    if n==3: continue
    name='page-00-cover.png' if n==0 else f'page-{n:02}.png'
    src=old/name; dst=pages_dir/name
    if not src.is_file(): raise FileNotFoundError(src)
    target=os.path.relpath(src.resolve(),pages_dir)
    if dst.is_symlink():
        if os.readlink(dst)==target: continue
        dst.unlink()
    elif dst.exists(): raise FileExistsError(dst)
    dst.symlink_to(target)
pages=[pages_dir/'page-00-cover.png']+[pages_dir/f'page-{n:02}.png' for n in range(1,10)]
labels=['封面','出发','商量路线','企鹅和肩上骑','海底隧道','四人合影','水母','休息','企鹅玩偶','回家']
lines=['# 第六话｜今天一起去水族馆 · 对白归属调整版','','> 保留第六话封面及剧情；仅重排第03页气泡并标注说话人，原对白不变。请用户确认排版。','> PNG为 1440×1920 排版图（原画896×1200）；轻量PDF供预览。','']
for label,page in zip(labels,pages):
    url=os.path.relpath(page.resolve(),out) if page.is_symlink() else f'pages/{page.name}'
    lines += [f'## {label}','',f'![{label}]({url})','']
(out/'第六话_逐页检查版.md').write_text('\n'.join(lines),encoding='utf8')
doc=pymupdf.open()
for page in pages:
    with Image.open(page) as image:
        if image.size!=(1440,1920): raise ValueError(page)
        thumb=image.convert('RGB').resize((720,960),Image.Resampling.LANCZOS)
        buf=io.BytesIO(); thumb.save(buf,format='JPEG',quality=88,subsampling=0,optimize=True)
    p=doc.new_page(width=691.2,height=921.6); p.insert_image(p.rect,stream=buf.getvalue())
doc.set_metadata({'title':'第六话 今天一起去水族馆 对白归属调整版','subject':'720x960 JPEG quality 88 subsampling 0'})
tmp=out/'preview-tmp.pdf'; doc.save(tmp,deflate=True,garbage=4); doc.close(); tmp.replace(out/'第六话_轻量检查预览.pdf')
print('已生成气泡候选，框:', boxes)
