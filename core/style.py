# -*- coding: utf-8 -*-
"""图片导出样式配置。"""

FIG_WIDTH_PX = 1600
FIG_HEIGHT_PX = 2000
FIG_DPI = 200
FIGSIZE = (FIG_WIDTH_PX / FIG_DPI, FIG_HEIGHT_PX / FIG_DPI)

COLORS = {
    "primary": "#1F3A5F",
    "secondary": "#16324F",
    "accent": "#F59E0B",
    "text": "#111827",
    "muted": "#6B7280",
    "grid": "#D1D5DB",
    "divider": "#E5E7EB",
    "bg": "#FFFFFF",
    "fill": "#EAF2FB",
}

FONT_FAMILY = ["Microsoft YaHei", "Source Han Sans SC", "SimHei", "Arial Unicode MS", "DejaVu Sans"]

FONT_SIZE = {
    "title": 19,
    "subtitle": 11,
    "summary_label": 10,
    "summary_value": 24,
    "summary_minor": 12,
    "body": 12,
    "caption": 9,
    "footer": 9,
}

LAYOUT = {
    "left": 0.055,
    "right": 0.965,
    "top": 0.975,
    "bottom": 0.04,
    "hspace": 0.34,
}

LINE_WIDTH = {
    "series": 2.6,
    "quantile": 1.05,
    "current": 2.8,
}

VALUATION_QUANTILES = [0.10, 0.25, 0.50, 0.75, 0.90]

CARD = {
    "radius": 0.028,
    "lw": 1.0,
    "pad": 0.012,
}
