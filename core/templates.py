# -*- coding: utf-8 -*-
"""Page templates for single and dual media-card layouts."""

import matplotlib.pyplot as plt

from core.style import COLORS, FIGSIZE, FONT_FAMILY, PAGE, SUMMARY_BAR

plt.rcParams["font.sans-serif"] = FONT_FAMILY
plt.rcParams["axes.unicode_minus"] = False


SINGLE_REGIONS = {
    "title": [PAGE["left"], 0.89, PAGE["content_width"], 0.055],
    "meta": [PAGE["left"], 0.848, PAGE["content_width"], 0.03],
    "summary": [PAGE["left"], 0.77, PAGE["content_width"], SUMMARY_BAR["height"]],
    "chart": [PAGE["left"], 0.36, PAGE["content_width"], 0.355],
    "conclusion": [PAGE["left"], 0.235, PAGE["content_width"], 0.06],
    "footer": [PAGE["left"], 0.065, PAGE["content_width"], 0.035],
}

DUAL_REGIONS = {
    "title": [PAGE["left"], 0.90, PAGE["content_width"], 0.05],
    "meta": [PAGE["left"], 0.862, PAGE["content_width"], 0.028],
    "summary": [PAGE["left"], 0.79, PAGE["content_width"], 0.06],
    "pe_chart": [PAGE["left"], 0.53, PAGE["content_width"], 0.18],
    "pb_chart": [PAGE["left"], 0.28, PAGE["content_width"], 0.18],
    "conclusion": [PAGE["left"], 0.165, PAGE["content_width"], 0.055],
    "footer": [PAGE["left"], 0.06, PAGE["content_width"], 0.03],
}


def _create_text_axis(fig, position):
    ax = fig.add_axes(position)
    ax.set_facecolor(COLORS["bg"])
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    return ax


def _create_chart_axis(fig, position):
    ax = fig.add_axes(position)
    ax.set_facecolor(COLORS["bg"])
    return ax


def create_single_template():
    """Create the single-indicator page skeleton."""
    fig = plt.figure(figsize=FIGSIZE, dpi=200, facecolor=COLORS["bg"])
    axes = {
        "title": _create_text_axis(fig, SINGLE_REGIONS["title"]),
        "meta": _create_text_axis(fig, SINGLE_REGIONS["meta"]),
        "summary": _create_text_axis(fig, SINGLE_REGIONS["summary"]),
        "chart": _create_chart_axis(fig, SINGLE_REGIONS["chart"]),
        "conclusion": _create_text_axis(fig, SINGLE_REGIONS["conclusion"]),
        "footer": _create_text_axis(fig, SINGLE_REGIONS["footer"]),
    }
    return fig, axes


def create_dual_template():
    """Create the dual-indicator page skeleton."""
    fig = plt.figure(figsize=FIGSIZE, dpi=200, facecolor=COLORS["bg"])
    axes = {
        "title": _create_text_axis(fig, DUAL_REGIONS["title"]),
        "meta": _create_text_axis(fig, DUAL_REGIONS["meta"]),
        "summary": _create_text_axis(fig, DUAL_REGIONS["summary"]),
        "pe_chart": _create_chart_axis(fig, DUAL_REGIONS["pe_chart"]),
        "pb_chart": _create_chart_axis(fig, DUAL_REGIONS["pb_chart"]),
        "conclusion": _create_text_axis(fig, DUAL_REGIONS["conclusion"]),
        "footer": _create_text_axis(fig, DUAL_REGIONS["footer"]),
    }
    return fig, axes
