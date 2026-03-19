# -*- coding: utf-8 -*-
"""基础绘图能力：卡片化区块 + 图表绘制。"""

from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.patches as patches
import pandas as pd

from core.style import CARD, COLORS, FONT_SIZE, LINE_WIDTH, VALUATION_QUANTILES


def turn_off_axis(ax):
    ax.set_facecolor(COLORS["bg"])
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def draw_card(ax, facecolor: str = COLORS["bg"]):
    """在轴内绘制浅色卡片底，增强成品感。"""
    turn_off_axis(ax)
    card = patches.FancyBboxPatch(
        (0.0, 0.0),
        1.0,
        1.0,
        boxstyle=f"round,pad={CARD['pad']},rounding_size={CARD['radius']}",
        linewidth=CARD["lw"],
        edgecolor=COLORS["divider"],
        facecolor=facecolor,
        transform=ax.transAxes,
        zorder=0,
    )
    ax.add_patch(card)


def valuation_status(position_pct: float) -> str:
    if position_pct < 10:
        return "极低估"
    if position_pct < 30:
        return "低估"
    if position_pct <= 70:
        return "中性"
    if position_pct <= 90:
        return "偏高"
    return "极高"


def render_title(ax, title: str, subtitle: str):
    draw_card(ax, COLORS["bg"])
    ax.add_patch(
        patches.FancyBboxPatch(
            (0.0, 0.84),
            0.22,
            0.10,
            boxstyle="round,pad=0.005,rounding_size=0.02",
            linewidth=0,
            facecolor=COLORS["fill"],
            transform=ax.transAxes,
            zorder=1,
        )
    )
    ax.text(0.03, 0.88, "INDEX SNAPSHOT", fontsize=FONT_SIZE["caption"], color=COLORS["primary"], weight="bold")
    ax.text(0.03, 0.58, title, fontsize=FONT_SIZE["title"], color=COLORS["secondary"], weight="bold")
    ax.text(0.03, 0.28, subtitle, fontsize=FONT_SIZE["subtitle"], color=COLORS["muted"])
    ax.plot([0.03, 0.97], [0.12, 0.12], color=COLORS["divider"], linewidth=1.0, transform=ax.transAxes)


def _summary_block(ax, x0: float, title: str, value: str, extra: str = "", accent: bool = False):
    face = COLORS["fill"] if accent else COLORS["bg"]
    edge = COLORS["divider"]
    ax.add_patch(
        patches.FancyBboxPatch(
            (x0, 0.16),
            0.30,
            0.68,
            boxstyle="round,pad=0.01,rounding_size=0.03",
            linewidth=1.0,
            edgecolor=edge,
            facecolor=face,
            transform=ax.transAxes,
            zorder=1,
        )
    )
    ax.text(x0 + 0.03, 0.69, title, fontsize=FONT_SIZE["summary_label"], color=COLORS["muted"], transform=ax.transAxes)
    ax.text(x0 + 0.03, 0.44, value, fontsize=FONT_SIZE["summary_value"], color=COLORS["text"], weight="bold", transform=ax.transAxes)
    if extra:
        ax.text(x0 + 0.03, 0.24, extra, fontsize=FONT_SIZE["summary_minor"], color=COLORS["primary"], transform=ax.transAxes)


def render_single_summary(ax, metrics: dict, indicator_key: str):
    draw_card(ax, COLORS["bg"])
    if indicator_key in {"pe", "pb"}:
        _summary_block(ax, 0.02, "当前", f"{metrics['current_value']:.2f}", f"分位 {metrics['position_pct']:.0f}%", accent=True)
        _summary_block(ax, 0.35, "状态", valuation_status(metrics["position_pct"]), "估值区间")
        _summary_block(ax, 0.68, "区间", f"{metrics['min_value']:.2f}-{metrics['max_value']:.2f}", f"样本 {metrics['sample_count']}")
    else:
        _summary_block(ax, 0.02, "当前点位", f"{metrics['current_value']:.2f}", f"区间位置 {metrics['position_pct']:.1f}%", accent=True)
        _summary_block(ax, 0.35, "区间低点", f"{metrics['min_value']:.2f}")
        _summary_block(ax, 0.68, "区间高点", f"{metrics['max_value']:.2f}")


def _draw_quantile_lines(ax, values: pd.Series):
    q_values = values.quantile(VALUATION_QUANTILES)
    labels = ["10%", "25%", "50%", "75%", "90%"]
    for label, q in zip(labels, q_values.values):
        ax.axhline(q, color=COLORS["grid"], linewidth=LINE_WIDTH["quantile"], linestyle="--", zorder=1)
        ax.text(
            1.01,
            q,
            label,
            transform=ax.get_yaxis_transform(),
            fontsize=FONT_SIZE["caption"],
            color=COLORS["muted"],
            va="center",
            ha="left",
        )


