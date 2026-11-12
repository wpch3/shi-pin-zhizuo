"""Align the complete illustrated girls to the adult's lower waist on one baseline.
This is a proportional composition, not a redraw: no body part is separately scaled.
"""
from pathlib import Path
import cv2
import numpy as np
from PIL import Image,ImageDraw
r=Path(__file__).resolve().parents[1]; d=r/'art/角色形象区/邻居姐妹_比例重设v4'; src=Image.open(d/'三人比例统一画风候选02.png').convert('RGB')
# Original is a single AI illustration. Cut-outs crop the already aligned adult and girls.
boxes=[(30,65,370,1085),(395,495,590,1085),(640,525,870,1085)]
def cut(box):
 im=src.crop(box); a=np.asarray(im).astype('int16'); b=np.array([250,246,233]);
 dist=np.max(np.abs(a-b),axis=2)
 bg=((dist<30)&(a[:,:,0]>220)&(a[:,:,1]>216)&(a[:,:,2]>198)).astype('uint8')
 cv2.floodFill(bg,None,(0,0),2); fg=(bg!=2).astype('uint8')*255
 n,labels,stats,_=cv2.connectedComponentsWithStats(fg,8); i=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]);fg=(labels==i).astype('uint8')*255
 fg=cv2.GaussianBlur(fg,(3,3),0.5);im=im.convert('RGBA');im.putalpha(Image.fromarray(fg));bounds=im.getchannel('A').getbbox();return im.crop(bounds)
# Same canvas, same adult size, shrink each entire girl uniformly, align all shoes.
out=Image.new('RGBA',src.size,(249,245,234,255));draw=ImageDraw.Draw(out); draw.line((65,1072,860,1072), fill=(210,203,190,255),width=1)
for box,height,x in zip(boxes,(None,452,435),(202,492,752)):
 im=cut(box)
 if height:
  im=im.resize((round(im.width*height/im.height),height),Image.Resampling.LANCZOS)
 out.alpha_composite(im,(round(x-im.width/2),1072-im.height))
out.convert('RGB').save(d/'三人比例对照_统一风格等比合成.png',optimize=True)
print('Final is a uniform full-person composite; source unchanged; baseline 1072, head tops sister 620 / younger 637')
