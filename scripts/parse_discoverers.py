# -*- coding: utf-8 -*-
"""从 PSP 原始页面提取发现者统计，并生成主数据文件。"""
from __future__ import annotations

import re
from collections import Counter
from typing import Any

from bs4 import BeautifulSoup

from common import (
    DISCOVERERS_PATH,
    RAW_PAGE_PATH,
    normalize_text,
    normalize_type,
    read_text,
    write_json,
)

SOURCE_URL = "https://nadc.china-vo.org/psp/article/20171116151450"
NAME_SEPARATOR = re.compile(r"[\s\u00a0、，,;；]+")
FONT_SIZE_16 = re.compile(r"font-size\s*:\s*16px", re.IGNORECASE)


def names_from_row(row: Any) -> list[str]:
    """提取一个表格行中以 16px 样式显示的发现者名单。"""
    names: list[str] = []
    for span in row.find_all("span"):
        style = span.get("style", "")
        if not FONT_SIZE_16.search(style):
            continue
        names.extend(
            token
            for token in NAME_SEPARATOR.split(span.get_text(" ", strip=True))
            if token
        )
    return list(dict.fromkeys(names))


def parse_entries(raw_html: str) -> list[dict[str, Any]]:
    """从原始 HTML 提取目标名称、规范化类型和发现者署名。"""
    soup = BeautifulSoup(raw_html, "html.parser")
    entries: list[dict[str, Any]] = []

    for row in soup.find_all("tr"):
        designation_node = row.select_one('span[style*="ff8c00"]')
        if designation_node is None:
            continue

        designation = normalize_text(designation_node.get_text(" ", strip=True))
        container = designation_node.find_parent("div")
        if container is None:
            raise ValueError(f"未找到目标 {designation} 的名称容器")

        container_text = normalize_text(container.get_text(" ", strip=True))
        object_type = normalize_type(
            normalize_text(container_text.replace(designation, "", 1))
        )
        discoverers = names_from_row(row)
        entries.append(
            {
                "designation": designation,
                "type": object_type,
                "discoverers": discoverers,
            }
        )
    return entries


def build_payload(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """建立排行、反向对象清单和可追溯元信息。"""
    counts: Counter[str] = Counter()
    objects_by_discoverer: dict[str, list[str]] = {}

    for entry in entries:
        object_label = f"{entry['designation']}（{entry['type']}）"
        for name in entry["discoverers"]:
            counts[name] += 1
            objects_by_discoverer.setdefault(name, []).append(object_label)

    return {
        "metadata": {
            "source_name": "PSP系统发现目标列表",
            "source_url": SOURCE_URL,
            "source_snapshot": "data/raw/psp_page.html",
            "entry_count": len(entries),
            "counting_rule": "多人共同发现时，每位页面署名者各计一次参与。",
        },
        "entries": entries,
        "counts": [
            {"name": name, "count": count}
            for name, count in counts.most_common()
        ],
        "objects_by_discoverer": objects_by_discoverer,
    }


def main() -> None:
    """读取源页面、生成主数据并输出处理摘要。"""
    entries = parse_entries(read_text(RAW_PAGE_PATH))
    empty_names = [entry["designation"] for entry in entries if not entry["discoverers"]]
    if empty_names:
        raise ValueError(f"以下目标未提取到发现者名单：{', '.join(empty_names)}")

    payload = build_payload(entries)
    write_json(DISCOVERERS_PATH, payload)

    participation_count = sum(item["count"] for item in payload["counts"])
    print(f"已写入：{DISCOVERERS_PATH}")
    print(f"目标数：{len(entries)}")
    print(f"署名实体数：{len(payload['counts'])}")
    print(f"发现参与人次：{participation_count}")


if __name__ == "__main__":
    main()
