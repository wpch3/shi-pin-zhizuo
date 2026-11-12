"""Three cutouts from existing, user-supplied/accepted portraits, for size comparison.
Uniform scaling and baseline alignment only. Nothing modifies source images.
"""
from pathlib import Path
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw
R=Path(__file__).resolve().parents[1]
O=R/'art/角色形象区/邻居姐妹_比例重设v4'
if sys.argv[1:] not in ([], ['--abdomen']): raise SystemExit('use --abdomen for candidate 02 reference')
sister_height, younger_height = (770, 735) if sys.argv[1:] else (650, 625)
inputs=[
 (R/'art/角色形象区/四位主角_造型v1/second-brother-home.png',(270,55,640,1165),1380,310),
 (R/'art/角色形象区/邻居姐妹_用户选定新参考v1/姐姐_用户原图.png',(325,65,760,1405),sister_height,825),
 (R/'art/角色形象区/邻居姐妹_用户选定新参考v1/妹妹_用户原图.png',(290,105,775,1390),younger_height,1185),
]
# Background-connected near-paper pixels are removed; enclosed whites remain.
def extract(path, crop):
 im=Image.open(path).convert('RGB'); arr=np.asarray(im)
 a=arr.astype(np.int16); bg=np.array([250,246,233]); dist=np.max(np.abs(a-bg),axis=2)
 traversable=((dist < 28) & (a[:,:,0] > 220) & (a[:,:,1] > 216) & (a[:,:,2] > 198)).astype('uint8')
 flood=traversable.copy(); cv2.floodFill(flood,None,(0,0),2)
 foreground=(flood!=2).astype('uint8')*255
 # Remove minor background texture specks unattached to body by retaining largest connected component.
 n,labels,stats,_=cv2.connectedComponentsWithStats(foreground,8)
 keep=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]); foreground=(labels==keep).astype('uint8')*255
 foreground=cv2.GaussianBlur(foreground,(3,3),0.5)
 rgba=im.convert('RGBA');rgba.putalpha(Image.fromarray(foreground));rgba=rgba.crop(crop)
 box=rgba.getchannel('A').getbbox()
 if not box: raise ValueError(path)
 return rgba.crop(box)
canvas=Image.new('RGB',(1500,1600),'#f9f5e9').convert('RGBA')
d=ImageDraw.Draw(canvas);d.line((80,1480,1420,1480), fill='#d3cbbd',width=2)
for path,crop,height,cx in inputs:
 im=extract(path,crop);w,h=im.size; im=im.resize((round(w*height/h),height),Image.Resampling.LANCZOS)
 canvas.alpha_composite(im,(round(cx-im.width/2),1480-height))
name = '三人身高对照_腹部附近参考.png' if sys.argv[1:] else '三人身高对照_原人设等比合成.png'
canvas.convert('RGB').save(O/name,optimize=True)
print(f'built: adult 1380px, sister {sister_height}px, younger {younger_height}px; baseline aligned; no real-world numeric height claim')
