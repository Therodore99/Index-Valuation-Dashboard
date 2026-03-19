# -*- coding: utf-8 -*-
"""图片导出入口：单指标图 + PE/PB 组合图。"""

from pathlib import Path

import matplotlib.pyplot as plt

from core import plotter
from core.templates import create_dual_template, create_single_template
from utils.file_utils import build_dual_output_path, build_output_path, ensure_dir


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
    title = f"{index_name} {window_tag.upper()} {indicator_name}卡片"
    subtitle = f"截至 {metrics['end_date']:%Y-%m-%d}  |  数据源 iFinD  |  金融媒体卡片"

    plotter.render_title(axes["title"], title, subtitle)
    plotter.render_single_summary(axes["summary"], metrics, indicator_key)
    plotter.render_indicator_chart(axes["chart"], df, metrics, indicator_key, indicator_name)
    plotter.render_single_conclusion(axes["conclusion"], indicator_key, metrics)
    plotter.render_footer(axes["footer"], metrics["start_date"], metrics["end_date"])

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
    title = f"{index_name} {window_tag.upper()} 估值概览卡片"
    subtitle = f"PE + PB 双指标  |  截至 {max(pe_metrics['end_date'], pb_metrics['end_date']):%Y-%m-%d}"

    plotter.render_title(axes["title"], title, subtitle)
    plotter.render_dual_summary(axes["summary"], pe_metrics, pb_metrics)
    plotter.render_indicator_chart(axes["pe_chart"], pe_df, pe_metrics, "pe", "PE")
    plotter.render_indicator_chart(axes["pb_chart"], pb_df, pb_metrics, "pb", "PB")
    plotter.render_dual_conclusion(axes["conclusion"], pe_metrics, pb_metrics)

    start_date = max(pe_metrics["start_date"], pb_metrics["start_date"])
    end_date = min(pe_metrics["end_date"], pb_metrics["end_date"])
    plotter.render_footer(axes["footer"], start_date, end_date)

    fig.savefig(output_path, facecolor=fig.get_facecolor())
    plt.close(fig)
    return output_path
