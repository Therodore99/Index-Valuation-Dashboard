# -*- coding: utf-8 -*-
"""Unified design tokens for the media-card export system."""

FIG_WIDTH_PX = 1600
FIG_HEIGHT_PX = 2000
FIG_DPI = 200
FIGSIZE = (FIG_WIDTH_PX / FIG_DPI, FIG_HEIGHT_PX / FIG_DPI)

COLORS = {
    "primary": "#1E4E8C",
    "line": "#2459A6",
    "accent": "#F59E0B",
    "text": "#111827",
    "muted": "#6B7280",
    "grid": "#D1D5DB",
    "divider": "#E5E7EB",
    "bg": "#FFFFFF",
    "fill": "#DCE9F8",
    "summary_divider": "#6E8DBA",
}

FONT_FAMILY = [
    "Microsoft YaHei",
    "Source Han Sans SC",
    "SimHei",
    "Arial Unicode MS",
    "DejaVu Sans",
]

FONT_SIZE = {
    "title": 30,
    "meta": 15,
    "summary_main": 24,
    "summary_sub": 16,
    "section": 22,
    "conclusion": 19,
    "axis": 13,
    "footer": 13,
}

PAGE = {
    "left": 0.06,
    "right": 0.94,
    "content_width": 0.88,
}

SUMMARY_BAR = {
    "height": 0.075,
    "padding_x": 0.04,
}

CHART = {
    "fill_alpha": 0.7,
    "line_width": 2.9,
    "quantile_width": 1.0,
    "marker_size": 95,
    "x_margin": 0.015,
    "current_label_offset_right": (18, 18),
    "current_label_offset_left": (-86, 18),
}

VALUATION_QUANTILES = [0.10, 0.25, 0.50, 0.75, 0.90]

BRAND_TEXT = "@指数估值策略室"
