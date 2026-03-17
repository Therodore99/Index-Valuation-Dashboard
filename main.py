# -*- coding: utf-8 -*-
"""项目入口。

运行方式：
    python main.py

职责边界：
- 这里只做流程调度，不放具体业务细节。
- 具体登录、拉数、缓存、计算、画图分别交给对应模块。
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from config import (
    DATA_DIR,
    DEFAULT_WINDOW_DAYS,
    DEFAULT_WINDOW_TAG,
    INDEXES,
    INDICATORS,
    OUTPUT_DIR,
)
from core.calculator import calculate_metrics
from core.data_manager import get_series_with_incremental_update
from core.ifind_client import IFindClient
from core.plotter import generate_position_chart
from utils.date_utils import get_window_dates
from utils.file_utils import build_cache_path, build_output_path, ensure_dir


def print_report(index_name: str, indicator_name: str, metrics: dict) -> None:
    """统一的命令行输出格式。"""
    print("-" * 56)
    print(f"指数名称: {index_name}")
    print(f"指标名称: {indicator_name}")
    print(
        "数据区间: "
        f"{metrics['start_date'].strftime('%Y-%m-%d')} ~ {metrics['end_date'].strftime('%Y-%m-%d')}"
    )
    print(f"样本数量: {metrics['sample_count']}")
    print()
    print(f"区间最低值: {metrics['min_value']:.2f}")
    print(f"区间最高值: {metrics['max_value']:.2f}")
    print(f"当前值: {metrics['current_value']:.2f}")
    print(f"区间位置比例: {metrics['position_pct']:.2f}%")
    print("-" * 56)


def run() -> None:
    """主流程：按配置遍历指数和指标，完成缓存更新、计算和出图。"""
    ensure_dir(DATA_DIR)
    ensure_dir(OUTPUT_DIR)

    start_date, end_date = get_window_dates(DEFAULT_WINDOW_DAYS)

    client = IFindClient()
    success_count = 0
    failure_messages = []

    for index_key, index_cfg in INDEXES.items():
        index_name = index_cfg["display_name"]
        index_code = index_cfg["code"]

        for indicator_key, indicator_cfg in INDICATORS.items():
            indicator_name = indicator_cfg["name"]

            print(
                f"\nProcessing index={index_name}, indicator={indicator_name}, "
                f"field={indicator_cfg.get('field')}, jsonparam={indicator_cfg.get('jsonparam')!r}, "
                f"globalparam={indicator_cfg.get('globalparam')!r}"
            )

            cache_path = build_cache_path(DATA_DIR, index_key, indicator_key)
            output_path = build_output_path(OUTPUT_DIR, index_key, indicator_key, DEFAULT_WINDOW_TAG)

            try:
                window_df = get_series_with_incremental_update(
                    client=client,
                    index_code=index_code,
                    indicator_key=indicator_key,
                    indicator_config=indicator_cfg,
                    cache_path=cache_path,
                    start_date=start_date,
                    end_date=end_date,
                )

                if window_df.empty:
                    raise ValueError("No data available in selected window.")

                metrics = calculate_metrics(window_df)
                print_report(index_name, indicator_name, metrics)

                title = f"{index_name} {indicator_name} {DEFAULT_WINDOW_TAG} 区间位置"
                generate_position_chart(metrics=metrics, title=title, output_path=output_path)
                print(f"图表已保存: {output_path}")
                success_count += 1
            except Exception as exc:
                msg = f"Indicator failed -> index={index_name}, indicator={indicator_name}, reason={exc}"
                print(msg)
                failure_messages.append(msg)
                continue

    if success_count == 0:
        detail = "\n".join(failure_messages) if failure_messages else "No indicators were processed."
        raise RuntimeError(f"All indicators failed.\n{detail}")


def main() -> None:
    """统一入口，负责错误兜底和退出码。"""
    try:
        run()
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
