import matplotlib.pyplot as plt

def check_collision(placements, x, y, w, h):
    """ตรวจสอบว่าชิ้น (x, y, w, h) ชนกับชิ้นอื่นใน placements หรือไม่"""
    for p in placements:
        if not (x + w <= p['x'] or x >= p['x'] + p['width'] or
                y + h <= p['y'] or y >= p['y'] + p['height']):
            return True
    return False

def first_fit_decreasing_2d(parts, sheet_width):
    parts_sorted = sorted(parts, key=lambda x: max(x), reverse=True)
    placements = []

    for part in parts_sorted:
        placed = False
        for rotated in [False, True]:
            w, h = (part[0], part[1]) if not rotated else (part[1], part[0])

            for y in range(0, 10000):
                for x in range(0, int(sheet_width - w) + 1):
                    if not check_collision(placements, x, y, w, h):
                        placements.append({
                            "x": x,
                            "y": y,
                            "width": w,
                            "height": h,
                            "rotated": rotated
                        })
                        placed = True
                        break
                if placed:
                    break
            if placed:
                break

    return placements

def best_fit_decreasing_2d(parts, sheet_width):
    parts_sorted = sorted(parts, key=lambda x: max(x), reverse=True)
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

def guillotine_cutting_2d(parts, sheet_width):
    parts_sorted = sorted(parts, key=lambda x: max(x), reverse=True)
    placements = []
    free_rects = [{"x": 0, "y": 0, "width": sheet_width, "height": float('inf')}]  # เริ่มต้นมีแผ่นใหญ่ 1 แผ่น

    for part in parts_sorted:
        placed = False
        for i, rect in enumerate(free_rects):
            for rotated in [False, True]:
                w, h = (part[0], part[1]) if not rotated else (part[1], part[0])
                if w <= rect["width"] and h <= rect["height"]:
                    placement = {
                        "x": rect["x"],
                        "y": rect["y"],
                        "width": w,
                        "height": h,
                        "rotated": rotated
                    }
                    placements.append(placement)

                    right = {
                        "x": rect["x"] + w,
                        "y": rect["y"],
                        "width": rect["width"] - w,
                        "height": h
                    }
                    top = {
                        "x": rect["x"],
                        "y": rect["y"] + h,
                        "width": rect["width"],
                        "height": rect["height"] - h
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

def place_parts_free_rect(parts, sheet_width, sheet_length=float('inf')):
    placements = []
    free_rects = [{"x": 0, "y": 0, "width": sheet_width, "height": sheet_length}]

    for part in parts:
        placed = False

        for i, rect in enumerate(free_rects):
            for rotated in [False, True]:
                w, h = (part[0], part[1]) if not rotated else (part[1], part[0])
                if w <= rect["width"] and h <= rect["height"]:
                    placement = {
                        "x": rect["x"],
                        "y": rect["y"],
                        "width": w,
                        "height": h,
                        "rotated": rotated
                    }
                    placements.append(placement)

                    right_rect = {
                        "x": rect["x"] + w,
                        "y": rect["y"],
                        "width": rect["width"] - w,
                        "height": h
                    }
                    top_rect = {
                        "x": rect["x"],
                        "y": rect["y"] + h,
                        "width": rect["width"],
                        "height": rect["height"] - h
                    }

                    free_rects.pop(i)
                    if right_rect["width"] > 0 and right_rect["height"] > 0:
                        free_rects.append(right_rect)
                    if top_rect["width"] > 0 and top_rect["height"] > 0:
                        free_rects.append(top_rect)

                    placed = True
                    break
            if placed:
                break

    return placements

def plot_placements_2d_matplotlib(placements, sheet_width, title="2D Cutting Layout"):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, sheet_width)
    ax.set_ylim(0, max(p["y"] + p["height"] for p in placements) + 10)

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
    plt.gca().invert_yaxis()
    plt.grid(True)
    return fig
