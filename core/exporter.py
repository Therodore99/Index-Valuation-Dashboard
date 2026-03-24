# -*- coding: utf-8 -*-
"""Export orchestration for single and dual media-card charts."""

import re
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from core import plotter
from core.style import BRAND_TEXT, COLORS, DIVIDER, FONT_SIZE, SUMMARY_BAR
from core.templates import DUAL_REGIONS, create_dual_template, create_single_template
from utils.file_utils import build_dual_output_path, build_output_path, ensure_dir


def _window_label(window_tag: str) -> str:
    match = re.match(r"^(\d+(?:\.\d+)?)y$", window_tag.lower())
    if not match:
        return window_tag

    value = float(match.group(1))
    if abs(value - int(value)) < 1e-9:
        return f"{int(value)}年"
    return f"{value:g}年"


def _meta_line(end_date, indicator_key: str, window_label: str) -> str:
    suffix = f"近{window_label}滚动分位" if indicator_key in {"pe", "pb"} else f"近{window_label}区间观察"
    return f"截至 {end_date:%Y-%m-%d} ｜ 数据来源：同花顺iFinD ｜ {suffix}"


def _single_title(index_name: str, indicator_name: str, indicator_key: str, window_label: str) -> str:
    if indicator_key in {"pe", "pb"}:
        return f"{index_name}近{window_label}{indicator_name}估值"
    return f"{index_name}近{window_label}{indicator_name}相对位置"


def _dual_title(index_name: str, window_label: str) -> str:
    return f"{index_name}近{window_label}估值概览"


def _render_text_line(ax, text: str, fontsize: int, color: str, weight: str = "normal") -> None:
    ax.text(0.5, 0.5, text, ha="center", va="center", fontsize=fontsize, color=color, weight=weight)


def _prepare_summary_axis(ax):
    ax.set_facecolor(COLORS["bg"])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.add_patch(
        Rectangle((0.0, 0.0), 1.0, 1.0, transform=ax.transAxes, facecolor=COLORS["primary"], edgecolor=COLORS["primary"], zorder=0)
    )


def _render_single_summary_bar(ax, indicator_key: str, indicator_name: str, metrics: dict) -> None:
    _prepare_summary_axis(ax)

    if indicator_key in {"pe", "pb"}:
        segments = [f"当前 {metrics['current_value']:.2f}", f"{metrics['position_pct']:.1f}%分位", plotter.valuation_status(metrics["position_pct"])]
        accent_indices = {2}
        dividers = [1 / 3, 2 / 3]
        centers = [1 / 6, 0.5, 5 / 6]
    else:
        segments = [f"当前 {metrics['current_value']:.2f}", f"区间位置 {metrics['position_pct']:.1f}%"]
        accent_indices = set()
        dividers = [0.5]
        centers = [0.25, 0.75]

    for x in dividers:
        ax.plot([x, x], [0.2, 0.8], color=COLORS["summary_divider"], linewidth=SUMMARY_BAR["divider_width"], transform=ax.transAxes, zorder=1)

    for idx, text in enumerate(segments):
        ax.text(
            centers[idx],
            0.5,
            text,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=FONT_SIZE["summary_main"],
            color=COLORS["accent"] if idx in accent_indices else COLORS["bg"],
            weight="bold",
            clip_on=False,
            zorder=2,
        )


def _clear_dual_summary_axis(ax):
    ax.set_facecolor(COLORS["bg"])
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def _render_dual_dividers(fig):
    """Draw faint structural dividers for the dual-indicator layout."""
    left = DIVIDER["left"]
    right = DIVIDER["right"]
    y_positions = [
        DUAL_REGIONS["summary"][1] + DUAL_REGIONS["summary"][3] / 2,
        (DUAL_REGIONS["pe_chart"][1] + (DUAL_REGIONS["pb_chart"][1] + DUAL_REGIONS["pb_chart"][3])) / 2,
        (DUAL_REGIONS["pb_chart"][1] + DUAL_REGIONS["footer"][1] + DUAL_REGIONS["footer"][3]) / 2,
    ]

    for y in y_positions:
        fig.add_artist(
            Line2D(
                [left, right],
                [y, y],
                transform=fig.transFigure,
                color=DIVIDER["color"],
                alpha=DIVIDER["alpha"],
                linewidth=DIVIDER["line_width"],
                zorder=0,
            )
        )


def _measure_text_width(ax, text: str, fontsize: int, renderer) -> float:
    """Measure text width in pixels inside the given axis."""
    probe = ax.text(0.0, 0.0, text, fontsize=fontsize, alpha=0.0, transform=ax.transAxes)
    width = probe.get_window_extent(renderer=renderer).width
    probe.remove()
    return width


