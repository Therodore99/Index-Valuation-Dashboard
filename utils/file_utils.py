# -*- coding: utf-8 -*-
"""文件与目录工具函数。"""

from pathlib import Path


def ensure_dir(path: Path) -> None:
    """确保目录存在。"""
    path.mkdir(parents=True, exist_ok=True)


def build_cache_path(data_dir: Path, index_key: str, indicator_key: str) -> Path:
    """生成缓存路径：data/{index_key}/{indicator_key}.csv"""
    return data_dir / index_key / f"{indicator_key}.csv"


def build_output_path(output_dir: Path, index_key: str, indicator_key: str, window_tag: str) -> Path:
    """生成单指标图片路径：outputs/{index}/{index}_{indicator}_{window}.png"""
    return output_dir / index_key / f"{index_key}_{indicator_key}_{window_tag}.png"


def build_dual_output_path(output_dir: Path, index_key: str, window_tag: str) -> Path:
    """生成 PE+PB 组合图路径：outputs/{index}/{index}_pe_pb_{window}.png"""
    return output_dir / index_key / f"{index_key}_pe_pb_{window_tag}.png"
