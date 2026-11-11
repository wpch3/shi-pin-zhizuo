from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import fitz

root = Path(__file__).resolve().parents[1]
out = root/'deliverables/新人物设定试案v1'
out.mkdir(parents=True, exist_ok=True)
reg = str(root/'assets/fonts/NotoSansCJKsc-Regular.otf')
bold = str(root/'assets/fonts/NotoSansCJKsc-Bold.otf')
F=lambda s:ImageFont.truetype(reg,s)
B=lambda s:ImageFont.truetype(bold,s)
cards=[
('01_妹妹的好友','妹妹的好友','安静猫系 · 校园好友', 'art/角色形象区/妹妹好友_参考与候选/新同学_体型优化试案.png',(315,35,710,1024), [
('已定方向','辰希的好朋友。娇小、蓝黑长发；有病弱感与猫系气质，但不是猫娘。校服与辰希相同。'),
('性格提案','安静慢热、细心敏锐；熟悉后会吐槽，也会主动说出自己的想法。累时愿意休息和求助。'),
('生活提案','喜欢手账和画解题小图。她与辰希互相启发：一个擅长找思路，一个擅长把步骤画清楚。'),
('与哥哥','先通过辰希相识；因被耐心倾听与平等对待而产生欣赏，渐渐期待与可靠的哥哥见面。')]),
('02_隔壁姐姐','隔壁姐姐','初一 · 安静的创作者', 'art/角色形象区/新人物设定试案v1/隔壁姐姐_橙发.png',(500,0,875,768), [
('已定方向','刚上初中；与妹妹同为暖橙棕发。表面高冷、内心脑补丰富，隐藏人气VTuber。'),
('性格提案','不擅长主动开口，却很细心；喜欢设计形象和服装，对熟悉的创作认真而有主见。'),
('姐妹互动','愿意为妹妹的活动出服装点子；偶尔脑补过度，也会自己冷静下来重新判断。'),
('与哥哥','欣赏他做事可靠、尊重别人隐私，把他视为让人安心的邻家哥哥。')]),
('03_隔壁妹妹','隔壁妹妹','小学四年级 · 爱挑战的小选手','art/角色形象区/新人物设定试案v1/隔壁妹妹_橙发.png',(500,0,875,768), [
('已定方向','与姐姐同为暖橙棕发；日常、Cos与花滑原图是同一人。活泼、略带傲娇。'),
('性格提案','不服输，也愿意反复练习；小恶作剧有分寸，犯错时能道歉，是有孩子气的行动派。'),
('姐妹互动','喜欢花滑和Cos，也会给姐姐的创作提建议、帮忙收拾材料。'),
('与哥哥','喜欢这位愿意陪玩、为她加油的邻家大哥哥，开心时会主动分享新学会的本领。')]),
('04_小姨','小姨','时髦直率 · 小满的小姨','art/角色形象区/新人物设定试案v1/小姨.png',(500,0,875,768), [
('已定关系','大哥妻子的妹妹，也就是小满的小姨；不是江家妈妈的妹妹。'),
('性格提案','外向、爱开玩笑，也很会看气氛；遇到别人不愿说的事，会主动收住。'),
('生活提案','打扮利落，方向感却不太好；愿意自己准备路线卡。她也有自己的长处，不总等别人帮忙。'),
('与星野','因家人相处逐渐熟悉，欣赏他的耐心与行动力；她也主动用自己的能力帮助他。')])]
paths=[]
for fname,title,sub,image,crop,sections in cards:
    canvas=Image.new('RGB',(1600,1200),'#faf6ec'); d=ImageDraw.Draw(canvas)
    d.rounded_rectangle((30,30,1570,1170),radius=28,fill='#fffdf7',outline='#dad4c6',width=3)
    d.text((65,52),'人物设定  /  讨论试案',font=B(27),fill='#87949b')
    d.text((65,100),title,font=B(59),fill='#303c49')
    d.text((68,185),sub,font=F(28),fill='#73818b')
    d.line((65,233,1535,233),fill='#d5dcd9',width=2)
    im=Image.open(root/image).convert('RGB').crop(crop)
    im.thumbnail((510,850),Image.Resampling.LANCZOS)
    canvas.paste(im,(70+(510-im.width)//2,280+(850-im.height)//2))
    d.line((620,276,620,1110),fill='#e8e3d9',width=2)
    y=280
    for label,body in sections:
        d.text((680,y),label,font=B(30),fill='#7d8f95'); y+=49
        # wrap by actual glyph width
        current=''
        for ch in body:
            if d.textlength(current+ch,font=F(29))>800 and ch not in '，。！？；：、）】》':
                d.text((680,y),current,font=F(29),fill='#39444a');y+=47;current=ch
            else: current+=ch
        if current: d.text((680,y),current,font=F(29),fill='#39444a');y+=47
        y+=30
    assert y < 1110,(fname,y)
    d.text((680,1115),'设定细节为提案  ·  姓名与剧情待确认',font=F(23),fill='#89928f')
    p=out/(fname+'.png');canvas.save(p,optimize=True);paths.append(p)
doc=fitz.open()
for p in paths:
    page=doc.new_page(width=800,height=600)
    page.insert_image(page.rect,filename=str(p))
doc.save(str(out/'四位新人物_设定试案v1.pdf'),deflate=True)
doc.close()
