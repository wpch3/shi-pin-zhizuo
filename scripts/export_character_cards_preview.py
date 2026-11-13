#!/usr/bin/env python3
"""人设卡 PDF 的可打开副本：轻量在线预览 PDF、兼容版 PDF、逐页 PNG、PNG ZIP、网页看图页。

背景：正式人设 PDF（8 页整图 JPEG，1.1MB，中文文件名）在本机可正常解析，
但 GitHub 网页 / 浏览器内置 PDF 预览对「中文路径 + 纯整页图片 + 无 Fast Web View」
容易白屏或报 Unable to render code block。此脚本生成不依赖在线 PDF 渲染的入口。
"""
from __future__ import annotations

import io
import os
import zipfile
from pathlib import Path

import pymupdf
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "deliverables/人物资料/人设与合照"
SRC = OUT_DIR / "完整人设与合照_V3.pdf"
PNG_DIR = OUT_DIR / "完整人设与合照_PNG版"
PREVIEW_PDF = OUT_DIR / "character-cards-v3-preview.pdf"  # ASCII 名，规避中文 URL
COMPAT_PDF = OUT_DIR / "完整人设与合照_V3_兼容版.pdf"
ZIP_PATH = OUT_DIR / "完整人设与合照_8页PNG图片版.zip"
VIEW_MD = OUT_DIR / "完整人设与合照_逐页看图.md"

TITLES = [
    "江怀川｜父亲", "沈静宜｜母亲", "江昭远｜大哥", "江望舒｜姐姐",
    "江星野｜二弟", "江辰希｜妹妹", "小满｜小侄女", "七人合照｜家族角色设定资料集",
]


