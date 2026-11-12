#!/usr/bin/env python3
"""Add the approved chapter 7 and 8 reading files without modifying their masters.

Chapter 7 PDFs are byte-for-byte copies of the approved v7 deliverable. Chapter 8
full PDF embeds the v11 PNGs losslessly; its lightweight PDF is the approved v11
JPEG preview, copied byte-for-byte. Markdown links directly to the PNG masters.
"""
from pathlib import Path
import os
import re
import shutil
import sys

import pymupdf
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / 'deliverables'
AREA = D / '分格式阅读区'
sys.path.insert(0, str(ROOT / 'scripts'))
from pdf_export import save_lossless_pdf_from_paths

ITEMS = (
    ('第七话', D / 'review-chapter-07-user-feedback-v7/第七话_返修试排.md', 8,
     D / 'review-chapter-07-user-feedback-v7/第七话_返修完整版.pdf',
     D / 'review-chapter-07-user-feedback-v7/第七话_返修轻量试排.pdf',
     '用户整体确认 v7；封面《一起做晚饭》，第03页为本版，其他正文沿用 v6。'),
    ('第八话', D / 'review-chapter-08-reset-v11/第八话_气泡位置修订预览.md', 19,
     None, D / 'review-chapter-08-reset-v11/第八话_气泡位置修订预览.pdf',
     '用户确认定稿 v11；封面＋18页。'),
)


def pages_from_md(md, count):
    links = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', md.read_text(encoding='utf-8'))
    if len(links) != count:
        raise ValueError(f'{md}: expected {count} images, got {len(links)}')
    paths = [(md.parent / link).resolve() for link in links]
    if not all(p.is_relative_to(ROOT) and p.is_file() for p in paths):
        raise ValueError(f'{md}: missing or unsafe image')
    return paths


def check_full_pdf(pdf, pages):
    """Compare every embedded image's decoded pixels with its master PNG."""
    with pymupdf.open(pdf) as doc:
        if len(doc) != len(pages):
            raise ValueError(f'{pdf}: wrong page count')
        for i, path in enumerate(pages):
            images = doc[i].get_images(full=True)
            if len(images) != 1:
                raise ValueError(f'{pdf} page {i}: expected one image, got {len(images)}')
            pix = pymupdf.Pixmap(doc, images[0][0])
            if pix.alpha or pix.n != 3:
                pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
            actual = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
            with Image.open(path) as source:
                if actual.size != source.size or ImageChops.difference(actual, source.convert('RGB')).getbbox():
                    raise ValueError(f'{pdf} page {i}: pixels differ from {path}')


def main():
    for name, md_src, count, full_src, light_src, status in ITEMS:
        pages = pages_from_md(md_src, count)
        full = AREA / 'PDF完整版' / f'{name}_完整版.pdf'
        light = AREA / 'PDF轻量版' / f'{name}_轻量版.pdf'
        md = AREA / 'Markdown完整版' / f'{name}_完整版.md'
        for p in (full, light, md):
            p.parent.mkdir(parents=True, exist_ok=True)
        if full_src:
            shutil.copyfile(full_src, full)
        else:
            save_lossless_pdf_from_paths(pages, full)
        shutil.copyfile(light_src, light)
        check_full_pdf(full, pages)
        with pymupdf.open(light) as doc:
            if len(doc) != count:
                raise ValueError(f'{light}: wrong page count')
        text = [f'# {name}｜完整版', '', f'> {status}',
                '> 原尺寸图片依次引用已确认版本；完整版 PDF 无损，轻量 PDF 为压缩预览。', '']
        for i, p in enumerate(pages):
            label = '封面' if i == 0 else f'第{i:02}页'
            link = os.path.relpath(p, md.parent).replace(os.sep, '/')
            text.extend([f'## {label}', '', f'![{label}]({link})', ''])
        md.write_text('\n'.join(text), encoding='utf-8')
        print(f'{name}: {count} pages, full PDF pixels match PNG masters, light PDF {count} pages')


if __name__ == '__main__':
    main()
