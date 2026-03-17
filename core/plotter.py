# -*- coding: utf-8 -*-
"""区间位置图绘制模块。"""

from pathlib import Path

import matplotlib.pyplot as plt

from utils.file_utils import ensure_dir

# 优先使用 Windows 常见中文字体，提升中文标题可读性。
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def generate_position_chart(metrics: dict, title: str, output_path: Path) -> None:
    """绘制横向区间位置图并保存。"""
    ensure_dir(output_path.parent)

    min_value = metrics["min_value"]
    max_value = metrics["max_value"]
    current_value = metrics["current_value"]

    fig, ax = plt.subplots(figsize=(10, 2.8), dpi=150)

    # 横向区间线：表示历史最小值到最大值的整体范围。
    ax.hlines(0, min_value, max_value, color="#4C4C4C", linewidth=3)

    # 当前值红点。
    ax.scatter([current_value], [0], color="#D62728", s=85, zorder=3)

    # 左右端标注最小值和最大值。
    ax.text(min_value, -0.14, f"Min: {min_value:.2f}", ha="left", va="top", fontsize=10, color="#1F77B4")
    ax.text(max_value, -0.14, f"Max: {max_value:.2f}", ha="right", va="top", fontsize=10, color="#FF7F0E")

    # 当前值数值标注放在红点上方。
    ax.text(current_value, 0.12, f"{current_value:.2f}", ha="center", va="bottom", fontsize=10, color="#D62728")

    # 给横轴留出边距，避免文字贴边。
    span = max_value - min_value
    margin = span * 0.08 if span > 0 else max(1.0, abs(max_value) * 0.08)
    ax.set_xlim(min_value - margin, max_value + margin)
    ax.set_ylim(-0.38, 0.38)

    ax.set_yticks([])
    ax.set_xlabel("Value")
    ax.set_title(title, fontsize=13, pad=12)

    for spine in ("left", "right", "top"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#B0B0B0")

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
