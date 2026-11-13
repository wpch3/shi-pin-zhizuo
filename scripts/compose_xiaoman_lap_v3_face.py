"""将生图候选的小满表情局部合入用户所选原图；不覆盖原图。"""
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFilter
r=Path(__file__).resolve().parents[1]
a=Image.open(r/'art/xiaoman-lap-short-v2/04-turn-new-view.png').convert('RGB')
b=Image.open(r/'art/xiaoman-lap-short-v3/04-gentle-generated.png').convert('RGB')
assert a.size==b.size==(896,1200)
mask=Image.new('L',a.size,0);d=ImageDraw.Draw(mask);d.rounded_rectangle((226,379,308,454),radius=13,fill=255);mask=mask.filter(ImageFilter.GaussianBlur(3))
out=Image.composite(b,a,mask);bbox=ImageChops.difference(a,out).getbbox();assert bbox==(220,373,315,460),bbox
out.save(r/'art/xiaoman-lap-short-v3/04-gentle-face-only.png')
print('局部差异 bbox:',bbox)
