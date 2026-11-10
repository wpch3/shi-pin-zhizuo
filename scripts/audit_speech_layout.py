"""静态审计两话全部 speech(...) 调用；人物遮挡仍须逐页人工目检。"""
import ast
import copy
import math
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from speech_text_layout import measure_speech_text

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / 'assets/fonts/NotoSansCJKsc-Bold.otf'
FILES = [ROOT / 'scripts/build_chapter_v4.py', ROOT / 'scripts/build_chapter02_v4.py', ROOT / 'scripts/build_chapter03_v4.py', ROOT / 'scripts/build_chapter04_v1.py', ROOT / 'scripts/build_chapter02_redraw.py', ROOT / 'scripts/build_chapter05_draft.py', ROOT / 'scripts/build_chapter05_v3.py', ROOT / 'scripts/build_chapter05_home_review.py', ROOT / 'scripts/build_chapter05_home_v3.py', ROOT / 'scripts/build_chapter05_home_recovery.py', ROOT / 'scripts/build_chapter05_home_recovery_v2.py']
draw = ImageDraw.Draw(Image.new('RGB', (16, 16)))
by_scene = defaultdict(list)
records = []

def literal_for_mode(node, review):
    # Replace REVIEW branches even when nested in a coordinate tuple.
    class SelectReview(ast.NodeTransformer):
        def visit_IfExp(self, expr):
            if not isinstance(expr.test, ast.Name) or expr.test.id != 'REVIEW':
                raise ValueError('unsupported conditional in speech layout')
            return self.visit(expr.body if review else expr.orelse)
    return ast.literal_eval(SelectReview().visit(copy.deepcopy(node)))


for review in (False, True):
    for path in FILES:
        tree = ast.parse(path.read_text())
        scene = ''
        for node in tree.body:
            if (isinstance(node, ast.Assign) and isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Name) and node.value.func.id == 'scene'):
                scene = ast.literal_eval(node.value.args[0])
            if not (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Name) and node.value.func.id == 'speech'):
                continue
            args = node.value.args
            lines = ast.literal_eval(args[1])
            center = literal_for_mode(args[2], review)
            target = literal_for_mode(args[3], review)
            size = ast.literal_eval(args[4]) if len(args) > 4 else (30 if 'chapter02' not in path.name else 29)
            font = ImageFont.truetype(str(FONT), size)
            layout = measure_speech_text(draw, lines, center, font, size)
            final_boxes = [draw.textbbox((x, y), line, font=font) for x, y, line in layout['positions']]
            cx, cy = center
            line_center_error = max(abs((b[0] + b[2]) / 2 - cx) for b in final_boxes)
            block_center_error = abs((min(b[1] for b in final_boxes) + max(b[3] for b in final_boxes)) / 2 - cy)
            bw, bh = layout['bubble_size']
            radii = [((x-cx)/(bw/2))**2 + ((y-cy)/(bh/2))**2
                     for b in final_boxes for x in (b[0], b[2]) for y in (b[1], b[3])]
            max_radius = math.sqrt(max(radii))
            assert line_center_error <= 1, (path, scene, lines, line_center_error)
            assert block_center_error <= 1, (path, scene, lines, block_center_error)
            assert max_radius <= .8401, (path, scene, lines, max_radius)
            rx, ry = bw/2, bh/2
            dx, dy = target[0]-cx, target[1]-cy
            scale = 1/math.sqrt((dx/rx)**2+(dy/ry)**2)
            edge = (cx+dx*scale, cy+dy*scale)
            distance = math.hypot(target[0]-edge[0], target[1]-edge[1])
            record = {'chapter': path.name, 'mode': 'review' if review else 'standard', 'scene': scene, 'lines': lines,
                      'center': center, 'target': target, 'box': layout['box'],
                      'distance': distance, 'radius': max_radius}
            records.append(record)
            by_scene[(path.name, review, scene)].append(record)
for key, bubbles in by_scene.items():
    for i, a in enumerate(bubbles):
        for b in bubbles[i+1:]:
            overlap = not (a['box'][2] <= b['box'][0] or b['box'][2] <= a['box'][0]
                           or a['box'][3] <= b['box'][1] or b['box'][3] <= a['box'][1])
            assert not overlap, f'气泡框体重叠: {key}: {a["lines"]} / {b["lines"]}'

print(f'PASS: {len(records)} 个气泡（普通及检查版）；逐行水平居中、文字块垂直居中、椭圆安全边距、同页气泡互不重叠。')
print('以下仅作人工目检提示，不代替人物遮挡与说话者归属判断：')
for record in records:
    if record['distance'] > 350:
        print(f"  距离提示 {record['chapter']} {record['scene']} {record['lines']}: {record['distance']:.0f}px")
