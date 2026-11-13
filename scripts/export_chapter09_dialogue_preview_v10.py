from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io,os
root=Path(__file__).resolve().parent.parent
out=root/'deliverables/章节/第九话/第九话逐页台词预览v10'
new='art/chapter-09-dialogue-preview-v8/'
pages=[
('封面','art/chapter-09-continuation-v5/cover-重画.png',[], '工作封面；标题待定。'),
('01 来访','art/chapter-09-continuation-v6/01-重画.png',['邻居妹妹：我要给 Cos 配件选颜色，你帮我看看！','二哥：好，进来慢慢看。'],'妹妹带来样品；姐姐拿底座。'),
('02 小挑战','art/chapter-09-redesign-v2/02.png',['邻居妹妹：猜猜我喜欢哪一个？猜错可要再陪我选！'],'妹妹举起两色样品，观察二哥反应。'),
('02a 玄关换鞋','art/chapter-09-dialogue-preview-v10/02a-普通脱鞋重画.png',[],'姐妹在玄关脱鞋，二哥等她们进屋。'),
('03 小满参与','art/chapter-09-dialogue-preview-v10/03-补底座.png',['小满：都好看！我也能选吗？','邻居妹妹：可以，但先让他猜！'],'四人在客厅看样品。'),
('04 姐姐说明','art/chapter-09-continuation-v4/04.png',['邻居姐姐：这是装布结的地方，颜色可以换。'],'姐姐指向底座，二哥认真看。'),
('05 争取注意','art/chapter-09-continuation-v5/05.png',['邻居妹妹：还没猜我的呢！先看我嘛。'],'妹妹轻拉袖子，期待二哥注意她。'),
('06 二哥猜颜色','art/chapter-09-continuation-v5/06.png',['二哥：我猜深红。这个颜色很适合你。'],'二哥指着红结，妹妹露出意外表情。'),
('07 嘴硬','art/chapter-09-continuation-v4/07-重画.png',['邻居妹妹：哼，你只是运气好吧！'],'她拿着红结比了一下。'),
('07a 放回桌上',new+'07a-放回红结重画.png',[],'妹妹将红结放回桌上，准备继续比较。'),
('08 姐姐的心思','art/chapter-09-continuation-v4/08.png',['邻居姐姐（心声）：只是在确认配色，别突然紧张。'],'姐姐靠近桌边指向底座。'),
('09 妹妹发现','art/chapter-09-continuation-v5/09.png',['邻居妹妹：姐姐，你刚才怎么不说话了？','邻居姐姐：……在想颜色。','邻居姐姐（心声）：我刚刚是不是反应太明显了？'],'妹妹留意到姐姐的反应。'),
('10 小满的想法','art/chapter-09-dialogue-preview-v10/10-连续站位.png',['小满：深红这个，像小恶魔的蝴蝶结！','邻居姐姐：这个形状确实很合适。'],'小满指着桌上的深红布结。'),
('11 决定','art/chapter-09-correction-v7/11-重画.png',['邻居妹妹：好吧，那就选深红。姐姐做的底座也挺好看的。','二哥：边上的小褶子很用心。','邻居姐姐：嗯。'],'妹妹将红结递给姐姐。'),
('12 准备收拾','art/chapter-09-dialogue-preview-v10/12-不用袋子收拾.png',['邻居妹妹：做好之后你也要第一个看！','二哥：好。','小满：我也想看！'],'姐妹拿着两色布结，准备收好配件。')]
fontpath=root/'assets/fonts/chapter08-handwriting/MaShanZheng-Regular.ttf'
regular=root/'assets/fonts/NotoSansCJKsc-Regular.otf'
F=ImageFont.truetype(str(fontpath),34); small=ImageFont.truetype(str(regular),24); head=ImageFont.truetype(str(regular),29)
md=['# 第九话｜完整逐页图文台词预览 v10','', '工作代称：邻居姐妹的配件小讨论。封面＋12页＋两张过门，共15张。台词在图片下方，角色标注只用于预览；尚未上漫画气泡、未定稿。', '', '画面与对白存在仍需处理的衔接问题，详见[检查记录](检查与待修.md)。','']
images=[]
for i,(title,path,dialogue,note) in enumerate(pages):
 p=root/path; assert p.is_file(), p
 page=Image.new('RGB',(1200,1700),'#faf9f7'); draw=ImageDraw.Draw(page)
 draw.text((65,25),f'第九话 · 台词预览   {title}',font=head,fill='#344354')
 im=Image.open(p).convert('RGB'); im.thumbnail((1030,1245),Image.Resampling.LANCZOS)
 page.paste(im,((1200-im.width)//2,75))
 draw.line((65,1340,1135,1340), fill='#d3d8dc',width=2)
 draw.text((65,1352),note,font=small,fill='#68727b')
 y=1393
 for line in dialogue:
  draw.text((65,y),line,font=F,fill='#202830'); y+=56
 assert y<1645,(title,y)
 draw.text((65,1652),f'{i+1:02d} / {len(pages):02d}   图文对照工作预览 · 非气泡成品',font=small,fill='#77818a')
 buf=io.BytesIO(); page.save(buf,format='JPEG',quality=88); buf.seek(0); images.append(buf)
 rel=os.path.relpath(p,out)
 md += [f'## {title}','',f'![{title}]({rel})','',f'*{note}*','']
 md += [f'- {line}' for line in dialogue] if dialogue else ['（无对白）']
 md += ['']
(out/'第九话_逐页图文台词预览.md').write_text('\n'.join(md),encoding='utf8')
c=canvas.Canvas(str(out/'第九话_逐页图文台词预览.pdf'),pagesize=(600,850)); c.setTitle('Chapter 09 dialogue image preview v10')
for buf in images:
 c.drawImage(ImageReader(buf),0,0,width=600,height=850); c.showPage()
c.save()
print('pages',len(pages))
