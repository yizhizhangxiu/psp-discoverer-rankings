# -*- coding: utf-8 -*-
"""执行 PSP 发现者统计项目的端到端数据验证。"""
from __future__ import annotations

from collections import Counter

from parse_discoverers import parse_entries
from common import (
    DISCOVERERS_PATH,
    PARSED_ENTRIES_PATH,
    RAW_PAGE_PATH,
    category_for_type,
    read_json,
    read_text,
)


def main() -> None:
    """核对原始页、主数据、辅助数据与排行统计的关键不变量。"""
    source_entries = parse_entries(read_text(RAW_PAGE_PATH))
    discoverer_data = read_json(DISCOVERERS_PATH)
    parsed_entries = read_json(PARSED_ENTRIES_PATH)

    if source_entries != discoverer_data["entries"]:
        raise AssertionError("主数据 entries 与原始页面解析结果不一致")

    expected_parsed = [
        {"designation": entry["designation"], "type": entry["type"]}
        for entry in source_entries
    ]
    if parsed_entries != expected_parsed:
        raise AssertionError("辅助条目数据与原始页面规范化解析结果不一致")

    designations = [entry["designation"] for entry in source_entries]
    if len(designations) != len(set(designations)):
        raise AssertionError("目标名称存在重复")

    for entry in source_entries:
        names = entry["discoverers"]
        if not names:
            raise AssertionError(f"目标缺少发现者：{entry['designation']}")
        if len(names) != len(set(names)):
            raise AssertionError(f"目标存在重复发现者：{entry['designation']}")

    calculated_counts = Counter(
        name for entry in source_entries for name in entry["discoverers"]
    )
    stored_counts = {item["name"]: item["count"] for item in discoverer_data["counts"]}
    if dict(calculated_counts) != stored_counts:
        raise AssertionError("排行计数与条目汇总不一致")

    for name, count in stored_counts.items():
        if len(discoverer_data["objects_by_discoverer"].get(name, [])) != count:
            raise AssertionError(f"反向对象清单长度不一致：{name}")

    categories = Counter(category_for_type(entry["type"]) for entry in source_entries)
    print("全量验证通过。")
    print(f"目标数：{len(source_entries)}")
    print(f"署名实体数：{len(stored_counts)}")
    print(f"发现参与人次：{sum(calculated_counts.values())}")
    print(f"类别汇总：{dict(categories)}")


if __name__ == "__main__":
    main()
