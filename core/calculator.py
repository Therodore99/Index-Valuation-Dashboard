# -*- coding: utf-8 -*-
"""指标计算模块。"""

import pandas as pd


def calculate_metrics(df: pd.DataFrame) -> dict:
    """计算区间统计值与位置比例。

    返回字段：
    - min_value
    - max_value
    - current_value
    - position_pct
    - start_date
    - end_date
    - sample_count
    """
    if df.empty:
        raise ValueError("No data available in selected window.")

    values = df["value"].astype(float)

    min_value = float(values.min())
    max_value = float(values.max())
    current_value = float(values.iloc[-1])

    # 避免 max == min 导致除零错误。
    if max_value == min_value:
        position_pct = 0.0
    else:
        position_pct = (current_value - min_value) / (max_value - min_value) * 100.0

    return {
        "start_date": df["date"].min(),
        "end_date": df["date"].max(),
        "sample_count": int(len(df)),
        "min_value": min_value,
        "max_value": max_value,
        "current_value": current_value,
        "position_pct": float(position_pct),
    }
