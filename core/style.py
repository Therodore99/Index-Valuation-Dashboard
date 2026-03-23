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
    "chart_subtitle": 17,
    "current_label": 14,
    "dual_chart_summary": 17,
    "conclusion": 19,
    "axis": 13,
    "quantile_label": 12,
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
    "divider_width": 1.0,
}

CHART = {
    "fill_alpha": 0.7,
    "line_width": 2.9,
    "quantile_width": 1.0,
    "marker_size": 95,
    "x_margin": 0.015,
    "current_label_min_distance": 18,
    "current_label_candidate_offsets": {
        "right_up": (14, 16),
        "left_up": (-14, 16),
        "right_down": (14, -16),
        "left_down": (-14, -16),
    },
    "dual_chart_summary_y": 1.045,
    "dual_chart_summary_gap": 0.27,
    "dual_chart_title_pad": 22,
    "quantile_label_safe_left": 118,
}

DUAL_LAYOUT = {
    "title_y": 0.913,
    "title_h": 0.043,
    "meta_y": 0.879,
    "meta_h": 0.022,
    "top_divider_y": 0.842,
    "top_divider_h": 0.012,
    "pe_chart_y": 0.562,
    "pe_chart_h": 0.250,
    "pb_chart_y": 0.272,
    "pb_chart_h": 0.200,
    "conclusion_y": 0.157,
    "conclusion_h": 0.05,
    "footer_y": 0.068,
    "footer_h": 0.028,
}

DIVIDER = {
    "color": "#E5E7EB",
    "alpha": 0.62,
    "line_width": 0.8,
    "left": 0.11,
    "right": 0.89,
}

VALUATION_QUANTILES = [0.10, 0.25, 0.50, 0.75, 0.90]

BRAND_TEXT = "@指数估值策略室"
