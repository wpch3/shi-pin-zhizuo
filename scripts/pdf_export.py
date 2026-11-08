"""无损 PDF 导出：直接嵌入 PNG/Flate，避免 JPEG 二次压缩细线与小字。

实现上保留 PNG 的 IDAT 压缩流，并在 PDF 图像对象中使用 PNG predictor 15。
这样仍是逐像素无损，但比先解码再重新压缩的 PDF 更小。
"""
from __future__ import annotations

import io
import struct
from pathlib import Path

from PIL import Image


def _png_chunks(data: bytes):
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('不是有效 PNG')
    pos = 8
    while pos < len(data):
        if pos + 8 > len(data):
            raise ValueError('PNG chunk 头损坏')
        length = struct.unpack('>I', data[pos:pos + 4])[0]
        typ = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + length]
        if len(payload) != length:
            raise ValueError('PNG chunk 长度损坏')
        pos += 12 + length
        yield typ, payload
        if typ == b'IEND':
            break


def _pdf_from_png_streams(png_streams, path: Path, resolution: int = 150) -> None:
    objs: list[bytes] = [b'', b'']  # 1=Catalog, 2=Pages
    page_ids: list[int] = []

    def add(obj: bytes) -> int:
        objs.append(obj)
        return len(objs)

    for png_data in png_streams:
        chunks = list(_png_chunks(png_data))
        ihdr = next(payload for typ, payload in chunks if typ == b'IHDR')
        width, height, bit_depth, color_type, comp, filt, interlace = struct.unpack('>IIBBBBB', ihdr)
        if bit_depth != 8 or color_type != 2 or interlace != 0:
            raise ValueError(f'仅支持 8-bit RGB 非隔行 PNG: {(bit_depth, color_type, interlace)}')
        idat = b''.join(payload for typ, payload in chunks if typ == b'IDAT')
        if not idat:
            raise ValueError('PNG 缺少 IDAT')
        img_dict = (
            f'<< /Type /XObject /Subtype /Image /Width {width} /Height {height} '
            f'/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode '
            f'/DecodeParms << /Predictor 15 /Colors 3 /BitsPerComponent 8 /Columns {width} >> '
            f'/Length {len(idat)} >>\nstream\n'
        ).encode()
        img_id = add(img_dict + idat + b'\nendstream')
        pw = width / resolution * 72
        ph = height / resolution * 72
        content = f'q\n{pw:.4f} 0 0 {ph:.4f} 0 0 cm\n/Im{img_id} Do\nQ\n'.encode()
        cont_id = add(b'<< /Length ' + str(len(content)).encode() + b' >>\nstream\n' + content + b'endstream')
        page_id = add(
            f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {pw:.4f} {ph:.4f}] '
            f'/Resources << /XObject << /Im{img_id} {img_id} 0 R >> >> /Contents {cont_id} 0 R >>'.encode()
        )
        page_ids.append(page_id)

    if not page_ids:
        raise ValueError('PDF 至少需要一页')
    kids = ' '.join(f'{i} 0 R' for i in page_ids)
    objs[0] = b'<< /Type /Catalog /Pages 2 0 R >>'
    objs[1] = f'<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>'.encode()

    out = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
    offsets = []
    for i, obj in enumerate(objs, 1):
        offsets.append(len(out))
        out += f'{i} 0 obj\n'.encode() + obj + b'\nendobj\n'
    xref_pos = len(out)
    out += f'xref\n0 {len(objs) + 1}\n'.encode()
    out += b'0000000000 65535 f \n'
    for offset in offsets:
        out += f'{offset:010d} 00000 n \n'.encode()
    out += (
        f'trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\n'
        f'startxref\n{xref_pos}\n%%EOF\n'
    ).encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes(out))


def save_lossless_pdf(images, path: Path, resolution: int = 150) -> None:
    """按给定 DPI 将 PIL 图像逐页无损嵌入 PDF。"""
    streams = []
    for im in images:
        buf = io.BytesIO()
        im.convert('RGB').save(buf, format='PNG', optimize=True, compress_level=9)
        streams.append(buf.getvalue())
    _pdf_from_png_streams(streams, Path(path), resolution)


def save_lossless_pdf_from_paths(paths, path: Path, resolution: int = 150) -> None:
    """直接嵌入已保存的 PNG 母版，避免二次编码并确保 PDF 与 PNG 逐像素一致。"""
    _pdf_from_png_streams((Path(p).read_bytes() for p in paths), Path(path), resolution)
