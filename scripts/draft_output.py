"""安全、增量生成隔离草稿的 PNG 和无损 PDF。"""
import hashlib
from PIL import Image, ImageChops
from pdf_export import save_lossless_pdf_from_paths


def save_png_if_changed(im, path):
    """草稿逐像素不变即复用，避免无谓的 PNG 编码；不改正式目录。"""
    if path.exists():
        with Image.open(path) as existing:
            old = existing.convert('RGB')
        if old.size == im.size and ImageChops.difference(old, im.convert('RGB')).getbbox() is None:
            return False
    tmp = path.with_name(path.name + '.tmp')
    try:
        im.convert('RGB').save(tmp, format='PNG')
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)
    return True


def file_sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def ensure_draft_pdf(paths, pdf_path, previous):
    """页图和 PDF 自身哈希都一致才复用；先写临时文件再原子替换。"""
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode('utf-8'))
        digest.update(bytes.fromhex(file_sha256(path)))
    source = digest.hexdigest()
    if (pdf_path.exists() and previous.get('source') == source
            and previous.get('pdf') == file_sha256(pdf_path)):
        return {'source': source, 'pdf': previous['pdf']}, False
    tmp = pdf_path.with_name(pdf_path.name + '.tmp')
    try:
        save_lossless_pdf_from_paths(paths, tmp, resolution=150)
        tmp.replace(pdf_path)
    finally:
        tmp.unlink(missing_ok=True)
    return {'source': source, 'pdf': file_sha256(pdf_path)}, True