def render_indicator_chart(ax, df: pd.DataFrame, metrics: dict, indicator_key: str, indicator_name: str):
    ax.set_facecolor(COLORS["bg"])
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(COLORS["divider"])
    ax.spines["bottom"].set_color(COLORS["divider"])

    x = pd.to_datetime(df["date"])
    y = pd.to_numeric(df["value"], errors="coerce")

    ax.grid(axis="y", color=COLORS["grid"], linewidth=0.8, alpha=0.8)
    ax.plot(x, y, color=COLORS["primary"], linewidth=LINE_WIDTH["series"], zorder=2)

    if indicator_key in {"pe", "pb"}:
        _draw_quantile_lines(ax, y)
        point_text = f"当前：{float(y.iloc[-1]):.2f}（{metrics['position_pct']:.0f}%）"
    else:
        point_text = f"当前：{float(y.iloc[-1]):.2f}"

    current_x = x.iloc[-1]
    current_y = float(y.iloc[-1])
    ax.scatter([current_x], [current_y], color=COLORS["accent"], s=58, zorder=4)

    x_ratio = 0.88
    try:
        x_num = mdates.date2num(x)
        x_ratio = (mdates.date2num(current_x) - x_num.min()) / max(x_num.max() - x_num.min(), 1)
    except Exception:
        pass
    offset = (-120, 10) if x_ratio > 0.82 else (10, 10)

    ax.annotate(
        point_text,
        (current_x, current_y),
        textcoords="offset points",
        xytext=offset,
        fontsize=FONT_SIZE["body"],
        color=COLORS["text"],
        bbox=dict(boxstyle="round,pad=0.30", fc=COLORS["bg"], ec=COLORS["divider"]),
        zorder=5,
    )

    ax.set_title(f"{indicator_name} 走势", fontsize=FONT_SIZE["summary_minor"], color=COLORS["secondary"], loc="left", pad=8)
    ax.tick_params(axis="x", labelsize=FONT_SIZE["caption"], colors=COLORS["muted"])
    ax.tick_params(axis="y", labelsize=FONT_SIZE["caption"], colors=COLORS["muted"])
    ax.margins(x=0.04)


def render_single_conclusion(ax, indicator_key: str, metrics: dict):
    draw_card(ax, COLORS["fill"])

    if indicator_key in {"pe", "pb"}:
        pct = metrics["position_pct"]
        if pct < 30:
            text = "结论：分位偏低，估值处于低估区，关注后续修复空间。"
        elif pct <= 70:
            text = "结论：分位中性，估值大体均衡，维持观察节奏。"
        else:
            text = "结论：分位偏高，估值压力抬升，注意波动风险。"
    else:
        text = f"结论：当前位于近一年区间 {metrics['position_pct']:.1f}% 位置，体现阶段位置特征。"

    ax.text(0.03, 0.58, text, fontsize=FONT_SIZE["body"], color=COLORS["text"], transform=ax.transAxes)


def render_dual_summary(ax, pe_metrics: dict, pb_metrics: dict):
    draw_card(ax, COLORS["bg"])
    _summary_block(
        ax,
        0.02,
        "PE",
        f"{pe_metrics['current_value']:.2f}",
        f"{pe_metrics['position_pct']:.0f}% · {valuation_status(pe_metrics['position_pct'])}",
        accent=True,
    )
    _summary_block(
        ax,
        0.35,
        "PB",
        f"{pb_metrics['current_value']:.2f}",
        f"{pb_metrics['position_pct']:.0f}% · {valuation_status(pb_metrics['position_pct'])}",
        accent=True,
    )
    _summary_block(ax, 0.68, "定位", "估值双因子", "同口径并列观察")


def render_dual_conclusion(ax, pe_metrics: dict, pb_metrics: dict):
    draw_card(ax, COLORS["fill"])

    def _short(pct: float) -> str:
        if pct < 30:
            return "低估"
        if pct <= 70:
            return "中性"
        return "偏高"

    text = f"统一结论：PE {_short(pe_metrics['position_pct'])}，PB {_short(pb_metrics['position_pct'])}，整体估值处于可跟踪区间。"
    ax.text(0.03, 0.58, text, fontsize=FONT_SIZE["body"], color=COLORS["text"], transform=ax.transAxes)


def render_footer(ax, start_date, end_date):
    turn_off_axis(ax)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    footer = (
        f"数据区间：{start_date:%Y-%m-%d} ~ {end_date:%Y-%m-%d}  |  数据源：iFinD  |  生成：{generated}"
    )
    ax.text(0.01, 0.12, footer, fontsize=FONT_SIZE["footer"], color=COLORS["muted"], transform=ax.transAxes)