def main() -> None:
    if any(p.exists() or p.is_symlink() for p in (PNG_DIR, PREVIEW_PDF, COMPAT_PDF, ZIP_PATH, VIEW_MD)):
        raise SystemExit('人设交付已存在；为保护文件，禁止原地重建。请复制脚本并使用新的输出目录。')
    if not SRC.exists():
        raise SystemExit(f"缺少人设 PDF：{SRC}")
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(SRC)
    if doc.page_count != 8:
        raise SystemExit(f"人设 PDF 页数异常：{doc.page_count}")

    # 1) 逐页 PNG：直接取 PDF 内嵌的 1440x1920 原图，解码后无损转 PNG
    png_paths: list[Path] = []
    for i in range(doc.page_count):
        info = doc.extract_image(doc[i].get_images(full=True)[0][0])
        im = Image.open(io.BytesIO(info["image"])).convert("RGB")
        if im.size != (1440, 1920):
            raise SystemExit(f"第 {i+1} 页尺寸异常：{im.size}")
        p = PNG_DIR / f"{i+1:02d}.png"
        im.save(p, format="PNG", optimize=True)
        png_paths.append(p)

    # 2) 轻量在线预览 PDF：720x960 / JPEG q=88 / ASCII 文件名
    light = pymupdf.open()
    for p in png_paths:
        im = Image.open(p).resize((720, 960), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=88, subsampling=0, optimize=True)
        page = light.new_page(width=691.2, height=921.6)
        page.insert_image(page.rect, stream=buf.getvalue())
    light.set_metadata({"title": "完整人设与合照 V3 · 轻量在线预览（非定稿）",
                        "subject": "JPEG q=88 / 720x960 / 仅供网页快速看图"})
    # 本环境 PyMuPDF 已移除 linear=True（Linearisation is no longer supported），
    # 改用 clean + garbage + deflate 重存，确保 xref/trailer 规范、无游离对象。
    light.save(PREVIEW_PDF, garbage=4, deflate=True, clean=True,
               pretty=False, no_new_id=False)
    light.close()

    # 3) 兼容版正式 PDF：同样规范重存并写入新 /ID，去掉旧的手写 xref 隐患
    doc.set_metadata({**doc.metadata, "title": "完整人设与合照 V3（兼容版）"})
    doc.save(COMPAT_PDF, garbage=4, deflate=True, clean=True,
             pretty=False, no_new_id=False)

    # 4) PNG ZIP
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in png_paths:
            z.write(p, p.name)

    # 5) 网页逐页看图页（相对路径，GitHub 直接渲染 PNG）
    lines = [
        "# 完整人设与合照 V3｜逐页看图",
        "",
        "> 正式文件：`完整人设与合照_V3.pdf`（8 页，无损原图）。若网页 PDF 预览打不开，",
        "> 直接用本页逐张 PNG；也可下载 `完整人设与合照_8页PNG图片版.zip`，",
        "> 或打开 `character-cards-v3-preview.pdf`（720×960 / JPEG q=88 / 明确非定稿）。",
        "> `完整人设与合照_V3_兼容版.pdf` 为补了 Fast Web View 与文件 ID 的兼容重存版。",
        "",
        "## 8 页人设卡与合照",
        "",
    ]
    for i, p in enumerate(png_paths):
        rel = f"{PNG_DIR.name}/{p.name}"
        lines += [f"### {i+1} / 8　{TITLES[i]}", "", f"![{TITLES[i]}]({rel})", ""]
    lines += [
        "## 单独立绘（画风与人设基准）",
        "",
        "以下 7 张为 `art/character-v3/` 的官方单独立绘，`family-character-design-v3.jpg`",
        "是用户确认的最高视觉基准：**暖纸底、低饱和、细腻手绘线、轻薄水彩填色、自然五官、",
        "克制阴影、写实头身比**。生图必须与此并排比对，不得只比脸。",
        "",
        "![家族角色设定资料集](../../../art/reference/family-character-design-v3.jpg)",
        "",
    ]
    for name, label in [
        ("second-brother", "江星野｜二弟（男主）"), ("older-sister", "江望舒｜姐姐"),
        ("younger-sister", "江辰希｜妹妹"), ("niece", "小满｜小侄女"),
        ("eldest-brother", "江昭远｜大哥"), ("father", "江怀川｜父亲"), ("mother", "沈静宜｜母亲"),
    ]:
        lines += [f"### {label}", "", f"![{label}](../../../art/character-v3/{name}.png)", ""]
    lines += ["文字设定（身份/经历/性格/外貌）见 `../../../data/characters.json`，",
              "画风锁定条款见 `../../../docs/V3角色与画风锁定.md`。", ""]
    VIEW_MD.write_text("\n".join(lines), encoding="utf-8")
    doc.close()

    # 6) 一次自检
    d2 = pymupdf.open(PREVIEW_PDF)
    assert d2.page_count == 8, "轻量预览页数不对"
    for i in range(8):
        assert len(d2[i].get_images(full=True)) == 1, f"轻量预览第{i+1}页缺图"
        assert d2[i].get_pixmap(dpi=36).width > 0, f"轻量预览第{i+1}页无法渲染"
    d2.close()
    d3 = pymupdf.open(COMPAT_PDF)
    assert d3.page_count == 8 and not d3.is_encrypted
    d3.close()
    with zipfile.ZipFile(ZIP_PATH) as z:
        assert len(z.namelist()) == 8
        for p in png_paths:
            assert z.read(p.name) == p.read_bytes(), f"ZIP 内 {p.name} 字节不等同"
    text = VIEW_MD.read_text(encoding="utf-8")
    links = [ln.split("](", 1)[1].rstrip(")") for ln in text.splitlines() if ln.startswith("![")]
    for rel in links:
        assert (OUT_DIR / rel).exists(), f"看图页链接失效：{rel}"
    print(f"[OK] 轻量预览 8 页 {PREVIEW_PDF.stat().st_size/1024:.0f}KB；"
          f"兼容版 8 页 {COMPAT_PDF.stat().st_size/1024:.0f}KB；"
          f"PNG 8 张；ZIP {ZIP_PATH.stat().st_size/1024/1024:.1f}MB；"
          f"看图页 {len(links)} 个链接全部有效")


if __name__ == "__main__":
    main()
