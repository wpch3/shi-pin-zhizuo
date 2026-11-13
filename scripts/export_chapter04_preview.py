"""第四话轻量在线预览 PDF、独立 PNG 图片版、网页逐页看图页（10 页）。

沿用第三话决定：两份 PNG/Flate 无损 PDF 作印刷/归档定稿与备份；
主入口是网页逐页看图 + PNG ZIP + 轻量 JPEG 预览 PDF，规避 GitHub 大 PDF
"Unable to render code block" 与「下载后没法把 PDF 转图片」。

与第三话脚本的差异（2026-11-08 自查修复）：缓存写入移到三件套全部生成成功之后，
避免「先写缓存、产物生成失败」导致下次误判为无变化而跳过重建（失败原子性）。

用法：.venv/bin/python scripts/export_chapter04_preview.py
"""
from pathlib import Path
import hashlib
import io
import json
import os
import zipfile

from PIL import Image
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'deliverables/章节/第四话/历史图源/full-v4'
OUT_DIR = ROOT / 'deliverables/章节/第四话/原交付'
PREVIEW = OUT_DIR / '第四话_轻量在线预览.pdf'
ZIP = OUT_DIR / '第四话_10页PNG图片版.zip'
GALLERY = OUT_DIR / '第四话_逐页看图.md'
PREVIEW_SIZE = (720, 960)
JPEG_QUALITY = 88
PREVIEW_RESOLUTION = 75
N = 10

CACHE = OUT_DIR / '.chapter04-lightweight-cache.json'


def label(path: Path, index: int) -> str:
    return '封面' if 'cover' in path.name else f'第{int(path.stem.split("-")[-1])}页'


def page_digest(paths):
    h = hashlib.sha256()
    for path in paths:
        h.update(path.name.encode())
        h.update(path.read_bytes())
    return h.hexdigest()


def main():
    if any(p.exists() or p.is_symlink() for p in (PREVIEW, ZIP, GALLERY)):
        raise SystemExit('第四话已有交付文件；为保护作品，禁止原地重建。请复制脚本并使用新的输出目录。')
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pages = sorted(SRC.glob('page-*.png'))
    if len(pages) != N:
        raise SystemExit(f'阅读版应为 {N} 页，实测 {len(pages)} 页：{SRC}')
    digest = page_digest(pages)
    outputs = [PREVIEW, ZIP, GALLERY]
    prev = json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}
    if prev.get('page_digest') == digest and all(p.exists() for p in outputs):
        print(f'增量导出：{N} 张 PNG 母版未变化，轻量PDF / ZIP / 看图页全部复用，跳过重建。')
        return

    # 1. 独立 PNG 图片版 ZIP（原样打包，字节级等同正式 PNG）
    with zipfile.ZipFile(ZIP, 'w', compression=zipfile.ZIP_STORED) as zf:
        for i, path in enumerate(pages):
            zf.write(path, arcname=f'第四话_10页PNG图片版/{i:02d}_{label(path, i)}.png')

    # 2. 轻量预览 PDF：从原始 PNG 一次编码成 JPEG，不经二次转存
    doc = pymupdf.open()
    pw = PREVIEW_SIZE[0] / PREVIEW_RESOLUTION * 72
    ph = PREVIEW_SIZE[1] / PREVIEW_RESOLUTION * 72
    for path in pages:
        im = Image.open(path).convert('RGB')
        if im.size != (1440, 1920):
            raise SystemExit(f'页面尺寸异常：{path} {im.size}')
        thumb = im.resize(PREVIEW_SIZE, Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        thumb.save(buf, format='JPEG', quality=JPEG_QUALITY, subsampling=0, optimize=True)
        page = doc.new_page(width=pw, height=ph)
        page.insert_image(page.rect, stream=buf.getvalue())
    doc.set_metadata({'title': '第四话《陪小满》轻量在线预览（非定稿）',
                      'subject': f'720x960, JPEG q={JPEG_QUALITY}; 定稿请用无损PNG/Flate PDF'})
    doc.save(PREVIEW, deflate=True, garbage=4)
    doc.close()

    # 3. GitHub 网页逐页看图页
    lines = [
        '# 第四话《陪小满》· 逐页看图',
        '',
        f'> 这一页在 GitHub 网页上会直接显示 {N} 张图，不用下载、不用把 PDF 转成图片。',
        f'> 右键单张图片即可另存；要一次拿全 {N} 张，下载 `{ZIP.name}`。',
        '> `第四话_陪小满.pdf` / `第四话_竖屏全页漫画.pdf` 是 PNG/Flate',
        '> 无损定稿，保留作印刷／归档备份；`第四话_轻量在线预览.pdf` 是 720×960 的',
        '> 小体积翻页预览，画质不代表定稿。',
        '',
    ]
    for i, path in enumerate(pages):
        rel = os.path.relpath(path, OUT_DIR).replace(os.sep, '/')
        lines += [f'## {label(path, i)}', '', f'![{label(path, i)}]({rel})', '']
    GALLERY.write_text('\n'.join(lines), encoding='utf-8')

    # 缓存只在三件套全部落盘成功后写入：失败不得短路掉下一次重建。
    CACHE.write_text(json.dumps({'page_digest': digest}, ensure_ascii=False), encoding='utf-8')

    print(f'轻量预览 PDF：{PREVIEW.name}  {PREVIEW.stat().st_size / 1024 / 1024:.2f} MB, {N} 页, JPEG q={JPEG_QUALITY}')
    print(f'PNG 图片版：{ZIP.name}  {ZIP.stat().st_size / 1024 / 1024:.2f} MB, {N} 张')
    print(f'网页看图页：{GALLERY.name}')


if __name__ == '__main__':
    main()
