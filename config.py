# -*- coding: utf-8 -*-
"""项目配置中心。

为什么集中配置：
1) 新增指数时，不需要改业务代码，只需要加配置项。
2) 调整指标字段（例如 iFinD 字段名变化）时，避免在多处重复修改。
3) 后续扩展到 5 年、10 年时，只改时间参数即可。
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"

# 默认分析周期：近 365 天（1 年）
DEFAULT_WINDOW_DAYS = 365
DEFAULT_WINDOW_TAG = "1y"

# 指数配置：当前默认恒生科技指数，后续可继续扩展。
INDEXES = {
    "hstech": {
        "display_name": "恒生科技指数",
        "code": "HSTECH.HK",
    }
}
DEFAULT_INDEX_KEY = "hstech"

# 指标配置：统一走配置驱动。
# 说明：PB 目前按已确认方案固定使用 ths_pb_index + jsonparam="10,1"。
INDICATORS = {
    "close": {
        "name": "收盘价",
        "field": "ths_close_price_index",
        "jsonparam": "",
        "globalparam": "",
    },
    "pe": {
        "name": "PE",
        "field": "ths_pe_ttm_index",
        "jsonparam": "",
        "globalparam": "",
    },
    "pb": {
        "name": "PB",
        "field": "ths_pb_index",
        "jsonparam": "10,1",
        "globalparam": "",
    },
}
