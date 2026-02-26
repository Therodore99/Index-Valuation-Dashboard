# -*- coding: utf-8 -*-
"""
依赖安装（示例）：
    pip install iFinDPy pandas matplotlib

Windows 设置环境变量（示例）：
    setx IFIND_USER "你的用户名"
    setx IFIND_PASS "你的密码"

注意：setx 设置后需要重新打开终端才会生效。
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from iFinDPy import THS_DS, THS_iFinDLogin


CONFIG = {
    "INDEX_CODE": "HSTECH.HK",
    "INDICATOR_NAME": "ths_close_price_index",
    "CACHE_PATH": Path("data") / "hstech_1y.csv",
    "OUTPUT_PATH": Path("outputs") / "hstech_1y_position.png",
    "CACHE_MAX_AGE_HOURS": 24,
}


def login_ifind():
    """Login to iFinDPy with environment variables."""
    user = os.getenv("IFIND_USER")
    password = os.getenv("IFIND_PASS")

    if not user or not password:
        print("Missing IFIND_USER / IFIND_PASS environment variables.")
        print("Please set them in Windows CMD:")
        print('  setx IFIND_USER "你的用户名"')
        print('  setx IFIND_PASS "你的密码"')
        print("Then reopen terminal and run again.")
        sys.exit(1)

    login_result = THS_iFinDLogin(user, password)

    if isinstance(login_result, int):
        code = login_result
        message = ""
    else:
        code = getattr(login_result, "errorcode", None)
        message = getattr(login_result, "errmsg", "")

    if code not in (0, -201):
        err_detail = f"iFinDPy login failed. code={code}"
        if message:
            err_detail += f", message={message}"
        raise RuntimeError(err_detail)


def _extract_dataframe_from_ifind_response(response):
    """Best-effort parser for different iFinDPy return structures."""
    if isinstance(response, pd.DataFrame):
        return response.copy()

    data = getattr(response, "data", None)

    if isinstance(data, pd.DataFrame):
        return data.copy()

    if isinstance(data, dict):
        for key in ("tables", "table", "data"):
            value = data.get(key)
            if isinstance(value, list) and value:
                if isinstance(value[0], pd.DataFrame):
                    return value[0].copy()
                if isinstance(value[0], dict):
                    return pd.DataFrame(value)
            if isinstance(value, pd.DataFrame):
                return value.copy()

        if data and all(isinstance(v, list) for v in data.values()):
            return pd.DataFrame(data)

    if isinstance(data, list) and data:
        if isinstance(data[0], dict):
            return pd.DataFrame(data)
        if isinstance(data[0], (list, tuple)):
            return pd.DataFrame(data)

    raise RuntimeError("Unable to parse iFinDPy response into DataFrame.")


def fetch_hstech_1y():
    """Fetch 1-year daily close prices of HSTECH from iFinDPy or cache."""
    cache_path = CONFIG["CACHE_PATH"]
    now = datetime.now()

    if cache_path.exists():
        modified_ts = datetime.fromtimestamp(cache_path.stat().st_mtime)
        if now - modified_ts <= timedelta(hours=CONFIG["CACHE_MAX_AGE_HOURS"]):
            cached_df = pd.read_csv(cache_path)
            cached_df["date"] = pd.to_datetime(cached_df["date"])
            cached_df["close"] = cached_df["close"].astype(float)
            cached_df = cached_df[["date", "close"]].sort_values("date").reset_index(drop=True)
            print("Loaded from cache")
            return cached_df

    login_ifind()

    end_date = now.date()
    start_date = end_date - timedelta(days=365)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    response = THS_DS(
        CONFIG["INDEX_CODE"],
        CONFIG["INDICATOR_NAME"],
        '',
        '',
        start_str,
        end_str,
    )

    errorcode = getattr(response, "errorcode", 0)
    errmsg = getattr(response, "errmsg", "")
    if errorcode not in (0, None):
        raise RuntimeError(f"iFinDPy data fetch failed. code={errorcode}, message={errmsg}")

    raw_df = _extract_dataframe_from_ifind_response(response)

    date_col = None
    close_col = None
    for col in raw_df.columns:
        lower = str(col).strip().lower()
        if lower in ("time", "date", "tradedate", "trade_date"):
            date_col = col
        if lower in (
            "ths_close_price_index",
            CONFIG["INDICATOR_NAME"].lower(),
            "close",
            "closeprice",
            "close_price",
            "收盘价",
        ):
            close_col = col

    if date_col is None:
        date_col = raw_df.columns[0] if len(raw_df.columns) > 0 else None
    if close_col is None:
        for col in raw_df.columns[1:]:
            if pd.to_numeric(raw_df[col], errors="coerce").notna().any():
                close_col = col
                break

    if date_col is None or close_col is None:
        raise RuntimeError(
            f"Failed to identify date/close columns from iFinDPy result. columns={list(raw_df.columns)}"
        )

    df = pd.DataFrame({
        "date": pd.to_datetime(raw_df[date_col], errors="coerce"),
        "close": pd.to_numeric(raw_df[close_col], errors="coerce"),
    }).dropna(subset=["date", "close"])

    if df.empty:
        raise RuntimeError("No valid date/close rows returned from iFinDPy.")

    df = df.sort_values("date").reset_index(drop=True)

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(cache_path, index=False)
    print("Fetched from iFinDPy")

    return df


def calculate_metrics(df):
    """Calculate min/max/current and position percentage."""
    if df.empty:
        raise ValueError("Input DataFrame is empty.")

    min_close = float(df["close"].min())
    max_close = float(df["close"].max())
    current_close = float(df.iloc[-1]["close"])

    if max_close == min_close:
        position_pct = 0.0
    else:
        position_pct = (current_close - min_close) / (max_close - min_close) * 100.0

    metrics = {
        "start_date": df["date"].min(),
        "end_date": df["date"].max(),
        "sample_count": int(len(df)),
        "min_close": min_close,
        "max_close": max_close,
        "current_close": current_close,
        "position_pct": float(position_pct),
    }
    return metrics


def generate_chart(metrics):
    """Generate and save horizontal position chart."""
    output_path = CONFIG["OUTPUT_PATH"]
    output_path.parent.mkdir(parents=True, exist_ok=True)

    min_close = metrics["min_close"]
    max_close = metrics["max_close"]
    current_close = metrics["current_close"]

    fig, ax = plt.subplots(figsize=(10, 2.8), dpi=150)

    ax.hlines(0, min_close, max_close, color="#4C4C4C", linewidth=3)

    ax.scatter([current_close], [0], color="#D62728", s=80, zorder=3)

    ax.text(min_close, -0.15, f"Min: {min_close:.2f}", ha="left", va="top", fontsize=10, color="#1F77B4")
    ax.text(max_close, -0.15, f"Max: {max_close:.2f}", ha="right", va="top", fontsize=10, color="#FF7F0E")
    ax.text(current_close, 0.12, f"{current_close:.2f}", ha="center", va="bottom", fontsize=10, color="#D62728")

    margin = (max_close - min_close) * 0.08 if max_close > min_close else max(1.0, abs(max_close) * 0.08)
    ax.set_xlim(min_close - margin, max_close + margin)
    ax.set_ylim(-0.4, 0.4)

    ax.set_yticks([])
    ax.set_xlabel("Index Level")
    ax.set_title("恒生科技指数近一年区间位置", fontsize=13, pad=12)

    for spine in ("left", "right", "top"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#B0B0B0")

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close(fig)

    print(f"Chart saved to: {output_path}")


def main():
    Path("data").mkdir(parents=True, exist_ok=True)
    Path("outputs").mkdir(parents=True, exist_ok=True)

    try:
        df = fetch_hstech_1y()
        metrics = calculate_metrics(df)

        print("-" * 40)
        print("恒生科技指数（近1年区间位置）")
        print(
            "数据区间: "
            f"{metrics['start_date'].strftime('%Y-%m-%d')} ~ {metrics['end_date'].strftime('%Y-%m-%d')}"
        )
        print(f"样本数量: {metrics['sample_count']}")
        print()
        print(f"区间最低值: {metrics['min_close']:.2f}")
        print(f"区间最高值: {metrics['max_close']:.2f}")
        print(f"当前指数值: {metrics['current_close']:.2f}")
        print(f"区间位置比例: {metrics['position_pct']:.2f}%")
        print("-" * 40)

        generate_chart(metrics)
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()

