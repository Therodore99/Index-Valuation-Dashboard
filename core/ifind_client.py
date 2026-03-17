# -*- coding: utf-8 -*-
"""iFinD 客户端封装。

该模块只做两件事：
1) 登录 iFinD；
2) 拉取指定指数 + 指标 + 日期区间的数据，并输出统一 DataFrame(date, value)。

这样主流程就不需要关心 iFinD 返回结构细节，便于维护和扩展。
"""

import os
import sys
from datetime import date

import pandas as pd
from iFinDPy import THS_DS, THS_iFinDLogin

from utils.date_utils import to_ifind_date


class IFindClient:
    """iFinD 数据客户端。"""

    def __init__(self) -> None:
        self._logged_in = False

    def login(self) -> None:
        """使用环境变量登录 iFinD。"""
        if self._logged_in:
            return

        user = os.getenv("IFIND_USER")
        password = os.getenv("IFIND_PASS")

        if not user or not password:
            print("Missing IFIND_USER / IFIND_PASS environment variables.")
            print("Please set them in Windows CMD:")
            print('  setx IFIND_USER "你的用户名"')
            print('  setx IFIND_PASS "你的密码"')
            print("Then reopen terminal and run again.")
            sys.exit(1)

        result = THS_iFinDLogin(user, password)

        if isinstance(result, int):
            code = result
            message = ""
        else:
            code = getattr(result, "errorcode", None)
            message = getattr(result, "errmsg", "")

        if code not in (0, -201):
            raise RuntimeError(f"iFinD login failed. code={code}, message={message}")

        self._logged_in = True

    def fetch_series(
        self,
        index_code: str,
        indicator_key: str,
        indicator_config: dict,
        start_date: date,
        end_date: date,
    ) -> pd.DataFrame:
        """拉取指数某指标的时间序列，返回标准列：date/value。"""
        if start_date > end_date:
            return pd.DataFrame(columns=["date", "value"])

        field = indicator_config.get("field", "")
        jsonparam = indicator_config.get("jsonparam", "")
        globalparam = indicator_config.get("globalparam", "")

        if not field:
            raise RuntimeError(f"No field configured for indicator={indicator_key}")

        self.login()

        print(
            "Fetching from iFinD | "
            f"code={index_code}, field={field}, jsonparam={jsonparam!r}, globalparam={globalparam!r}, "
            f"start_date={start_date}, end_date={end_date}"
        )

        response = THS_DS(
            index_code,
            field,
            jsonparam,
            globalparam,
            to_ifind_date(start_date),
            to_ifind_date(end_date),
        )

        errorcode = getattr(response, "errorcode", 0)
        errmsg = getattr(response, "errmsg", "")
        if errorcode not in (0, None):
            raise RuntimeError(
                f"iFinD data fetch failed. indicator={indicator_key}, field={field}, "
                f"jsonparam={jsonparam!r}, code={errorcode}, message={errmsg}"
            )

        raw_df = self._extract_dataframe(response)
        if raw_df.empty:
            self._log_empty_result(
                index_code=index_code,
                indicator_key=indicator_key,
                field=field,
                jsonparam=jsonparam,
                globalparam=globalparam,
                start_date=start_date,
                end_date=end_date,
                response=response,
                raw_df=raw_df,
                reason="Extracted DataFrame is empty.",
            )
            return pd.DataFrame(columns=["date", "value"])

        date_col, value_col = self._detect_columns(raw_df, field, indicator_key)

        if date_col is None or value_col is None:
            self._log_empty_result(
                index_code=index_code,
                indicator_key=indicator_key,
                field=field,
                jsonparam=jsonparam,
                globalparam=globalparam,
                start_date=start_date,
                end_date=end_date,
                response=response,
                raw_df=raw_df,
                reason="Failed to identify date/value columns.",
            )
            return pd.DataFrame(columns=["date", "value"])

        cleaned_value = (
            raw_df[value_col]
            .astype(str)
            .str.strip()
            .replace(
                {
                    "": None,
                    "--": None,
                    "None": None,
                    "null": None,
                    "NULL": None,
                    "nan": None,
                    "NaN": None,
                }
            )
        )

        df = pd.DataFrame(
            {
                "date": pd.to_datetime(raw_df[date_col], errors="coerce"),
                "value": pd.to_numeric(cleaned_value, errors="coerce"),
            }
        ).dropna(subset=["date", "value"])

        df = df[(df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)]
        df = df.drop_duplicates(subset=["date"], keep="last").sort_values("date").reset_index(drop=True)

        if df.empty:
            self._log_empty_result(
                index_code=index_code,
                indicator_key=indicator_key,
                field=field,
                jsonparam=jsonparam,
                globalparam=globalparam,
                start_date=start_date,
                end_date=end_date,
                response=response,
                raw_df=raw_df,
                reason="Data became empty after numeric conversion / date filtering.",
            )

        return df

    @staticmethod
    def _extract_dataframe(response) -> pd.DataFrame:
        """兼容 iFinD 多种返回结构，尽量提取为 DataFrame。"""
        if isinstance(response, pd.DataFrame):
            return response.copy()

        data = getattr(response, "data", None)

        if isinstance(data, pd.DataFrame):
            return data.copy()

        if isinstance(data, dict):
            if data and all(isinstance(v, list) for v in data.values()):
                return pd.DataFrame(data)

            for key in ("tables", "table", "data"):
                value = data.get(key)
                if isinstance(value, pd.DataFrame):
                    return value.copy()
                if isinstance(value, list) and value:
                    if isinstance(value[0], dict):
                        return pd.DataFrame(value)
                    if isinstance(value[0], pd.DataFrame):
                        return value[0].copy()

        if isinstance(data, list) and data and isinstance(data[0], dict):
            return pd.DataFrame(data)

        return pd.DataFrame()

    @staticmethod
    def _detect_columns(raw_df: pd.DataFrame, field: str, indicator_key: str) -> tuple[str | None, str | None]:
        """识别日期列和值列。"""
        date_col = None
        value_col = None

        candidates_date = {"time", "date", "tradedate", "trade_date"}
        candidates_value = {
            field.lower(),
            "value",
            "close",
            "pe",
            "pb",
            "收盘价",
            "市盈率",
            "市净率",
        }

        for col in raw_df.columns:
            lower = str(col).strip().lower()
            if lower in candidates_date and date_col is None:
                date_col = col
            if lower in candidates_value and value_col is None:
                value_col = col
            if indicator_key.lower() in lower and value_col is None and lower not in candidates_date:
                value_col = col

        if date_col is None and len(raw_df.columns) > 0:
            date_col = raw_df.columns[0]

        if value_col is None:
            for col in raw_df.columns:
                if col == date_col:
                    continue
                numeric_ratio = pd.to_numeric(raw_df[col], errors="coerce").notna().mean()
                if numeric_ratio > 0:
                    value_col = col
                    break

        return date_col, value_col

    @staticmethod
    def _log_empty_result(
        index_code: str,
        indicator_key: str,
        field: str,
        jsonparam: str,
        globalparam: str,
        start_date: date,
        end_date: date,
        response,
        raw_df: pd.DataFrame,
        reason: str,
    ) -> None:
        """空结果诊断日志（摘要版）。"""
        columns = list(raw_df.columns) if not raw_df.empty else []
        sample_rows = raw_df.head(5).to_dict(orient="records") if not raw_df.empty else []
        print(
            "[DEBUG] Empty result summary | "
            f"code={index_code}, indicator={indicator_key}, field={field}, jsonparam={jsonparam!r}, "
            f"globalparam={globalparam!r}, date_range={start_date}~{end_date}, "
            f"response_type={type(response).__name__}, columns={columns}, reason={reason}"
        )
        print(f"[DEBUG] Sample rows (top 5): {sample_rows}")
