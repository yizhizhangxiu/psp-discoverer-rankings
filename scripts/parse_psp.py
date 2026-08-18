# -*- coding: utf-8 -*-
"""从 PSP 原始页面生成规范化的目标名称与类型清单。"""
from __future__ import annotations

from collections import Counter

from parse_discoverers import parse_entries
from common import (
    PARSED_ENTRIES_PATH,
    RAW_PAGE_PATH,
    category_for_type,
    read_text,
    write_json,
)


def main() -> None:
    """提取并写出 223 条（或源页面实际条数）规范化条目。"""
    entries = parse_entries(read_text(RAW_PAGE_PATH))
    parsed_entries = [
        {"designation": entry["designation"], "type": entry["type"]}
        for entry in entries
    ]
    write_json(PARSED_ENTRIES_PATH, parsed_entries)

    category_counts = Counter(category_for_type(entry["type"]) for entry in entries)
    print(f"已写入：{PARSED_ENTRIES_PATH}")
    print(f"条目数：{len(parsed_entries)}")
    for category, count in category_counts.most_common():
        print(f"{category}\t{count}")


if __name__ == "__main__":
    main()