def _split_token_by_width(ax, token: str, fontsize: int, max_width_px: float, renderer) -> list[str]:
    """Split an overlong token by characters so each piece can fit the line width."""
    pieces = []
    current = ""
    for char in token:
        trial = current + char
        if not current or _measure_text_width(ax, trial, fontsize, renderer) <= max_width_px:
            current = trial
        else:
            pieces.append(current)
            current = char

    if current:
        pieces.append(current)
    return pieces


def _fit_text_to_width(ax, text: str, fontsize: int, max_width_px: float, renderer) -> str:
    """Trim the last line with an ellipsis when the remaining text still cannot fit."""
    if _measure_text_width(ax, text, fontsize, renderer) <= max_width_px:
        return text

    fitted = ""
    for char in text:
        trial = fitted + char
        if _measure_text_width(ax, trial + "…", fontsize, renderer) <= max_width_px:
            fitted = trial
        else:
            break

    if not fitted:
        return text[:1]
    return fitted + "…"


def _wrap_conclusion_text(ax, text: str, fontsize: int, max_width_ratio: float = 0.94, max_lines: int = 3) -> str:
    """Wrap single-indicator conclusions against the actual conclusion-axis width."""
    ax.figure.canvas.draw()
    renderer = ax.figure.canvas.get_renderer()
    max_width_px = ax.get_window_extent(renderer=renderer).width * max_width_ratio

    tokens = [token for token in re.split(r"(?<=[，。；：、])", text) if token]
    units = []
    for token in tokens:
        if _measure_text_width(ax, token, fontsize, renderer) <= max_width_px:
            units.append(token)
        else:
            units.extend(_split_token_by_width(ax, token, fontsize, max_width_px, renderer))

    lines = []
    current = ""
    for idx, unit in enumerate(units):
        trial = current + unit
        if not current:
            current = unit
            continue

        if _measure_text_width(ax, trial, fontsize, renderer) <= max_width_px:
            current = trial
            continue

        lines.append(current.strip())
        current = unit

        if max_lines and len(lines) >= max_lines - 1:
            remaining = current + "".join(units[idx + 1 :])
            lines.append(_fit_text_to_width(ax, remaining.strip(), fontsize, max_width_px, renderer))
            return "\n".join(lines)

    if current:
        lines.append(current.strip())

    return "\n".join(lines[:max_lines] if max_lines else lines)


def _single_close_conclusion(window_label: str, metrics: dict) -> str:
    position_pct = metrics["position_pct"]
    # if position_pct < 20:
    #     lead = f"当前点位已靠近近{window_label}区间下沿，更反映阶段位置偏弱，不直接代表估值高低。"
    # elif position_pct < 40:
    #     lead = f"当前点位位于近{window_label}偏低区域，更适合作为阶段位置观察，而不是单独判断便宜或昂贵。"
    # elif position_pct <= 60:
    #     lead = f"当前点位处于近{window_label}区间中部，阶段位置相对均衡，更适合继续跟踪方向选择。"
    # elif position_pct <= 80:
    #     lead = f"当前点位已回到近{window_label}偏高区域，说明阶段位置已有修复，但位置本身不等同于高估。"
    # else:
    #     lead = f"当前点位接近近{window_label}区间上沿，更多体现阶段位置偏强，仍需与估值判断分开看待。"

    tail = f"近{window_label}观察区间约为{metrics['min_value']:.2f}-{metrics['max_value']:.2f}。"
    return tail


def _single_valuation_conclusion(indicator_name: str, window_label: str, metrics: dict) -> str:
    position_pct = metrics["position_pct"]
    if position_pct < 10:
        return f"当前{indicator_name}已进入近{window_label}极低区间，市场定价明显偏谨慎，后续更值得跟踪修复弹性。"
    if position_pct < 30:
        return f"当前{indicator_name}位于近{window_label}偏低区间，若预期改善，后续更值得关注修复空间。"
    if position_pct <= 70:
        return f"当前{indicator_name}仍处于近{window_label}中低至中性区间，市场定价相对克制，更应观察修复而非扩张。"
    if position_pct <= 90:
        return f"当前{indicator_name}已进入近{window_label}偏高区间，后续更需要观察业绩兑现对估值的消化能力。"
    return f"当前{indicator_name}处于近{window_label}较高区间，后续更应关注预期兑现与估值压缩的平衡。"


def _single_conclusion(indicator_key: str, indicator_name: str, metrics: dict, window_label: str) -> str:
    if indicator_key in {"pe", "pb"}:
        return _single_valuation_conclusion(indicator_name, window_label, metrics)
    return _single_close_conclusion(window_label, metrics)


