# -*- coding: utf-8 -*-
"""Chart drawing primitives for the media-card export system."""

import math

import matplotlib.dates as mdates
import pandas as pd

from core.style import CHART, COLORS, FONT_SIZE, SINGLE_LAYOUT, VALUATION_QUANTILES


def valuation_status(position_pct: float) -> str:
    """Map percentile to a normalized valuation label."""
    if position_pct < 10:
        return "极低估"
    if position_pct < 30:
        return "低估"
    if position_pct <= 70:
        return "中性"
    if position_pct <= 90:
        return "偏高"
    return "极高"


def _configure_axis(ax):
    ax.set_facecolor(COLORS["bg"])
    ax.grid(axis="y", color=COLORS["grid"], linewidth=0.8, alpha=0.45)

    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(COLORS["divider"])
    ax.spines["bottom"].set_color(COLORS["divider"])

    ax.tick_params(axis="x", labelsize=FONT_SIZE["axis"], colors=COLORS["muted"], length=0, pad=10)
    ax.tick_params(axis="y", labelsize=FONT_SIZE["axis"], colors=COLORS["muted"], length=0)
    ax.set_xlabel("")
    ax.set_ylabel("")


def _configure_time_axis(ax, x: pd.Series):
    span_days = max((x.iloc[-1] - x.iloc[0]).days, 1)
    if span_days <= 450:
        locator = mdates.MonthLocator(interval=2)
        formatter = mdates.DateFormatter("%Y-%m")
    elif span_days <= 1200:
        locator = mdates.MonthLocator(interval=4)
        formatter = mdates.DateFormatter("%Y-%m")
    else:
        locator = mdates.YearLocator(base=1)
        formatter = mdates.DateFormatter("%Y-%m")

    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)


def _draw_quantile_lines(ax, values: pd.Series):
    quantiles = values.quantile(VALUATION_QUANTILES)
    configs = [
        ("10%分位", quantiles.iloc[0], True, 0.85),
        ("25%", quantiles.iloc[1], False, 0.42),
        ("50%分位", quantiles.iloc[2], True, 0.75),
        ("75%", quantiles.iloc[3], False, 0.42),
        ("90%分位", quantiles.iloc[4], True, 0.85),
    ]

    label_x = [0.014, 0.020, 0.028]
    label_idx = 0
    for label, level, show_label, alpha in configs:
        ax.axhline(level, color=COLORS["grid"], linestyle="--", linewidth=CHART["quantile_width"], alpha=alpha, zorder=1)
        if show_label:
            ax.text(
                label_x[label_idx],
                level,
                label,
                transform=ax.get_yaxis_transform(),
                fontsize=FONT_SIZE["quantile_label"],
                color=COLORS["muted"],
                va="bottom",
            )
            label_idx += 1


def _adapt_single_chart_left_margin(ax):
    """Increase the single-chart left gutter only when y tick labels are too close to the page edge."""
    fig = ax.figure
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    labels = [label for label in ax.get_yticklabels() if label.get_text().strip()]
    if not labels:
        return

    min_left_px = min(label.get_window_extent(renderer=renderer).x0 for label in labels)
    fig_width_px = fig.bbox.width
    target_left_px = fig_width_px * SINGLE_LAYOUT["chart_safe_left"]

    if min_left_px >= target_left_px:
        return

    shift_px = (target_left_px - min_left_px) + SINGLE_LAYOUT["chart_label_padding_px"]
    shift_frac = min(shift_px / fig_width_px, SINGLE_LAYOUT["chart_max_left_shift"])

    pos = ax.get_position()
    max_shift_frac = max(pos.width - SINGLE_LAYOUT["chart_min_width"], 0.0)
    shift_frac = min(shift_frac, max_shift_frac)
    if shift_frac <= 0:
        return

    ax.set_position([pos.x0 + shift_frac, pos.y0, pos.width - shift_frac, pos.height])
    fig.canvas.draw()


def _point_to_segment_distance(px, py, ax, ay, bx, by):
    dx = bx - ax
    dy = by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    cx = ax + t * dx
    cy = ay + t * dy
    return math.hypot(px - cx, py - cy)


def _estimate_label_box(current_label: str):
    font_px = FONT_SIZE["current_label"] * 2.25
    width = max(102.0, len(current_label) * font_px * 0.52)
    height = max(24.0, font_px * 0.82)
    return width, height


def _build_candidate_box(point_x, point_y, offset, width, height, ha, va):
    anchor_x = point_x + offset[0]
    anchor_y = point_y + offset[1]

    if ha == "left":
        x0 = anchor_x
        x1 = anchor_x + width
    else:
        x0 = anchor_x - width
        x1 = anchor_x

    if va == "bottom":
        y0 = anchor_y
        y1 = anchor_y + height
    else:
        y0 = anchor_y - height
        y1 = anchor_y

    return x0, y0, x1, y1


