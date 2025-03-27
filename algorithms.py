import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.font_manager import FontProperties
import os

# ✅ ฟังก์ชันจัดเรียง parts ตามกลยุทธ์ต่างๆ
def sort_parts(parts, strategy="max_side"):
    if strategy == "max_side":
        return sorted(parts, key=lambda x: max(x), reverse=True)
    elif strategy == "area":
        return sorted(parts, key=lambda x: x[0] * x[1], reverse=True)
    elif strategy == "width":
        return sorted(parts, key=lambda x: x[0], reverse=True)
    return parts

# ✅ ฟังก์ชันหลักสำหรับ layout แบบ shelf-based
def shelf_based_layout(parts, sheet_width, sort_strategy="max_side"):
    parts = sort_parts(parts, strategy=sort_strategy)
    placements = []
    y_offset = 0
    shelf_height = 0
    current_shelf = []

    for part in parts:
        placed = False
        for rotated in [False, True]:
            w, h = (part[0], part[1]) if not rotated else (part[1], part[0])
            x_offset = sum(p["width"] for p in current_shelf)

            if x_offset + w <= sheet_width:
                placement = {
                    "x": x_offset,
                    "y": y_offset,
                    "width": w,
                    "height": h,
                    "rotated": rotated
                }
                placements.append(placement)
                current_shelf.append(placement)
                shelf_height = max(shelf_height, h)
                placed = True
                break

        if not placed:
            y_offset += shelf_height
            shelf_height = 0
            current_shelf = []
            for rotated in [False, True]:
                w, h = (part[0], part[1]) if not rotated else (part[1], part[0])
                if w <= sheet_width:
                    placement = {
                        "x": 0,
                        "y": y_offset,
                        "width": w,
                        "height": h,
                        "rotated": rotated
                    }
                    placements.append(placement)
                    current_shelf.append(placement)
                    shelf_height = h
                    break

    return placements

# ✅ อัลกอริทึม FFD 2D (เรียง max side)
def first_fit_decreasing_2d(parts, sheet_width):
    return shelf_based_layout(parts, sheet_width, sort_strategy="max_side")

# ✅ อัลกอริทึม BFD 2D (เรียง area)
def best_fit_decreasing_2d(parts, sheet_width):
    return shelf_based_layout(parts, sheet_width, sort_strategy="area")

# ✅ อัลกอริทึม Guillotine 2D (เรียง width)
def guillotine_cutting_2d(parts, sheet_width):
    return shelf_based_layout(parts, sheet_width, sort_strategy="width")

# ✅ ฟังก์ชันเช็คว่าชิ้นงานถูกวางครบไหม
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

# ✅ ฟังก์ชันวาด layout
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
