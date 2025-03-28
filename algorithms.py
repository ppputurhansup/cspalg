import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.font_manager import FontProperties
import os

def safe_check_collision(placements, x, y, w, h, sheet_width):
    if x < 0 or y < 0 or x + w > sheet_width:
        return True
    return any(
        not (x + w <= p['x'] or x >= p['x'] + p['width'] or
             y + h <= p['y'] or y >= p['y'] + p['height'])
        for p in placements
    )

def check_all_orders_placed(placements, orders):
    used = [False] * len(orders)
    for p in placements:
        for i, (w, h) in enumerate(orders):
            match_normal = abs(p["width"] - w) < 1e-3 and abs(p["height"] - h) < 1e-3
            match_rotated = abs(p["width"] - h) < 1e-3 and abs(p["height"] - w) < 1e-3
            if (match_normal or match_rotated) and not used[i]:
                used[i] = True
                break
    return all(used)

def match_labels_to_placements(placements, orders, original_labels):
    used = [False] * len(orders)
    matched_labels = []
    for p in placements:
        label = f"{int(p['width'])}x{int(p['height'])}"
        for i, (w, h) in enumerate(orders):
            if not used[i]:
                match_normal = abs(p["width"] - w) < 1e-3 and abs(p["height"] - h) < 1e-3
                match_rotated = abs(p["width"] - h) < 1e-3 and abs(p["height"] - w) < 1e-3
                if match_normal or match_rotated:
                    label = original_labels[i] if i < len(original_labels) else label
                    used[i] = True
                    break
        matched_labels.append(label)
    return matched_labels

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
            max_y = max([p["y"] + p["height"] for p in placements], default=0)
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
            max_y = max([p["y"] + p["height"] for p in placements], default=0)
            for y in range(0, int(max_y) + 500, y_step):
                for x in range(0, int(sheet_width - w) + 1):
                    if not safe_check_collision(placements, x, y, w, h, sheet_width):
                        if y + h < min_y:
                            min_y = y + h
                            best_pos = {
                                "x": x, "y": y,
                                "width": w, "height": h,
                                "rotated": rotated
                            }
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
                    placement = {
                        "x": rect["x"], "y": rect["y"],
                        "width": w, "height": h,
                        "rotated": rotated
                    }
                    placements.append(placement)
                    right = {
                        "x": rect["x"] + w, "y": rect["y"],
                        "width": rect["width"] - w, "height": h
                    }
                    top = {
                        "x": rect["x"], "y": rect["y"] + h,
                        "width": rect["width"], "height": rect["height"] - h
                    }
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
        rect = plt.Rectangle((p["x"], p["y"]), p["width"], p["height"],
                             edgecolor='black', facecolor=color, linewidth=1.2)
        ax.add_patch(rect)
        label_text = labels[idx] if labels and idx < len(labels) else f"{int(p['width'])}x{int(p['height'])}"
        ax.text(p["x"] + p["width"] / 2,
                p["y"] + p["height"] / 2,
                label_text,
                ha='center', va='center',
                fontsize=14, color='white',
                fontproperties=thai_font)
    ax.set_title(title, fontsize=14, fontproperties=thai_font)
    ax.set_xlabel("Width (cm)", fontproperties=thai_font)
    ax.set_ylabel("Length (cm)", fontproperties=thai_font)
    ax.invert_yaxis()
    ax.grid(True, linestyle='--', alpha=0.5)
    return fig
