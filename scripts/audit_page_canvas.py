"""画面级预筛：黑边、画内框线、无意义纯纸空白带、纸色外边距、画风/线宽漂移。

由来：2026-11-08 用户第三次指出第三话“无意义空白 + 黑边”，且结尾页画风与全话不一致。
这些缺陷此前只靠人眼，程序气泡审计（audit_speech_layout.py）完全查不到，导致带病交付。

本脚本只做**疑点预筛**，不拥有验收权：
- FAIL 项必须实际重绘或重新构图，不得靠裁切/色块掩盖后宣称合格；
- WARN 项必须人眼放大确认；
- 全部通过也不等于画面合格，仍须按 PROJECT_MEMORY 的十项固定清单逐页目检。

误报排除原则（写在输出里，避免下次误判）：
- 门框、衣架立柱、货架、窗棂是场景结构，不是画框；靠“线条是否贴边成矩形闭环”区分。
- 暗色餐厅/夜景本身很暗，不等于黑边；黑边要求“边缘暗且紧邻内侧明显更亮”。
- 场景内真实墙面/天花板的负空间可以放气泡；生图自带的纸色留白格＋框线不可以。

人眼复核台账：目标目录内可放 `canvas-review.json`（数组，每项 {"file","reason","verified"}）。
命中的疑点降级为 [note] 并打印复核原因，不计入 FAIL；未命中的一律 FAIL。
只有真的放大看过、确认是场景结构/道具才允许登记，禁止为了刷绿而登记。

用法：
    .venv/bin/python scripts/audit_page_canvas.py art/chapter-03-v5
    .venv/bin/python scripts/audit_page_canvas.py deliverables/full-v4/chapter-03
    .venv/bin/python scripts/audit_page_canvas.py art/chapter-03-v4 --anchor shot-01.png
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

DARK_EDGE_MEAN = 115.0      # 边缘条带平均亮度低于此值
EDGE_CONTRAST = 55.0        # 且紧邻内侧比它亮这么多 → 判定为黑边而非暗场景
DARK_LINE_RATIO = 0.75      # 单行/列暗像素占比 → 贯通长线
FRAME_ZONE = 0.20           # 距边 20% 以内的贯通长线视为画内框线嫌疑
BLANK_BAND_RATIO = 0.05     # 纯纸空白带超过图高 5%
PAPER_MARGIN_PX = 10        # 折算 1440 宽后纯纸外边距上限
STROKE_RATIO_WARN = 1.45    # 相对锚点页线宽比超过此值 → 画风漂移嫌疑


def _load(path: Path):
    im = Image.open(path).convert('RGB')
    return im, np.asarray(im).astype(np.int16)


def check_dark_edge(a):
    """黑边：边缘暗 + 紧邻内侧明显更亮（排除整页暗场景）。"""
    h, w, _ = a.shape
    t = max(2, round(h * 0.0025))
    d = max(6, round(h * 0.02))
    pairs = {
        'top': (a[:t].mean(), a[t:t + d].mean()),
        'bottom': (a[-t:].mean(), a[-t - d:-t].mean()),
        'left': (a[:, :t].mean(), a[:, t:t + d].mean()),
        'right': (a[:, -t:].mean(), a[:, -t - d:-t].mean()),
    }
    return [f'{k}={e:.0f}(内侧{i:.0f})' for k, (e, i) in pairs.items()
            if e < DARK_EDGE_MEAN and i - e > EDGE_CONTRAST]


def check_inner_frame(a):
    """贴边贯通细暗线 = 生图自带漫画框/页眉线。粗暗区（暗背景）不算。"""
    h, w, _ = a.shape
    gray = a.mean(axis=2)
    dark = gray < 120
    out = []
    for axis, length, other in (('h', h, w), ('v', w, h)):
        rows = dark if axis == 'h' else dark.T
        means = gray if axis == 'h' else gray.T
        hits = [i for i in range(length)
                if rows[i].mean() > DARK_LINE_RATIO
                and (i < length * FRAME_ZONE or i > length * (1 - FRAME_ZONE))]
        merged = []
        for i in hits:
            if merged and i - merged[-1][1] <= 3:
                merged[-1][1] = i
            else:
                merged.append([i, i])
        thin_max = max(4, round(length * 0.012))
        for s, e in merged:
            if e - s + 1 > thin_max:
                continue  # 粗暗带 → 暗场景/暗家具，不是框线
            line = means[s:e + 1].mean()
            before = means[max(0, s - 12):max(1, s - 3)].mean() if s > 12 else 255.0
            after = means[min(length - 1, e + 4):min(length, e + 13)].mean() if e < length - 13 else 255.0
            if max(before, after) - line < 35:
                continue  # 两侧同样暗 → 不是分隔线
            out.append(f'{axis}@{s}' if s == e else f'{axis}@{s}-{e}')
    return out


def _paper_ref(a):
    return np.median(np.concatenate([a[0, 0], a[0, -1], a[-1, 0], a[-1, -1]]), axis=0)


def check_blank_band(a):
    """顶部/底部纯纸空白带；扫描时跨过细分隔线，抓出“框内空白格”。"""
    h, w, _ = a.shape
    ref = _paper_ref(a)
    flat = (np.abs(a - ref).mean(axis=(1, 2)) < 9) & (a.std(axis=(1, 2)) < 8)
    gray = a.mean(axis=2)

    def scan(order):
        count = 0
        crossed = 0
        i = 0
        while i < h:
            y = order(i)
            if flat[y]:
                count += 1
                i += 1
                continue
            # 尝试跨过 <=6px 的细暗分隔线
            j = i
            while j < h and not flat[order(j)] and j - i < 6 and gray[order(j)].mean() < 170:
                j += 1
            if j < h and j > i and flat[order(j)]:
                crossed += j - i
                i = j
                continue
            break
        return count, crossed

    out = []
    for label, order in (('顶部', lambda i: i), ('底部', lambda i: h - 1 - i)):
        n, crossed = scan(order)
        if n > h * BLANK_BAND_RATIO:
            extra = f'（跨过{crossed}px框线，含框内空白格）' if crossed else ''
            out.append(f'{label}纯纸带 {n}px ({n / h:.1%}){extra}')
    return out


def check_paper_margin(a):
    h, w, _ = a.shape
    ref = _paper_ref(a)
    flat = (np.abs(a - ref).mean(axis=(0, 2)) < 9) & (a.std(axis=(0, 2)) < 8)
    left = 0
    while left < w and flat[left]:
        left += 1
    right = 0
    while right < w and flat[w - 1 - right]:
        right += 1
    scale = 1440 / w
    out = []
    if left * scale > PAPER_MARGIN_PX:
        out.append(f'左纸边 {left * scale:.0f}px@1440')
    if right * scale > PAPER_MARGIN_PX:
        out.append(f'右纸边 {right * scale:.0f}px@1440')
    return out


def stroke_width(a):
    """线宽代理：暗像素水平连续段平均长度（<=40px），粗线条明显更长。"""
    gray = a.mean(axis=2)
    dark = gray < 120
    pad = np.zeros((dark.shape[0], dark.shape[1] + 1), dtype=bool)
    pad[:, :-1] = dark
    starts = pad[:, 1:] & ~pad[:, :-1]
    ends = ~pad[:, 1:] & pad[:, :-1]
    lens = []
    for r in range(0, dark.shape[0], 3):
        s = np.flatnonzero(starts[r])
        e = np.flatnonzero(ends[r])
        n = min(len(s), len(e))
        if n:
            d = e[:n] - s[:n]
            lens.extend(d[(d > 0) & (d <= 40)].tolist())
    return float(np.mean(lens)) if lens else 0.0


def style_vector(a):
    f = a.astype(np.float32)
    gray = f.mean(axis=2)
    ink = float((gray < 110).mean())
    gx = np.abs(np.diff(gray, axis=1)).mean()
    gy = np.abs(np.diff(gray, axis=0)).mean()
    edge = float((gx + gy) / 2)
    mx, mn = f.max(axis=2), f.min(axis=2)
    sat = float(((mx - mn) / np.maximum(mx, 1)).mean())
    r, g, b = f[:, :, 0], f[:, :, 1], f[:, :, 2]
    warm = float(((r > g + 6) & (g > b + 2)).mean())
    return np.array([ink, edge, sat, warm, stroke_width(a)])


def main():
    args = [x for x in sys.argv[1:] if not x.startswith('--')]
    anchor = None
    for i, x in enumerate(sys.argv):
        if x == '--anchor' and i + 1 < len(sys.argv):
            anchor = sys.argv[i + 1]
    target = Path(args[0] if args else 'art/chapter-03-v4')
    files = sorted(p for p in target.glob('*.png') if p.is_file())
    if not files:
        print(f'没有 PNG：{target}')
        return 2
    fails = 0
    vectors = {}
    # 人眼复核台账：把已放大确认为场景结构的误报降级为 note，保留原因供追溯。
    review_path = target / 'canvas-review.json'
    reviewed = {}
    if review_path.exists():
        for item in json.loads(review_path.read_text()):
            reviewed[item['file']] = item
    print(f'=== 画面级预筛：{target}（{len(files)} 张）===')
    for p in files:
        im, a = _load(p)
        edge = check_dark_edge(a)
        frame = check_inner_frame(a)
        blank = check_blank_band(a)
        margin = check_paper_margin(a)
        vectors[p.name] = style_vector(a)
        problems = []
        if edge:
            problems.append('黑边: ' + ', '.join(edge))
        if frame:
            problems.append('画内框线: ' + ', '.join(frame[:8]))
        if blank:
            problems.append('无意义空白: ' + ', '.join(blank))
        if margin:
            problems.append('纸色外边距: ' + ', '.join(margin))
        if problems and p.name in reviewed:
            print(f'[note] {p.name} {im.size} —— 已人眼放大复核为场景结构，非画框')
            for x in problems:
                print(f'        - {x}')
            print(f'        复核结论：{reviewed[p.name]["reason"]}')
        elif problems:
            fails += 1
            print(f'[FAIL] {p.name} {im.size}')
            for x in problems:
                print(f'        - {x}')
        else:
            print(f'[ok  ] {p.name} {im.size}')

    if len(vectors) >= 4:
        names = list(vectors)
        M = np.stack([vectors[n] for n in names])
        med = np.median(M, axis=0)
        mad = np.median(np.abs(M - med), axis=0)
        mad[mad < 1e-6] = 1e-6
        print('\n=== 画风漂移预筛（相对本目录中位数，>3 MAD 需人眼确认）===')
        warned = False
        for n in names:
            z = np.abs(vectors[n] - med) / mad
            if z.max() > 3:
                warned = True
                print(f'[WARN] {n}: ink={z[0]:.1f} edge={z[1]:.1f} sat={z[2]:.1f} '
                      f'warm={z[3]:.1f} stroke={z[4]:.1f} MAD')
        if not warned:
            print('（无显著漂移疑点）')
        if anchor:
            if anchor in vectors:
                base = vectors[anchor]
            else:
                anchor_path = Path(anchor)
                if not anchor_path.is_file():
                    raise FileNotFoundError(f'画风锚点不存在: {anchor}')
                _, anchor_array = _load(anchor_path)
                base = style_vector(anchor_array)
            print(f'\n=== 相对画风锚点 {anchor} 的线宽比（>{STROKE_RATIO_WARN} 需人眼确认）===')
            print(f'锚点线宽代理 = {base[4]:.2f}px')
            for n in names:
                ratio = vectors[n][4] / max(base[4], 1e-6)
                flag = 'WARN' if ratio > STROKE_RATIO_WARN or ratio < 1 / STROKE_RATIO_WARN else 'ok  '
                print(f'[{flag}] {n}: {ratio:.2f}x')
        print('（ ink=暗线占比 edge=边缘密度 sat=饱和度 warm=暖色占比 stroke=线宽代理 ）')

    print(f'\n预筛结论：{fails}/{len(files)} 张存在黑边/框线/空白/纸边疑点。')
    print('提醒：本脚本不拥有验收权；FAIL 必须重绘或重构图，WARN 必须放大目检，全通过仍须逐页人眼验收。')
    print('误报排除：门框/衣架/货架是场景结构；整页暗场景不是黑边；场景内真实墙面无框线可放气泡。')
    return 1 if fails else 0


if __name__ == '__main__':
    raise SystemExit(main())
