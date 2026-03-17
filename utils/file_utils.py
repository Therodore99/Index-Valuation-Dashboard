# -*- coding: utf-8 -*-
"""文件与目录工具函数。"""

from pathlib import Path


def ensure_dir(path: Path) -> None:
    """确保目录存在。

    为什么单独封装：
    - 统一目录创建方式，主流程更清晰。
    - 避免在多个模块重复写 mkdir 逻辑。
    """
    path.mkdir(parents=True, exist_ok=True)


def build_cache_path(data_dir: Path, index_key: str, indicator_key: str) -> Path:
    """生成缓存路径：data/{index_key}/{indicator_key}.csv"""
    return data_dir / index_key / f"{indicator_key}.csv"


def build_output_path(output_dir: Path, index_key: str, indicator_key: str, window_tag: str) -> Path:
    """生成图片路径：outputs/{index_key}/{index}_{indicator}_{window}_position.png"""
    file_name = f"{index_key}_{indicator_key}_{window_tag}_position.png"
    return output_dir / index_key / file_name