def _score_candidate(label_box, axis_box, recent_points, recent_segments, priority, with_quantiles):
    x0, y0, x1, y1 = label_box
    ax0, ay0, ax1, ay1 = axis_box

    if x0 < ax0 or x1 > ax1 or y0 < ay0 or y1 > ay1:
        return 1_000_000 + priority * 10

    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    point_x, point_y = recent_points[-1]

    point_distance = math.hypot(cx - point_x, cy - point_y)
    ideal_distance = CHART["current_label_min_distance"] + 18
    score = abs(point_distance - ideal_distance) * 2.8 + point_distance * 0.6

    min_distance = min(
        (_point_to_segment_distance(cx, cy, sx, sy, ex, ey) for (sx, sy), (ex, ey) in recent_segments),
        default=9999.0,
    )
    if min_distance < 14:
        score += 2800
    elif min_distance < 24:
        score += 1100
    elif min_distance < 38:
        score += 380

    padding = 6
    for px, py in recent_points:
        if (x0 - padding) <= px <= (x1 + padding) and (y0 - padding) <= py <= (y1 + padding):
            score += 1200
            break

    if with_quantiles and x0 < ax0 + CHART["quantile_label_safe_left"]:
        score += 260

    score += priority * 6
    return score


def _draw_current_marker(ax, x: pd.Series, y: pd.Series, current_label: str, with_quantiles: bool):
    current_x = x.iloc[-1]
    current_y = float(y.iloc[-1])
    ax.scatter([current_x], [current_y], color=COLORS["accent"], s=CHART["marker_size"], zorder=4)

    if not current_label:
        return

    ax.figure.canvas.draw()

    display_points = ax.transData.transform(list(zip(mdates.date2num(x), y)))
    point_x, point_y = display_points[-1]
    axis_box = ax.get_window_extent().extents
    label_width, label_height = _estimate_label_box(current_label)

    offset_cfg = CHART["current_label_candidate_offsets"]
    candidates = [
        ("right_up", offset_cfg["right_up"], "left", "bottom", 0),
        ("left_up", offset_cfg["left_up"], "right", "bottom", 1),
        ("right_down", offset_cfg["right_down"], "left", "top", 2),
        ("left_down", offset_cfg["left_down"], "right", "top", 3),
    ]

    recent_points = [tuple(p) for p in display_points[-8:]]
    recent_segments = list(zip(recent_points[:-1], recent_points[1:]))

    best = None
    for name, offset, ha, va, priority in candidates:
        label_box = _build_candidate_box(point_x, point_y, offset, label_width, label_height, ha, va)
        score = _score_candidate(label_box, axis_box, recent_points, recent_segments, priority, with_quantiles)
        if best is None or score < best[0]:
            best = (score, name, offset, ha, va)

    _, _, offset, ha, va = best
    ax.annotate(
        current_label,
        (current_x, current_y),
        textcoords="offset points",
        xytext=offset,
        fontsize=FONT_SIZE["current_label"],
        color=COLORS["line"],
        weight="bold",
        ha=ha,
        va=va,
        zorder=5,
        clip_on=False,
    )


def _draw_chart_summary(ax, summary_segments=None, accent_indices=None):
    if not summary_segments:
        return

    accent_indices = accent_indices or set()
    count = len(summary_segments)
    if count == 0:
        return

    center = 0.5
    gap = CHART["dual_chart_summary_gap"]
    if count == 1:
        positions = [center]
    elif count == 2:
        positions = [center - gap / 2, center + gap / 2]
    elif count == 3:
        positions = [center - gap, center, center + gap]
    else:
        positions = [0.20, 0.40, 0.60, 0.80]

    for i in range(1, len(positions)):
        divider_x = (positions[i - 1] + positions[i]) / 2
        ax.text(
            divider_x,
            CHART["dual_chart_summary_y"],
            "|",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=FONT_SIZE["dual_chart_summary"],
            color=COLORS["muted"],
            clip_on=False,
        )

    for idx, (xp, text) in enumerate(zip(positions, summary_segments)):
        ax.text(
            xp,
            CHART["dual_chart_summary_y"],
            text,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=FONT_SIZE["dual_chart_summary"],
            color=COLORS["accent"] if idx in accent_indices else COLORS["text"],
            weight="bold",
            clip_on=False,
        )


def plot_indicator_chart(
    ax,
    df: pd.DataFrame,
    chart_title: str,
    current_label: str,
    with_quantiles: bool,
    chart_summary_segments=None,
    chart_summary_accent_indices=None,
    adaptive_left_margin: bool = False,
) -> None:
    x = pd.to_datetime(df["date"])
    y = pd.to_numeric(df["value"], errors="coerce")

    _configure_axis(ax)
    _configure_time_axis(ax, x)

    if with_quantiles:
        _draw_quantile_lines(ax, y)

    ax.fill_between(x, y, y2=float(y.min()), color=COLORS["fill"], alpha=CHART["fill_alpha"], zorder=2)
    ax.plot(x, y, color=COLORS["line"], linewidth=CHART["line_width"], zorder=3)
    ax.margins(x=CHART["x_margin"])

    if adaptive_left_margin:
        _adapt_single_chart_left_margin(ax)

    _draw_current_marker(ax, x, y, current_label, with_quantiles)

    title_pad = CHART["dual_chart_title_pad"] if chart_summary_segments else 8
    ax.set_title(chart_title, loc="left", fontsize=FONT_SIZE["section"], color=COLORS["primary"], weight="bold", pad=title_pad)
    _draw_chart_summary(ax, chart_summary_segments, chart_summary_accent_indices)



