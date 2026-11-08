"""无损 PDF 导出：直接嵌入 PNG/Flate，避免 JPEG 二次压缩细线与小字。"""
from __future__ import annotations

import io
from pathlib import Path

import pymupdf
from PIL import Image


def save_lossless_pdf(images, path: Path, resolution: int = 150) -> None:
    """按给定 DPI 将 PIL 图像逐页无损嵌入 PDF。"""
    doc = pymupdf.open()
    try:
        for im in images:
            im = im.convert('RGB')
            w, h = im.size
            rect = pymupdf.Rect(0, 0, w / resolution * 72, h / resolution * 72)
            page = doc.new_page(width=rect.width, height=rect.height)
            buf = io.BytesIO()
            im.save(buf, format='PNG', optimize=True)
            page.insert_image(rect, stream=buf.getvalue(), keep_proportion=False)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        doc.save(path, garbage=4, deflate=True)
    finally:
        doc.close()
