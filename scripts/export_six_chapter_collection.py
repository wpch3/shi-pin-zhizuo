"""Export the selected reading versions, without modifying historical masters.

Default: full-size JPEG q=96 4:4:4 and up to 720x960 JPEG q=90 4:4:4.
Use --lossless-to DIR for optional PNG/Flate archive PDFs outside the collection.
The Markdown files link to the original full-resolution PNGs already in the repo.
"""
from pathlib import Path
import argparse, io, os, re, sys
import pymupdf
from PIL import Image
from pdf_export import save_lossless_pdf_from_paths

ROOT = Path(__file__).resolve().parents[1]
D = ROOT/'deliverables'
COLLECTION = D/'分格式阅读区'
SOURCES = [
 ('第一话','review-chapters-01-02/逐页看图.md',8,'用户已确认；末页“妈妈：”修正。'),
 ('第二话','review-chapter-02-redraw-v2/逐页看图.md',8,'用户已确认全新重绘v2。'),
 ('第三话','review-chapter-03-user-feedback-v2/第三话_用户反馈返修试排.md',12,'用户已确认反馈返修v2，08、10、11为返修版。'),
 ('第四话','第四话_逐页看图.md',10,'现有成品，第一页称呼已改为“小叔”。'),
 ('第五话','review-chapter-05-home-titled/第五话_逐页检查版.md',18,'用户已确认正文与标题。'),
 ('第六话','review-chapter-06-aquarium-user-gesture-v16/第六话_逐页检查版.md',10,'末页双挽动作获用户确认；第03页说话人标注及整话尚未获用户最终确认。'),
]

def pages_from_md(relative,count):
    src=D/relative; text=src.read_text(encoding='utf-8')
    names=re.findall(r'!\[[^]]*\]\(([^)]+)\)',text)[:count]
    paths=[(src.parent/n).resolve() for n in names]
    if len(paths)!=count or not all(p.is_file() and p.is_relative_to(ROOT) for p in paths):
        raise ValueError(f'页数或链接异常: {src}')
    return paths

def make_pdf(paths, dest, title, light):
    doc=pymupdf.open()
    for path in paths:
        with Image.open(path) as img:
            im=img.convert('RGB')
            if light: im.thumbnail((720,960), Image.Resampling.LANCZOS)
            b=io.BytesIO(); im.save(b,format='JPEG',quality=90 if light else 96,subsampling=0,optimize=True)
            page=doc.new_page(width=691.2,height=921.6);page.insert_image(page.rect,stream=b.getvalue())
    doc.set_metadata({'title':title,'subject':'长宽不超过720x960 JPEG q90 4:4:4' if light else '原尺寸 JPEG q96 4:4:4；无损母版为原PNG'})
    dest.parent.mkdir(parents=True,exist_ok=True)
    temp=dest.with_suffix('.tmp.pdf');doc.save(temp,deflate=True,garbage=4);doc.close();temp.replace(dest)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--lossless-to',type=Path);args=parser.parse_args()
    for folder in ('PDF完整版','PDF轻量版','Markdown完整版'): (COLLECTION/folder).mkdir(parents=True,exist_ok=True)
    index=['# 分格式阅读区','','三个文件区各按话数命名；历史制作文件及 PNG 母版保留原处，未迁移或覆盖。','','- 第一至六话的PDF完整版：原尺寸 JPEG q96、4:4:4；不是无损，请从 Markdown 中的原PNG查看无损细节。','- PDF轻量版：不超过720×960（保持比例），JPEG q90、4:4:4，方便预览。','- Markdown完整版：全话封面和正文逐页内嵌原尺寸 PNG；须保留本仓库相对路径。','- 为控制 Git 交付体积，完整版PDF亦经高质量 JPEG 编码；可用脚本 `--lossless-to 目录` 从相同PNG生成 PNG/Flate 无损归档 PDF。','','| 话数 | 完整版 PDF | 轻量 PDF | 完整 Markdown | 版本状态 |','| --- | --- | --- | --- | --- |']
    for name,src,count,status in SOURCES:
        paths=pages_from_md(src,count)
        if args.lossless_to:
            args.lossless_to.mkdir(parents=True,exist_ok=True)
            save_lossless_pdf_from_paths(paths,args.lossless_to/f'{name}_无损归档.pdf')
            continue
        full=COLLECTION/'PDF完整版'/f'{name}_完整版.pdf';light=COLLECTION/'PDF轻量版'/f'{name}_轻量版.pdf';md=COLLECTION/'Markdown完整版'/f'{name}_完整版.md'
        make_pdf(paths,full,name+' 完整版',False);make_pdf(paths,light,name+' 轻量预览',True)
        text=[f'# {name}｜完整版','','> '+status,'> 本文依次内嵌所有封面与正文PNG母版；PDF仅为阅读导出，不改变原画或排字。','']
        for i,p in enumerate(paths):
            label='封面' if i==0 else f'第{i:02}页'; link=os.path.relpath(p,md.parent).replace(os.sep,'/')
            text += [f'## {label}','',f'![{label}]({link})','']
        md.write_text('\n'.join(text),encoding='utf-8')
        for pdf in (full,light):
            with pymupdf.open(pdf) as document:
                if len(document)!=count: raise ValueError(f'PDF页数异常: {pdf}')
        index.append(f'| {name} | [完整版](PDF完整版/{full.name}) | [轻量版](PDF轻量版/{light.name}) | [完整版](Markdown完整版/{md.name}) | {status} |')
        print(name,count,round(full.stat().st_size/1048576,2),round(light.stat().st_size/1048576,2),flush=True)
    if not args.lossless_to:
        seventh = ['PDF完整版/第七话_试排v4_完整版.pdf', 'PDF轻量版/第七话_试排v4_轻量版.pdf', 'Markdown完整版/第七话_试排v4_完整版.md']
        if all((COLLECTION/p).is_file() for p in seventh):
            index.append(f'| 第七话（试排v4） | [完整版]({seventh[0]}) | [轻量版]({seventh[1]}) | [完整版]({seventh[2]}) | 待用户验收，完整版为无损PDF；第06页画幅较窄。 |')
        latest = ['PDF完整版/第七话_试排v5_完整版.pdf', 'PDF轻量版/第七话_试排v5_轻量版.pdf', 'Markdown完整版/第七话_试排v5_完整版.md']
        if all((COLLECTION/p).is_file() for p in latest):
            index.append(f'| 第七话（反馈返修试排v5） | [完整版]({latest[0]}) | [轻量版]({latest[1]}) | [完整版]({latest[2]}) | 本轮反馈返修，待用户确认；完整版无损。 |')
        index += ['', '后续新话完成后也按三个文件区分别存放；按版本状态区分候选和已确认成果，不覆盖旧版。']
        (COLLECTION/'README.md').write_text('\n'.join(index)+'\n',encoding='utf-8')
if __name__=='__main__': main()
