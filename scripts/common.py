# -*- coding: utf-8 -*-
"""PSP 发现者统计项目的共用路径、数据与解析工具。"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PAGE_PATH = PROJECT_ROOT / "data" / "raw" / "psp_page.html"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DISCOVERERS_PATH = PROCESSED_DIR / "discoverers.json"
PARSED_ENTRIES_PATH = PROCESSED_DIR / "parsed_entries.json"
DOCS_DIR = PROJECT_ROOT / "docs"
RANKING_PAGE_PATH = DOCS_DIR / "index.html"

UNCONFIRMED_TYPE_ALIASES = {"未证认": "未获证认"}


def strip_tags(fragment: str) -> str:
    """移除 HTML 标记并还原实体，同时压缩首尾空白。"""
    text = re.sub(r"<[^>]+>", "", fragment)
    return html.unescape(text).replace("\xa0", " ").strip()


def normalize_text(value: str) -> str:
    """将连续空白压缩为单一空格。"""
    return re.sub(r"\s+", " ", value).strip()


def normalize_type(value: str) -> str:
    """将源页面的同义类别统一为项目使用的标准文本。"""
    stripped = value.strip()
    compact = re.sub(r"\s+", "", stripped)
    if compact in {"未证认", "未获证认"}:
        return "未获证认"
    return UNCONFIRMED_TYPE_ALIASES.get(stripped, stripped)


def category_for_type(value: str) -> str:
    """将具体天体类型归并为排行榜使用的大类。"""
    normalized = normalize_type(value)
    if normalized.startswith("SN"):
        return "超新星 SN"
    if normalized.startswith("Nova"):
        return "新星 Nova"
    if normalized == "AGN":
        return "活动星系核 AGN"
    if normalized == "未获证认":
        return "未获证认"
    return "各类变星"


def read_json(path: Path) -> Any:
    """以 UTF-8 读取 JSON 文件。"""
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    """确保父目录存在后，以 UTF-8 写入格式化 JSON。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def read_text(path: Path) -> str:
    """以 UTF-8 读取文本文件。"""
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    """确保父目录存在后，以 UTF-8 写入文本文件。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
