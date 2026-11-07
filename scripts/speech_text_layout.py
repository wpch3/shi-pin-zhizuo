"""椭圆对白的可见文字测量与居中。

以实际 glyph bbox 而非字符数排版；文字块可见中心与椭圆中心重合。
所有文字角点必须位于椭圆内部，并保留统一的径向安全余量。
"""


def measure_speech_text(draw, lines, center, font, size, safety_radius=0.84):
    if not lines or any(not line for line in lines):
        raise ValueError('对白必须包含非空文字行')
    gap = round(size * 0.34)
    line_h = size + gap
    source_boxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    widths = [b[2] - b[0] for b in source_boxes]
    text_h = len(lines) * line_h - gap
    cx, cy = center

    # 先按行距排列，再用可见墨迹总边界修正垂直中心，消除字体 bearings 偏差。
    nominal_y = cy - text_h / 2
    positions = []
    for line, width, box in zip(lines, widths, source_boxes):
        positions.append([cx - width / 2 - box[0], nominal_y - box[1], line])
        nominal_y += line_h

    def visible_boxes():
        return [draw.textbbox((x, y), line, font=font) for x, y, line in positions]

    initial_boxes = visible_boxes()
    ink_cy = (min(b[1] for b in initial_boxes) + max(b[3] for b in initial_boxes)) / 2
    for position in positions:
        position[0] = round(position[0])
        position[1] = round(position[1] + cy - ink_cy)

    pad_x, pad_y = round(size * 1.12), round(size * 0.84)
    bw = max(widths) + 2 * pad_x + 16
    bh = text_h + 2 * pad_y + 14

    # 椭圆上下区域会收窄，矩形 padding 不足以保证长行安全。
    # 等量增加两个轴，直至所有可见文字角点均处于安全椭圆内。
    while True:
        rx, ry = bw / 2, bh / 2
        radii = [
            ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            for box in visible_boxes()
            for x in (box[0], box[2])
            for y in (box[1], box[3])
        ]
        if max(radii) <= safety_radius ** 2:
            break
        bw += 4
        bh += 4

    box = (round(cx - bw / 2), round(cy - bh / 2),
           round(cx + bw / 2), round(cy + bh / 2))
    if box[0] < 20 or box[1] < 20 or box[2] > 1420 or box[3] > 1900:
        raise ValueError(f'对白超出页面安全区: {box}, center={center}, lines={lines}')
    return {
        'positions': [(round(x), round(y), line) for x, y, line in positions],
        'bubble_size': (bw, bh),
        'box': box,
        'text_boxes': visible_boxes(),
        'safety_radius': safety_radius,
    }
