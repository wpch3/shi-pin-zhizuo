"""第三话轻量在线预览 PDF、独立 PNG 图片版、网页逐页看图页。

背景（2026-11-08 用户反馈）：两份正式 PDF 各约 37MB，GitHub 对单文件在线预览报
"Unable to render code block"，用户下载后也没法把大 PDF 转成图片。

结论：主交付不再依赖 PDF。三件套——
1. `第三话_12页PNG图片版.zip`：12 张 1440×1920 PNG 原样打包（ZIP_STORED，
   PNG 已压缩、不二次编码），一次下载解压即得全部页图，不需要「PDF 转图片」。
2. `第三话_逐页看图.md`：12 张 PNG 用相对路径内嵌，GitHub 网页直接逐页渲染，
   连下载都不用；单张 PNG 约 3MB，GitHub 对图片的在线渲染比大 PDF 稳定得多。
3. `第三话_轻量在线预览.pdf`：12 页，720×960，JPEG q=88 嵌入为 DCTDecode，约 2～3MB，
   给需要连续翻页／打印草稿的人用。**明确不是定稿**：
   定稿画质以 `第三话_妹妹的休息日.pdf`、`第三话_竖屏全页漫画.pdf`（PNG/Flate 无损）
   与 1440×1920 PNG 为准。按长期记录第十二节，使用 JPEG 必须记录质量参数并放大复检，
   本脚本写入固定 q=88、不重复转存（直接从内存中的原始 PNG 一次编码），
   交付前须用 `verify_chapter03_pdf.py` 渲染回读并放大目检。

用法：.venv/bin/python scripts/export_lightweight_preview.py
"""
from pathlib import Path
import io
import zipfile

from PIL import Image
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'deliverables/full-v4/chapter-03'
OUT_DIR = ROOT / 'deliverables'
PREVIEW = OUT_DIR / '第三话_轻量在线预览.pdf'
ZIP = OUT_DIR / '第三话_12页PNG图片版.zip'
GALLERY = OUT_DIR / '第三话_逐页看图.md'
PREVIEW_SIZE = (720, 960)
JPEG_QUALITY = 88
# 页面物理尺寸与正式阅读版一致：720/75*72 = 691.2pt, 960/75*72 = 921.6pt
PREVIEW_RESOLUTION = 75


def label(path: Path, index: int) -> str:
    return '封面' if 'cover' in path.name else f'第{int(path.stem.split("-")[-1])}页'


def main():
    pages = sorted(SRC.glob('page-*.png'))
    if len(pages) != 12:
        raise SystemExit(f'阅读版应为 12 页，实测 {len(pages)} 页：{SRC}')

    # 1. 独立 PNG 图片版 ZIP（原样打包，字节级等同正式 PNG）
    with zipfile.ZipFile(ZIP, 'w', compression=zipfile.ZIP_STORED) as zf:
        for i, path in enumerate(pages):
            zf.write(path, arcname=f'第三话_12页PNG图片版/{i:02d}_{label(path, i)}.png')

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
    doc.set_metadata({'title': '第三话《妹妹的休息日》轻量在线预览（非定稿）',
                      'subject': f'720x960, JPEG q={JPEG_QUALITY}; 定稿请用无损PNG/Flate PDF'})
    doc.save(PREVIEW, deflate=True, garbage=4)
    doc.close()

    # 3. GitHub 网页逐页看图页
    lines = [
        '# 第三话《妹妹的休息日》· 逐页看图',
        '',
        '> 这一页在 GitHub 网页上会直接显示 12 张图，不用下载、不用把 PDF 转成图片。',
        '> 右键单张图片即可另存；要一次拿全 12 张，下载 `第三话_12页PNG图片版.zip`。',
        '> 两份约 37MB 的 `第三话_妹妹的休息日.pdf` / `第三话_竖屏全页漫画.pdf` 是 PNG/Flate',
        '> 无损定稿，保留作印刷／归档备份；`第三话_轻量在线预览.pdf` 是 720×960 的',
        '> 小体积翻页预览，画质不代表定稿。',
        '',
    ]
    for i, path in enumerate(pages):
        rel = path.relative_to(OUT_DIR).as_posix()
        lines += [f'## {label(path, i)}', '', f'![{label(path, i)}]({rel})', '']
    GALLERY.write_text('\n'.join(lines), encoding='utf-8')

    print(f'轻量预览 PDF：{PREVIEW.name}  {PREVIEW.stat().st_size / 1024 / 1024:.2f} MB, 12 页, JPEG q={JPEG_QUALITY}')
    print(f'PNG 图片版：{ZIP.name}  {ZIP.stat().st_size / 1024 / 1024:.2f} MB, 12 张')
    print(f'网页看图页：{GALLERY.name}')


if __name__ == '__main__':
    main()
