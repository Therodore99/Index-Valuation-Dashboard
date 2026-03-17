# -*- coding: utf-8 -*-
"""缓存与增量更新管理。"""

from datetime import date
from pathlib import Path

import pandas as pd

from core.ifind_client import IFindClient
from utils.date_utils import plus_days
from utils.file_utils import ensure_dir


def load_cache(cache_path: Path) -> pd.DataFrame:
    """读取缓存 CSV。"""
    if not cache_path.exists():
        return pd.DataFrame(columns=["date", "value"])

    df = pd.read_csv(cache_path)
    if df.empty:
        return pd.DataFrame(columns=["date", "value"])

    if "date" not in df.columns or "value" not in df.columns:
        raise RuntimeError(f"Invalid cache format in {cache_path}. Expected columns: date,value")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["date", "value"])

    if df.empty:
        return pd.DataFrame(columns=["date", "value"])

    return df.drop_duplicates(subset=["date"], keep="last").sort_values("date").reset_index(drop=True)


def save_cache(df: pd.DataFrame, cache_path: Path) -> None:
    """保存缓存 CSV。"""
    ensure_dir(cache_path.parent)
    output = df[["date", "value"]].copy()
    output["date"] = output["date"].dt.strftime("%Y-%m-%d")
    output.to_csv(cache_path, index=False)


def get_series_with_incremental_update(
    client: IFindClient,
    index_code: str,
    indicator_key: str,
    indicator_config: dict,
    cache_path: Path,
    start_date: date,
    end_date: date,
) -> pd.DataFrame:
    """读取并增量更新缓存，返回分析窗口内数据。"""
    cache_exists = cache_path.exists()
    cache_df = load_cache(cache_path)

    if cache_df.empty:
        if cache_exists:
            print(f"Cache file exists but has no valid rows -> treat as no cache: {cache_path}")
        else:
            print(f"No cache found -> full fetch: {cache_path}")

        fetched = client.fetch_series(index_code, indicator_key, indicator_config, start_date, end_date)
        if fetched.empty:
            print(
                f"No valid data fetched for indicator={indicator_key}. "
                "Will not overwrite cache with empty content."
            )
            return pd.DataFrame(columns=["date", "value"])

        merged = fetched.copy()
    else:
        print(f"Cache found -> incremental update: {cache_path}")
        merged = cache_df.copy()

        min_cached = merged["date"].min().date()
        max_cached = merged["date"].max().date()

        if min_cached > start_date:
            backfill_start = start_date
            backfill_end = plus_days(min_cached, -1)
            backfill = client.fetch_series(index_code, indicator_key, indicator_config, backfill_start, backfill_end)
            if not backfill.empty:
                print(f"Backfill fetched: {backfill_start} ~ {backfill_end}")
                merged = pd.concat([merged, backfill], ignore_index=True)

        if max_cached < end_date:
            forward_start = plus_days(max_cached, 1)
            forward_end = end_date
            forward = client.fetch_series(index_code, indicator_key, indicator_config, forward_start, forward_end)
            if not forward.empty:
                print(f"Forward-fill fetched: {forward_start} ~ {forward_end}")
                merged = pd.concat([merged, forward], ignore_index=True)

    merged = merged.dropna(subset=["date", "value"])
    merged = merged.drop_duplicates(subset=["date"], keep="last").sort_values("date").reset_index(drop=True)

    if merged.empty:
        print(
            f"Merged result is empty for indicator={indicator_key}. "
            "Skip cache write to avoid replacing existing data with empty rows."
        )
        return pd.DataFrame(columns=["date", "value"])

    save_cache(merged, cache_path)

    window_df = merged[(merged["date"].dt.date >= start_date) & (merged["date"].dt.date <= end_date)]
    window_df = window_df.sort_values("date").reset_index(drop=True)

    return window_df
