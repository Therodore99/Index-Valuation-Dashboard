# -*- coding: utf-8 -*-
"""图片模板布局定义。"""

import matplotlib.pyplot as plt

from core.style import COLORS, FIGSIZE, FONT_FAMILY, LAYOUT

plt.rcParams["font.sans-serif"] = FONT_FAMILY
plt.rcParams["axes.unicode_minus"] = False


def create_single_template():
    """单指标图固定结构：标题、摘要、图表、结论、页脚。"""
    fig = plt.figure(figsize=FIGSIZE, dpi=200, facecolor=COLORS["bg"])
    gs = fig.add_gridspec(5, 1, height_ratios=[0.17, 0.20, 0.40, 0.15, 0.08])
    axes = {
        "title": fig.add_subplot(gs[0]),
        "summary": fig.add_subplot(gs[1]),
        "chart": fig.add_subplot(gs[2]),
        "conclusion": fig.add_subplot(gs[3]),
        "footer": fig.add_subplot(gs[4]),
    }
    fig.subplots_adjust(
        left=LAYOUT["left"],
        right=LAYOUT["right"],
        top=LAYOUT["top"],
        bottom=LAYOUT["bottom"],
        hspace=LAYOUT["hspace"],
    )
    return fig, axes


def create_dual_template():
    """双指标图固定结构：标题、统一摘要、PE、PB、结论、页脚。"""
    fig = plt.figure(figsize=FIGSIZE, dpi=200, facecolor=COLORS["bg"])
    gs = fig.add_gridspec(6, 1, height_ratios=[0.14, 0.15, 0.24, 0.24, 0.15, 0.08])
    axes = {
        "title": fig.add_subplot(gs[0]),
        "summary": fig.add_subplot(gs[1]),
        "pe_chart": fig.add_subplot(gs[2]),
        "pb_chart": fig.add_subplot(gs[3]),
        "conclusion": fig.add_subplot(gs[4]),
        "footer": fig.add_subplot(gs[5]),
    }
    fig.subplots_adjust(
        left=LAYOUT["left"],
        right=LAYOUT["right"],
        top=LAYOUT["top"],
        bottom=LAYOUT["bottom"],
        hspace=LAYOUT["hspace"],
    )
    return fig, axes
