# -*- coding: utf-8 -*-
"""日期相关工具函数。"""

from datetime import date, timedelta


def get_window_dates(window_days: int) -> tuple[date, date]:
    """返回分析窗口起止日期（含起止）。

    为什么这样做：
    - 用统一函数计算日期，避免不同模块各自计算导致口径不一致。
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=window_days)
    return start_date, end_date


def to_ifind_date(value: date) -> str:
    """将 date 转成 iFinD 常用 YYYY-MM-DD 格式。"""
    return value.strftime("%Y-%m-%d")


def plus_days(value: date, days: int) -> date:
    """日期偏移工具，便于增量更新时计算补拉起止。"""
    return value + timedelta(days=days)
