# -*- coding: utf-8 -*-
"""基础排版工具：中文换行、气泡、旁白框、贴图裁切。"""
from PIL import Image, ImageDraw, ImageFont

import os

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SUB = os.path.join(_HERE, "assets/fonts")          # 仓库内的子集字体（优先）
_RAW = "/home/user/fonts"                            # 本机完整字重（可选）


def _pick(name):
    for d, suffix in ((_SUB, ".subset.ttf"), (_RAW, ".ttf")):
        p = os.path.join(d, f"LXGWWenKai-{name}{suffix}")
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"缺少字体 LXGWWenKai-{name}，请先运行 tools/get_fonts.sh")


F_REG = _pick("Regular")
F_MED = _pick("Medium")
F_LIGHT = F_REG

INK = (36, 30, 26)
PAPER = (251, 247, 241)
CREAM = (243, 233, 218)
GREY = (150, 138, 126)
ACCENT = (196, 92, 74)   # 朱红，用于小标题 / 强调

# 不能出现在行首的标点
NO_HEAD = "，。、；：？！）」』】…—·%"
# 不能出现在行尾的标点
NO_TAIL = "（「『【"


def font(size, weight="med"):
    path = {"med": F_MED, "reg": F_REG, "light": F_LIGHT}[weight]
    return ImageFont.truetype(path, size)


def tw(draw, text, f):
    return draw.textlength(text, font=f)


def wrap(draw, text, f, max_w):
    """按字符贪心换行，避免标点出现在行首。"""
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(cur); cur = ""; continue
        trial = cur + ch
        if tw(draw, trial, f) <= max_w or not cur:
            cur = trial
        else:
            if ch in NO_HEAD:          # 标点跟着上一行走
                cur = trial
                continue
            if cur[-1] in NO_TAIL:
                lines.append(cur[:-1]); cur = cur[-1] + ch
            else:
                lines.append(cur); cur = ch
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, xy, lines, f, fill=INK, lh=1.62, align="left", tracking=0):
    x, y = xy
    step = int(f.size * lh)
    for ln in lines:
        w = tw(draw, ln, f) + tracking * max(0, len(ln) - 1)
        if align == "center":
            draw.text((x - w / 2, y), ln, font=f, fill=fill)
        elif align == "right":
            draw.text((x - w, y), ln, font=f, fill=fill)
        else:
            draw.text((x, y), ln, font=f, fill=fill)
        y += step
    return y


def cover(im, w, h, fx=0.5, fy=0.5):
    """等比缩放铺满 w*h，再按焦点裁切。"""
    s = max(w / im.width, h / im.height)
    nw, nh = int(im.width * s + 0.5), int(im.height * s + 0.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    x = int((nw - w) * fx)
    y = int((nh - h) * fy)
    return im.crop((x, y, x + w, y + h))


def tail(draw, box, target, color=INK, fill=(255, 255, 255), width=3, base=26):
    """从气泡边缘朝 target 画一个三角尾巴。box = (x0,y0,x1,y1)。"""
    x0, y0, x1, y1 = box
    tx, ty = target
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if ty > y1:                                    # 目标在下方
        px = min(max(tx, x0 + 34), x1 - 34)
        a = (px - base / 2, y1 - 2); b = (px + base / 2, y1 - 2); c = (tx, ty)
    elif ty < y0:                                  # 目标在上方
        px = min(max(tx, x0 + 34), x1 - 34)
        a = (px - base / 2, y0 + 2); b = (px + base / 2, y0 + 2); c = (tx, ty)
    elif tx < x0:                                  # 目标在左侧
        py = min(max(ty, y0 + 30), y1 - 30)
        a = (x0 + 2, py - base / 2); b = (x0 + 2, py + base / 2); c = (tx, ty)
    else:                                          # 目标在右侧
        py = min(max(ty, y0 + 30), y1 - 30)
        a = (x1 - 2, py - base / 2); b = (x1 - 2, py + base / 2); c = (tx, ty)
    draw.polygon([a, b, c], fill=fill, outline=color)


def bubble(img, text, box, target=None, size=38, pad=(34, 26), radius=46,
           line_color=INK, fill=(255, 255, 255), width=3, lh=1.55, align="center"):
    """圆角气泡，box=(x0,y0,x1,y1)；文字自适应缩放以塞进 box。"""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    inner_w = (x1 - x0) - pad[0] * 2
    f = font(size, "med")
    lines = wrap(d, text, f, inner_w)
    # 太高就缩字号
    while (len(lines) * f.size * lh + pad[1] * 2) > (y1 - y0) and size > 20:
        size -= 2
        f = font(size, "med")
        lines = wrap(d, text, f, inner_w)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=line_color, width=width)
    if target:
        tail(d, box, target, color=line_color, fill=fill, width=width)
        d.rounded_rectangle(box, radius=radius, fill=fill, outline=line_color, width=width)
    h = len(lines) * f.size * lh
    ty = (y0 + y1) / 2 - h / 2 + f.size * 0.12
    for ln in lines:
        w = tw(d, ln, f)
        d.text(((x0 + x1) / 2 - w / 2, ty), ln, font=f, fill=INK)
        ty += f.size * lh
    return box


def caption(img, lines, box, size=30, fill=CREAM, line_color=INK, width=2,
            radius=6, pad=(26, 20), lh=1.60, weight="reg", ink=INK):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=line_color, width=width)
    f = font(size, weight)
    y = box[1] + pad[1]
    for ln in lines:
        d.text((box[0] + pad[0], y), ln, font=f, fill=ink)
        y += int(f.size * lh)
    return box


def sfx(img, text, pos, size=130, fill=ACCENT, stroke=(255, 255, 255), sw=10, weight="med"):
    d = ImageDraw.Draw(img)
    f = font(size, weight)
    d.text(pos, text, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke)


def header(img, left, right, size=22, y=42, margin=56):
    d = ImageDraw.Draw(img)
    f = font(size, "reg")
    d.text((margin, y), left, font=f, fill=GREY)
    w = tw(d, right, f)
    d.text((img.width - margin - w, y), right, font=f, fill=GREY)
    d.line([(margin, y + size + 16), (img.width - margin, y + size + 16)], fill=(228, 219, 207), width=2)


def label(img, text, xy, size=24, color=ACCENT, weight="med"):
    d = ImageDraw.Draw(img)
    d.text(xy, text, font=font(size, weight), fill=color)


def chat_box(img, name, text, box, size=32):
    """手机消息样式的对话块。"""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=26, fill=(255, 255, 255), outline=INK, width=2)
    f = font(size, "reg")
    lines = wrap(d, text, f, (x1 - x0) - 56)
    label(img, name, (x0 + 28, y0 + 16), size=22, color=ACCENT)
    y = y0 + 54
    for ln in lines:
        d.text((x0 + 28, y), ln, font=f, fill=INK)
        y += int(f.size * 1.55)
    return box
