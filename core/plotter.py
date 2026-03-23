# -*- coding: utf-8 -*-
"""Chart drawing primitives for the media-card export system."""

import matplotlib.dates as mdates
import pandas as pd

from core.style import CHART, COLORS, FONT_SIZE, VALUATION_QUANTILES


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
    """Use a single YYYY-MM format across all windows, only changing spacing."""
    span_days = max((x.iloc[-1] - x.iloc[0]).days, 1)
    if span_days <= 450:
        interval = 2
    elif span_days <= 1200:
        interval = 4
    elif span_days <= 2200:
        interval = 6
    else:
        interval = 12

    locator = mdates.MonthLocator(interval=interval)
    formatter = mdates.DateFormatter("%Y-%m")
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)


def _draw_quantile_lines(ax, values: pd.Series):
    quantiles = values.quantile(VALUATION_QUANTILES)
    configs = [
        ("10%分位", quantiles.iloc[0], True, 0.9),
        ("25%", quantiles.iloc[1], False, 0.55),
        ("50%分位", quantiles.iloc[2], True, 0.85),
        ("75%", quantiles.iloc[3], False, 0.55),
        ("90%分位", quantiles.iloc[4], True, 0.9),
    ]

    label_x = [0.014, 0.014, 0.024]
    label_idx = 0
    for label, level, show_label, alpha in configs:
        ax.axhline(level, color=COLORS["grid"], linestyle="--", linewidth=CHART["quantile_width"], alpha=alpha, zorder=1)
        if show_label:
            ax.text(
                label_x[label_idx],
                level,
                label,
                transform=ax.get_yaxis_transform(),
                fontsize=FONT_SIZE["axis"],
                color=COLORS["muted"],
                va="bottom",
            )
            label_idx += 1


def _draw_current_marker(ax, x: pd.Series, y: pd.Series, current_label: str):
    current_x = x.iloc[-1]
    current_y = float(y.iloc[-1])

    ax.scatter([current_x], [current_y], color=COLORS["accent"], s=CHART["marker_size"], zorder=4)

    x_num = mdates.date2num(x)
    ratio = (mdates.date2num(current_x) - x_num.min()) / max(x_num.max() - x_num.min(), 1)
    if ratio > 0.84:
        offset = CHART["current_label_offset_left"]
        ha = "right"
    else:
        offset = CHART["current_label_offset_right"]
        ha = "left"

    ax.annotate(
        current_label,
        (current_x, current_y),
        textcoords="offset points",
        xytext=offset,
        fontsize=FONT_SIZE["summary_sub"],
        color=COLORS["line"],
        weight="bold",
        ha=ha,
        va="bottom",
        zorder=5,
        clip_on=False,
    )


def plot_indicator_chart(ax, df: pd.DataFrame, chart_title: str, current_label: str, with_quantiles: bool) -> None:
    """Draw a single indicator chart with optional valuation quantile guides."""
    x = pd.to_datetime(df["date"])
    y = pd.to_numeric(df["value"], errors="coerce")

    _configure_axis(ax)
    _configure_time_axis(ax, x)

    if with_quantiles:
        _draw_quantile_lines(ax, y)

    ax.fill_between(x, y, y2=float(y.min()), color=COLORS["fill"], alpha=CHART["fill_alpha"], zorder=2)
    ax.plot(x, y, color=COLORS["line"], linewidth=CHART["line_width"], zorder=3)
    _draw_current_marker(ax, x, y, current_label)

    ax.set_title(chart_title, loc="left", fontsize=FONT_SIZE["section"], color=COLORS["primary"], weight="bold", pad=8)
    ax.margins(x=CHART["x_margin"])
