# รวมโค้ด algorithms.py พร้อม validate_placements

from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.font_manager import FontProperties
import os


def safe_check_collision(placements, x, y, w, h, sheet_width):
    if x + w > sheet_width:
        return True
    return any(
        not (x + w <= p['x'] or x >= p['x'] + p['width'] or
             y + h <= p['y'] or y >= p['y'] + p['height'])
        for p in placements
    )


def sort_parts(parts, strategy="max_side"):
    if strategy == "max_side":
        return sorted(parts, key=lambda x: max(x), reverse=True)
    return parts


def first_fit_decreasing_2d(parts, sheet_width, y_step=5):
    parts_sorted = sort_parts(parts)
    placements = []

    for part in parts_sorted:
        placed = False
        for rotated in [False, True]:
            w, h = (part[0], part[1]) if not rotated else (part[1], part[0])
            max_y = 0 if not placements else max(p["y"] + p["height"] for p in placements)

            for y in range(0, int(max_y) + 500, y_step):
                for x in range(0, int(sheet_width - w) + 1):
                    if not safe_check_collision(placements, x, y, w, h, sheet_width):
                        placements.append({
                            "x": x, "y": y,
                            "width": w, "height": h,
                            "rotated": rotated
                        })
                        placed = True
                        break
                if placed:
                    break
            if placed:
                break

    return placements


def best_fit_decreasing_2d(parts, sheet_width, y_step=5):
    parts_sorted = sort_parts(parts)
    placements = []

    for part in parts_sorted:
        best_pos = None
        min_y = float('inf')

        for rotated in [False, True]:
            w, h = (part[0], part[1]) if not rotated else (part[1], part[0])
            max_y = 0 if not placements else max(p["y"] + p["height"] for p in placements)

            for y in range(0, int(max_y) + 500, y_step):
                for x in range(0, int(sheet_width - w) + 1):
                    if not safe_check_collision(placements, x, y, w, h, sheet_width):
                        if y + h < min_y:
                            min_y = y + h
                            best_pos = {"x": x, "y": y, "width": w, "height": h, "rotated": rotated}
                if best_pos and min_y < y:
                    break

        if best_pos:
            placements.append(best_pos)

    return placements


def guillotine_cutting_2d(parts, sheet_width):
    parts_sorted = sort_parts(parts)
    placements = []
    free_rects = [{"x": 0, "y": 0, "width": sheet_width, "height": float('inf')}]

    for part in parts_sorted:
        placed = False
        for i, rect in enumerate(free_rects):
            for rotated in [False, True]:
                w, h = (part[0], part[1]) if not rotated else (part[1], part[0])
                if w <= rect["width"] and h <= rect["height"] and rect["x"] + w <= sheet_width:
                    placement = {"x": rect["x"], "y": rect["y"], "width": w, "height": h, "rotated": rotated}
                    placements.append(placement)

                    right = {"x": rect["x"] + w, "y": rect["y"], "width": rect["width"] - w, "height": h}
                    top = {"x": rect["x"], "y": rect["y"] + h, "width": rect["width"], "height": rect["height"] - h}

                    free_rects.pop(i)
                    if right["width"] > 0 and right["height"] > 0:
                        free_rects.append(right)
                    if top["width"] > 0 and top["height"] > 0:
                        free_rects.append(top)

                    placed = True
                    break
            if placed:
                break

    return placements


def validate_placements(placements, orders, sheet_width, tolerance=0.01):
    def parts_match(p1, p2):
        return abs(p1[0] - p2[0]) <= tolerance and abs(p1[1] - p2[1]) <= tolerance

    for p in placements:
        if p['x'] + p['width'] > sheet_width + tolerance:
            return False, ["Over width"]

    for i in range(len(placements)):
        for j in range(i + 1, len(placements)):
            a = placements[i]
            b = placements[j]
            if not (a["x"] + a["width"] <= b["x"] or a["x"] >= b["x"] + b["width"] or
                    a["y"] + a["height"] <= b["y"] or a["y"] >= b["y"] + b["height"]):
                return False, ["Overlap"]

    order_counts = Counter((round(w, 2), round(h, 2)) for w, h in orders)
    placed_counts = Counter(
        (round(p['width'], 2), round(p['height'], 2)) if not p['rotated']
        else (round(p['height'], 2), round(p['width'], 2))
        for p in placements
    )

    for size, count in order_counts.items():
        if placed_counts[size] < count:
            return False, ["Missing Orders"]

    return True, []


def plot_placements_2d_matplotlib(placements, sheet_width, labels=None, title="2D Cutting Layout"):
    font_path = os.path.join(os.path.dirname(__file__), "NotoSansThai-Regular.ttf")
    thai_font = FontProperties(fname=font_path) if os.path.exists(font_path) else None

    max_y = max(p["y"] + p["height"] for p in placements)
    height_inches = max(6, min(20, max_y / 50))
    fig, ax = plt.subplots(figsize=(12, height_inches))

    ax.set_xlim(0, sheet_width)
    ax.set_ylim(0, max_y)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(200))
    ax.tick_params(axis='y', labelsize=10)

    for idx, p in enumerate(placements):
        color = 'red' if p["rotated"] else 'blue'
        rect = plt.Rectangle(
            (p["x"], p["y"]), p["width"], p["height"],
            edgecolor='black', facecolor=color, linewidth=1.2
        )
        ax.add_patch(rect)

        label_text = labels[idx] if labels and idx < len(labels) else f"{int(p['width'])}x{int(p['height'])}"
        ax.text(
            p["x"] + p["width"] / 2,
            p["y"] + p["height"] / 2,
            label_text,
            ha='center', va='center',
            fontsize=14, color='white',
            fontproperties=thai_font
        )

    ax.set_title(title, fontsize=14, fontproperties=thai_font)
    ax.set_xlabel("Width (cm)", fontproperties=thai_font)
    ax.set_ylabel("Length (cm)", fontproperties=thai_font)
    ax.invert_yaxis()
    ax.grid(True, linestyle='--', alpha=0.5)
    return fig
