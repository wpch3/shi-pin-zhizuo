#!/usr/bin/env python3
"""Build the image-only, lossy working preview from the integrated Markdown.

Requires Pillow and reportlab. Page images retain their aspect ratios; PDF contains text already typeset into page images, but not Markdown notes. No source image is changed.
"""
from io import BytesIO
from pathlib import Path
import re
from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'deliverables/review-chapter-08-reset-v8'
markdown = (DIR / '第八话_整话新版_对白试排.md').read_text(encoding='utf-8')
paths = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', markdown)
if len(paths) != 19:
    raise SystemExit(f'Expected cover plus 18 images, got {len(paths)}')
out = DIR / '第八话_整话新版_对白试排.pdf'
c = canvas.Canvas(str(out), pageCompression=1)
c.setTitle('Chapter 08 - image-only working preview')
for relative in paths:
    src = (DIR / relative).resolve()
    if not src.is_file() or ROOT not in src.parents:
        raise SystemExit(f'Invalid image: {relative}')
    with Image.open(src) as im:
        rgb = im.convert('RGB')
        width, height = rgb.size
        # Keep each source aspect ratio, so no image is cropped or stretched.
        scale = 720.0 / max(width, height)
        page_w, page_h = width * scale, height * scale
        c.setPageSize((page_w, page_h))
        data = BytesIO()
        rgb.save(data, format='JPEG', quality=85, subsampling=0, optimize=True)
        data.seek(0)
        c.drawImage(ImageReader(data), 0, 0, width=page_w, height=page_h)
        c.showPage()
c.save()
print(f'Wrote {out.relative_to(ROOT)}: {len(paths)} pages')
