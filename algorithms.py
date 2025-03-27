
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.font_manager import FontProperties
import os

def sort_parts(parts, strategy="max_side"):
    if strategy == "max_side":
        return sorted(parts, key=lambda x: max(x), reverse=True)
    return parts

def shelf_based_layout(parts, sheet_width, strategy="max_side", fit_strategy="first"):
    parts = sort_parts(parts, strategy)
    placements = []
    shelves = []

    for part in parts:
        best_placement = None
        best_shelf_index = None
        for rotated in [False, True]:
            w, h = (part[0], part[1]) if not rotated else (part[1], part[0])

            for shelf_index, shelf in enumerate(shelves):
                x_offset = shelf["used_width"]
                if x_offset + w <= sheet_width:
                    if fit_strategy == "first":
                        best_placement = {"x": x_offset, "y": shelf["y"], "width": w, "height": h, "rotated": rotated}
                        best_shelf_index = shelf_index
                        break
                    elif fit_strategy == "best":
                        remaining_width = sheet_width - (x_offset + w)
                        if best_placement is None or remaining_width < best_placement["remaining_width"]:
                            best_placement = {
                                "x": x_offset, "y": shelf["y"],
                                "width": w, "height": h,
                                "rotated": rotated,
                                "remaining_width": remaining_width
                            }
                            best_shelf_index = shelf_index
            if fit_strategy == "first" and best_placement:
                break

        if best_placement:
            placements.append(best_placement)
            shelves[best_shelf_index]["used_width"] += best_placement["width"]
            shelves[best_shelf_index]["height"] = max(shelves[best_shelf_index]["height"], best_placement["height"])
        else:
            for rotated in [False, True]:
                w, h = (part[0], part[1]) if not rotated else (part[1], part[0])
                if w <= sheet_width:
                    y_offset = sum(s["height"] for s in shelves)
                    new_shelf = {"y": y_offset, "used_width": w, "height": h}
                    shelves.append(new_shelf)
                    placements.append({
                        "x": 0, "y": y_offset, "width": w, "height": h, "rotated": rotated
                    })
                    break
    return placements

def first_fit_decreasing_2d(parts, sheet_width):
    return shelf_based_layout(parts, sheet_width, fit_strategy="first")

def best_fit_decreasing_2d(parts, sheet_width):
    return shelf_based_layout(parts, sheet_width, fit_strategy="best")

def guillotine_cutting_2d(parts, sheet_width):
    parts = sort_parts(parts)
    placements = []
    free_rects = [{"x": 0, "y": 0, "width": sheet_width, "height": float("inf")}]

    for part in parts:
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
        rect = plt.Rectangle((p["x"], p["y"]), p["width"], p["height"], edgecolor='black', facecolor=color, linewidth=1.2)
        ax.add_patch(rect)

        label_text = labels[idx] if labels and idx < len(labels) else f"{int(p['width'])}x{int(p['height'])}"
        ax.text(p["x"] + p["width"] / 2, p["y"] + p["height"] / 2, label_text,
                ha='center', va='center', fontsize=14, color='white', fontproperties=thai_font)

    ax.set_title(title, fontsize=14, fontproperties=thai_font)
    ax.set_xlabel("Width (cm)", fontproperties=thai_font)
    ax.set_ylabel("Length (cm)", fontproperties=thai_font)
    ax.invert_yaxis()
    ax.grid(True, linestyle='--', alpha=0.5)
    return fig
