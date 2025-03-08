import numpy as np
import random
import matplotlib.pyplot as plt

def sort_parts(parts, strategy):
    """Sort parts based on the given strategy."""
    if strategy == 'area':
        return sorted(parts, key=lambda x: x[0] * x[1], reverse=True)
    elif strategy == 'max_side':
        return sorted(parts, key=lambda x: max(x), reverse=True)
    return parts

def first_fit_decreasing_rotated(sheet_width, parts, sort_by="max_side"):
    """FFD algorithm with rotation support."""
    parts = sort_parts(parts, sort_by)
    bins = []

    for part in parts:
        w, h = part if part[0] <= part[1] else (part[1], part[0])
        placed = False

        for bin in bins:
            if sum(p[0] for p in bin) + w <= sheet_width:
                bin.append((w, h))
                placed = True
                break

        if not placed:
            bins.append([(w, h)])

    return bins

def best_fit_decreasing_rotated(sheet_width, parts, sort_by="max_side"):
    """BFD algorithm with rotation support."""
    parts = sort_parts(parts, sort_by)
    bins = []

    for part in parts:
        w, h = part if part[0] <= part[1] else (part[1], part[0])
        best_bin = None
        min_space_left = float('inf')

        for bin in bins:
            space_left = sheet_width - sum(p[0] for p in bin)
            if space_left >= w and space_left < min_space_left:
                best_bin = bin
                min_space_left = space_left

        if best_bin is not None:
            best_bin.append((w, h))
        else:
            bins.append([(w, h)])

    return bins

def guillotine_cutting_rotated(sheet_width, parts, sort_by="max_side"):
    """Guillotine Cutting algorithm with rotation support."""
    parts = sort_parts(parts, sort_by)
    rows = []
    remaining_parts = parts.copy()

    while remaining_parts:
        row_parts, row_height = [], 0
        row_width = 0
        for part in remaining_parts[:]:
            w, h = part if part[0] <= part[1] else (part[1], part[0])
            if row_width + w <= sheet_width:
                row_parts.append((w, h))
                row_width += w
                row_height = max(row_height, h)
                remaining_parts.remove(part)

        rows.append(row_parts)

    return rows

def plot_placements_shelf_matplotlib(bins, sheet_width, title):
    """Visualize the cutting layout."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, sheet_width)
    y_offset = 0

    for bin in bins:
        x_offset = 0
        max_height = max(h for _, h in bin)

        for w, h in bin:
            rect = plt.Rectangle((x_offset, y_offset), w, h, edgecolor='black', facecolor=np.random.rand(3,))
            ax.add_patch(rect)
            ax.text(x_offset + w / 2, y_offset + h / 2, f"{w}x{h}", ha='center', va='center', fontsize=8, color='white')
            x_offset += w

        y_offset += max_height

    ax.set_ylim(0, y_offset)
    ax.set_xlabel("Width")
    ax.set_ylabel("Length")
    ax.set_title(title)
    plt.gca().invert_yaxis()
    return fig