def _dual_chart_summary_segments(metrics: dict):
    return [f"当前 {metrics['current_value']:.2f}", f"{metrics['position_pct']:.1f}%分位", plotter.valuation_status(metrics['position_pct'])], {2}


def _render_footer(ax, start_date, end_date) -> None:
    ax.set_facecolor(COLORS["bg"])
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    left = f"统计周期：{start_date:%Y-%m-%d} ~ {end_date:%Y-%m-%d} ｜ 发布时间不足5年的指数均使用上市以来数据"
    ax.text(0.0, 0.5, left, ha="left", va="center", fontsize=FONT_SIZE["footer"], color=COLORS["muted"])
    ax.text(1.0, 0.5, BRAND_TEXT, ha="right", va="center", fontsize=FONT_SIZE["footer"], color=COLORS["muted"])


def export_single_indicator(
    index_key: str,
    index_name: str,
    indicator_key: str,
    indicator_name: str,
    df,
    metrics: dict,
    output_dir: Path,
    window_tag: str,
) -> Path:
    output_path = build_output_path(output_dir, index_key, indicator_key, window_tag)
    ensure_dir(output_path.parent)

    fig, axes = create_single_template()
    window_label = _window_label(window_tag)

    _render_text_line(axes["title"], _single_title(index_name, indicator_name, indicator_key, window_label), FONT_SIZE["title"], COLORS["primary"], weight="bold")
    _render_text_line(axes["meta"], _meta_line(metrics["end_date"], indicator_key, window_label), FONT_SIZE["meta"], COLORS["muted"])

    _render_single_summary_bar(axes["summary"], indicator_key, indicator_name, metrics)

    plotter.plot_indicator_chart(
        axes["chart"],
        df,
        chart_title=indicator_name,
        current_label=f"当前 {metrics['current_value']:.2f}",
        with_quantiles=indicator_key in {"pe", "pb"},
        adaptive_left_margin=True,
    )

    conclusion_text = _single_conclusion(indicator_key, indicator_name, metrics, window_label)
    wrapped_conclusion = _wrap_conclusion_text(axes["conclusion"], conclusion_text, FONT_SIZE["conclusion"], max_width_ratio=0.95, max_lines=3)
    axes["conclusion"].text(
        0.0,
        0.5,
        wrapped_conclusion,
        ha="left",
        va="center",
        fontsize=FONT_SIZE["conclusion"],
        color=COLORS["text"],
        linespacing=1.35,
        wrap=False,
    )
    _render_footer(axes["footer"], metrics["start_date"], metrics["end_date"])

    fig.savefig(output_path, facecolor=fig.get_facecolor())
    plt.close(fig)
    return output_path


def export_pe_pb_combo(
    index_key: str,
    index_name: str,
    pe_df,
    pe_metrics: dict,
    pb_df,
    pb_metrics: dict,
    output_dir: Path,
    window_tag: str,
) -> Path:
    output_path = build_dual_output_path(output_dir, index_key, window_tag)
    ensure_dir(output_path.parent)

    fig, axes = create_dual_template()
    window_label = _window_label(window_tag)
    dual_end_date = max(pe_metrics["end_date"], pb_metrics["end_date"])

    _render_text_line(axes["title"], _dual_title(index_name, window_label), FONT_SIZE["title"] + 2, COLORS["primary"], weight="bold")
    _render_text_line(axes["meta"], _meta_line(dual_end_date, "pe", window_label), FONT_SIZE["meta"], COLORS["muted"])
    _clear_dual_summary_axis(axes["summary"])
    _render_dual_dividers(fig)

    pe_segments, pe_accent = _dual_chart_summary_segments(pe_metrics)
    pb_segments, pb_accent = _dual_chart_summary_segments(pb_metrics)

    plotter.plot_indicator_chart(
        axes["pe_chart"],
        pe_df,
        chart_title="PE",
        current_label=f"当前 {pe_metrics['current_value']:.2f}",
        with_quantiles=True,
        chart_summary_segments=pe_segments,
        chart_summary_accent_indices=pe_accent,
    )
    plotter.plot_indicator_chart(
        axes["pb_chart"],
        pb_df,
        chart_title="PB",
        current_label=f"当前 {pb_metrics['current_value']:.2f}",
        with_quantiles=True,
        chart_summary_segments=pb_segments,
        chart_summary_accent_indices=pb_accent,
    )

    start_date = max(pe_metrics["start_date"], pb_metrics["start_date"])
    end_date = min(pe_metrics["end_date"], pb_metrics["end_date"])
    _render_footer(axes["footer"], start_date, end_date)

    fig.savefig(output_path, facecolor=fig.get_facecolor())
    plt.close(fig)
    return output_path

