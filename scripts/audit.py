# -*- coding: utf-8 -*-
"""对 PSP 原始页面、主数据和发布页面执行深度一致性审计。"""
from __future__ import annotations

import re
from collections import Counter
from typing import Any

from bs4 import BeautifulSoup

from common import (
    DISCOVERERS_PATH,
    RANKING_PAGE_PATH,
    RAW_PAGE_PATH,
    category_for_type,
    normalize_text,
    normalize_type,
    read_json,
    read_text,
)

FONT_SIZE_16 = re.compile(r"font-size\s*:\s*16px", re.IGNORECASE)
NAME_SEPARATOR = re.compile(r"[\s\u00a0、，,;；]+")


def independent_reparse(raw_html: str) -> list[dict[str, Any]]:
    """以与生产解析器分离的方式重新提取源页面的关键字段。"""
    soup = BeautifulSoup(raw_html, "html.parser")
    entries: list[dict[str, Any]] = []
    for row in soup.find_all("tr"):
        orange = row.select_one('span[style*="ff8c00"]')
        if orange is None:
            continue
        designation = normalize_text(orange.get_text(" ", strip=True))
        parent = orange.find_parent("div")
        if parent is None:
            raise AssertionError(f"{designation} 缺少名称容器")
        object_type = normalize_type(
            normalize_text(parent.get_text(" ", strip=True).replace(designation, "", 1))
        )
        raw_names: list[str] = []
        for span in row.find_all("span"):
            if FONT_SIZE_16.search(span.get("style", "")):
                raw_names.extend(NAME_SEPARATOR.split(span.get_text(" ", strip=True)))
        names = list(dict.fromkeys(name for name in raw_names if name))
        entries.append({"designation": designation, "type": object_type, "discoverers": names})
    return entries


def check_published_table(data: dict[str, Any]) -> None:
    """确认发布页的排行数值及对象明细与主数据完全一致。"""
    soup = BeautifulSoup(read_text(RANKING_PAGE_PATH), "html.parser")
    rows = soup.select("#tbody tr")
    expected_counts = {item["name"]: item["count"] for item in data["counts"]}
    if len(rows) != len(expected_counts):
        raise AssertionError(f"网页行数 {len(rows)} 与署名实体数 {len(expected_counts)} 不一致")

    for row in rows:
        cells = row.find_all("td")
        if len(cells) != 6:
            raise AssertionError("网页表格列数不是 6")
        name = cells[1].get_text(strip=True)
        count = int(cells[2].get_text(strip=True))
        if expected_counts.get(name) != count:
            raise AssertionError(f"网页计数不一致：{name}={count}")
        detail = row.select_one("details .obj-list")
        if detail is None:
            raise AssertionError(f"网页缺少对象明细：{name}")
        actual_objects = [value for value in detail.get_text("、").split("、") if value]
        expected_objects = data["objects_by_discoverer"][name]
        if actual_objects != expected_objects:
            raise AssertionError(f"网页对象明细不一致：{name}")


def main() -> None:
    """运行完整审计并在失败时以异常终止。"""
    data = read_json(DISCOVERERS_PATH)
    reparsed = independent_reparse(read_text(RAW_PAGE_PATH))
    if reparsed != data["entries"]:
        raise AssertionError("源页面独立重解析结果与 discoverers.json 不一致")

    derived_counts = Counter(
        name for entry in reparsed for name in entry["discoverers"]
    )
    saved_counts = {item["name"]: item["count"] for item in data["counts"]}
    if dict(derived_counts) != saved_counts:
        raise AssertionError("发现者排行与原始条目重新汇总结果不一致")

    for item in data["counts"]:
        object_count = len(data["objects_by_discoverer"].get(item["name"], []))
        if item["count"] != object_count:
            raise AssertionError(f"对象清单长度不一致：{item['name']}")

    check_published_table(data)
    category_counts = Counter(category_for_type(entry["type"]) for entry in reparsed)
    print(f"审计通过：目标 {len(reparsed)} 条，署名实体 {len(saved_counts)} 个。")
    print(f"分类汇总：{dict(category_counts)}")
    print(f"发现参与人次：{sum(derived_counts.values())}")


if __name__ == "__main__":
    main()
