"""第三话交付物校验：两份无损定稿 PDF + 轻量预览 PDF + PNG 图片版 ZIP + 网页看图页。

检查项：
- 两份正式 PDF 各 12 页、页面物理尺寸正确、全 /FlateDecode、逐页 150dpi 回读对 PNG 母版 max_pixel_diff=0；
- 轻量预览 PDF 12 页、页面物理尺寸与阅读版一致、图像为 DCTDecode(JPEG)、不大于 5MB；
- ZIP 12 张、逐张字节与正式 PNG 完全相同；
- 看图页 12 个相对路径全部指向存在的文件。

用法：.venv/bin/python scripts/verify_chapter03_pdf.py
"""
from pathlib import Path
import hashlib
import tempfile
import zipfile

import numpy as np
import pymupdf
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / 'deliverables'
OUTPUT = D / '章节/第三话/原交付'
PAGES = sorted((D / '章节/第三话/历史图源/full-v4').glob('page-*.png'))
VERT = sorted((D / '章节/第三话/历史图源/full-v4-vertical').glob('page-*.png'))
LOSSLESS = [
    (OUTPUT / '第三话_妹妹的休息日.pdf', PAGES, 691.2, 921.6),
    (OUTPUT / '第三话_竖屏全页漫画.pdf', VERT, 691.2, 1030.08),
]
PREVIEW = OUTPUT / '第三话_轻量在线预览.pdf'
ZIP = OUTPUT / '第三话_12页PNG图片版.zip'
GALLERY = OUTPUT / '第三话_逐页看图.md'


def check_lossless(pdf_path, pngs, expected_w, expected_h):
    doc = pymupdf.open(pdf_path)
    assert len(doc) == 12, f'{pdf_path.name}: {len(doc)} 页'
    filters = set()
    diffs = []
    for i, page in enumerate(doc):
        r = page.rect
        assert abs(r.width - expected_w) < 0.2 and abs(r.height - expected_h) < 0.2, \
            f'{pdf_path.name} p{i}: {r.width}x{r.height}'
        for info in page.get_images(full=True):
            xref = info[0]
            f = doc.xref_get_key(xref, 'Filter')[1]
            filters.add(f)
            smask = doc.xref_get_key(xref, 'SMask')[1]
            assert smask == 'null', f'{pdf_path.name} p{i} 带透明遮罩'
        pix = page.get_pixmap(dpi=150, alpha=False)
        rendered = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        master = Image.open(pngs[i]).convert('RGB')
        assert rendered.size == master.size, f'{pdf_path.name} p{i}: {rendered.size} vs {master.size}'
        diffs.append(int(np.abs(np.asarray(rendered, dtype=np.int16)
                               - np.asarray(master, dtype=np.int16)).max()))
    assert filters == {'/FlateDecode'}, f'{pdf_path.name} 过滤器异常: {filters}'
    assert max(diffs) == 0, f'{pdf_path.name} 非逐像素无损: {diffs}'
    doc.close()
    print(f'[OK] {pdf_path.name}: 12页, {expected_w}x{expected_h}pt, 全 FlateDecode, '
          f'150dpi max_pixel_diff={max(diffs)}, {pdf_path.stat().st_size/1024/1024:.1f}MB')


def check_preview():
    assert PREVIEW.stat().st_size < 5 * 1024 * 1024, '轻量预览 PDF 超过 5MB'
    doc = pymupdf.open(PREVIEW)
    assert len(doc) == 12, f'轻量预览 {len(doc)} 页'
    filters = set()
    for i, page in enumerate(doc):
        assert abs(page.rect.width - 691.2) < 0.2 and abs(page.rect.height - 921.6) < 0.2
        for info in page.get_images(full=True):
            filters.add(doc.xref_get_key(info[0], 'Filter')[1])
    assert filters == {'/DCTDecode'}, f'轻量预览过滤器异常: {filters}'
    # 渲染回读一页供人眼放大复检（JPEG 有损，只查可读性与页数，不查像素相等）
    pix = doc[4].get_pixmap(dpi=150, alpha=False)
    preview_dir = Path(tempfile.gettempdir()) / 'shi-pin-zhizuo-preview'
    preview_dir.mkdir(parents=True, exist_ok=True)
    Image.frombytes('RGB', (pix.width, pix.height), pix.samples).save(preview_dir / 'light-preview-page04.png')
    doc.close()
    print(f'[OK] {PREVIEW.name}: 12页, 691.2x921.6pt, DCTDecode(JPEG q=88), '
          f'{PREVIEW.stat().st_size/1024/1024:.2f}MB, 已导出第4页供放大目检')


def check_zip_and_gallery():
    with zipfile.ZipFile(ZIP) as zf:
        names = zf.namelist()
        assert len(names) == 12, f'ZIP 内 {len(names)} 张'
        for i, (name, path) in enumerate(zip(names, PAGES)):
            assert zf.read(name) == path.read_bytes(), f'ZIP 第{i+1}张与 PNG 母版不一致: {name}'
    print(f'[OK] {ZIP.name}: 12张，逐张字节等同 1440x1920 PNG 母版')
    text = GALLERY.read_text(encoding='utf-8')
    links = [ln.split('](')[1].rstrip(')') for ln in text.splitlines() if ln.startswith('![')]
    assert len(links) == 12, f'看图页 {len(links)} 张图'
    for rel in links:
        assert (GALLERY.parent / rel).exists(), f'看图页链接失效: {rel}'
    print(f'[OK] {GALLERY.name}: 12 个相对路径全部有效')


if __name__ == '__main__':
    assert len(PAGES) == 12 and len(VERT) == 12
    for args in LOSSLESS:
        check_lossless(*args)
    check_preview()
    check_zip_and_gallery()
    print('第三话交付物校验全部通过。')
