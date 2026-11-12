"""Archive the v6 review in the three reading areas; never call it approved."""
from pathlib import Path
import os,re,shutil
import pymupdf
from PIL import Image, ImageChops
root=Path(__file__).resolve().parents[1]; collection=root/'deliverables/分格式阅读区'; source=root/'deliverables/章节/第七话/review-chapter-07-user-feedback-v6'; md=source/'第七话_返修试排.md'
paths=[(md.parent/p).resolve() for p in re.findall(r'!\[[^]]*\]\(([^)]+)\)',md.read_text())]
if len(paths)!=8 or not all(p.is_file() for p in paths): raise ValueError('第七话页数/图源异常')
full=collection/'PDF完整版/第七话_试排v6_完整版.pdf'; light=collection/'PDF轻量版/第七话_试排v6_轻量版.pdf'; gallery=collection/'Markdown完整版/第七话_试排v6_完整版.md'
pdf=pymupdf.open()
for p in paths:
 with Image.open(p) as im: w,h=im.size
 page=pdf.new_page(width=691.2,height=691.2*h/w);page.insert_image(page.rect,stream=p.read_bytes())
pdf.set_metadata({'title':'第七话 试排v6 全尺寸无损（未验收）'});tmp=full.with_suffix('.tmp.pdf');pdf.save(tmp,deflate=True,garbage=4);pdf.close();tmp.replace(full)
shutil.copy2(source/'第七话_返修轻量试排.pdf',light)
lines=['# 第七话｜完整版试排 v6（尚未验收）','','> 封面＋七页。第07页妈妈对白按用户原句改为“这些孩子真是的...”，其余沿用v5；标题、纸条及整话仍待确认。','']
for i,p in enumerate(paths):
 label='封面' if i==0 else f'第{i:02}页'; lines += ['## '+label,'',f'![{label}]({os.path.relpath(p,gallery.parent)})','']
gallery.write_text('\n'.join(lines),encoding='utf8')
# Compare the actual PNG-to-PDF image pixels, not merely sizes.
with pymupdf.open(full) as doc:
 assert len(doc)==len(paths)
 for page,p in zip(doc,paths):
  images=page.get_images(full=True); assert len(images)==1
  pix=pymupdf.Pixmap(doc,images[0][0]); expected=Image.open(p).convert('RGB')
  if pix.n!=3: pix=pymupdf.Pixmap(pymupdf.csRGB,pix)
  actual=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
  assert expected.size==actual.size and ImageChops.difference(expected,actual).getbbox() is None, p
with pymupdf.open(light) as doc: assert len(doc)==8
print('PDF embedded pixels equal 8 source images; pdf sizes MiB',round(full.stat().st_size/1048576,2),round(light.stat().st_size/1048576,2))
