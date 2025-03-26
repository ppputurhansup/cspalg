import matplotlib.pyplot as plt

def check_collision(placements, x, y, w, h):
    for p in placements:
        if not (x + w <= p['x'] or x >= p['x'] + p['width'] or
                y + h <= p['y'] or y >= p['y'] + p['height']):
            return True
    return False

def sort_parts(parts, strategy="max_side"):
    if strategy == "max_side":
        return sorted(parts, key=lambda x: max(x), reverse=True)
    return parts

def first_fit_decreasing_2d(parts, sheet_width, sort_by="max_side"):
    parts_sorted = sort_parts(parts, sort_by)
    placements = []

    for part in parts_sorted:
        placed = False
        for rotated in [False, True]:
            w, h = (part[0], part[1]) if not rotated else (part[1], part[0])
            for y in range(0, 10000):
                for x in range(0, int(sheet_width - w) + 1):
                    if not check_collision(placements, x, y, w, h):
                        placements.append({"x": x, "y": y, "width": w, "height": h, "rotated": rotated})
                        placed = True
                        break
                if placed:
                    break
            if placed:
                break

    return placements

def best_fit_decreasing_2d(parts, sheet_width, sort_by="max_side"):
    parts_sorted = sort_parts(parts, sort_by)
    placements = []

    for part in parts_sorted:
        best_pos = None
        min_waste = float('inf')
        for rotated in [False, True]:
            w, h = (part[0], part[1]) if not rotated else (part[1], part[0])
            for y in range(0, 10000):
                for x in range(0, int(sheet_width - w) + 1):
                    if not check_collision(placements, x, y, w, h):
                        waste = y + h
                        if waste < min_waste:
                            best_pos = {"x": x, "y": y, "width": w, "height": h, "rotated": rotated}
                            min_waste = waste
        if best_pos:
            placements.append(best_pos)

    return placements

def guillotine_cutting_2d(parts, sheet_width, sort_by="max_side"):
    parts_sorted = sort_parts(parts, sort_by)
    placements = []
    free_rects = [{"x": 0, "y": 0, "width": sheet_width, "height": float('inf')}]

    for part in parts_sorted:
        placed = False
        for i, rect in enumerate(free_rects):
            for rotated in [False, True]:
                w, h = (part[0], part[1]) if not rotated else (part[1], part[0])
                if w <= rect["width"] and h <= rect["height"]:
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

def place_parts_free_rect(parts, sheet_width, sheet_length=float('inf'), sort_by="max_side"):
    parts_sorted = sort_parts(parts, sort_by)
    placements = []
    free_rects = [{"x": 0, "y": 0, "width": sheet_width, "height": sheet_length}]

    for part in parts_sorted:
        placed = False
        for i, rect in enumerate(free_rects):
            for rotated in [False, True]:
                w, h = (part[0], part[1]) if not rotated else (part[1], part[0])
                if w <= rect["width"] and h <= rect["height"]:
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

def plot_placements_2d_matplotlib(placements, sheet_width, title="2D Cutting Layout"):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, sheet_width)

    # ใช้ความยาวที่ใช้จริง ไม่ต้อง +10
    max_y = max(p["y"] + p["height"] for p in placements)
    ax.set_ylim(0, max_y)

    # 🔹 กำหนดระยะ tick ของแกน Y ให้สม่ำเสมอ
    step = 10  # เปลี่ยนเป็น 20 ถ้าอยากให้ห่างกว่านี้
    y_ticks = list(range(0, int(max_y) + step, step))
    ax.set_yticks(y_ticks)

    # 🔸 วาดสี่เหลี่ยมแต่ละออเดอร์
    for p in placements:
        color = 'red' if p["rotated"] else 'blue'
        rect = plt.Rectangle(
            (p["x"], p["y"]), p["width"], p["height"],
            edgecolor='black', facecolor=color, linewidth=1.5
        )
        ax.add_patch(rect)
        ax.text(
            p["x"] + p["width"] / 2,
            p["y"] + p["height"] / 2,
            f'{int(p["width"])}x{int(p["height"])}',
            ha='center', va='center', fontsize=8, color='white'
        )

    ax.set_title(title)
    ax.set_xlabel("Width (cm)")
    ax.set_ylabel("Length (cm)")
    ax.invert_yaxis()  # แสดงจากบนลงล่างเหมือนในชีวิตจริง
    ax.grid(True)
    return fig
