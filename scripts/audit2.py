# -*- coding: utf-8 -*-
"""专项审计发布页面中每位署名实体的对象明细列表。"""
from __future__ import annotations

from bs4 import BeautifulSoup

from common import DISCOVERERS_PATH, RANKING_PAGE_PATH, read_json, read_text


def main() -> None:
    """比较发布页面详情列表与主数据的反向索引。"""
    data = read_json(DISCOVERERS_PATH)
    expected = data["objects_by_discoverer"]
    soup = BeautifulSoup(read_text(RANKING_PAGE_PATH), "html.parser")
    rows = soup.select("#tbody tr")

    if len(rows) != len(expected):
        raise AssertionError(f"网页行数 {len(rows)} 与反向索引实体数 {len(expected)} 不一致")

    for row in rows:
        cells = row.find_all("td")
        name = cells[1].get_text(strip=True)
        detail = row.select_one("details .obj-list")
        if detail is None:
            raise AssertionError(f"缺少对象清单：{name}")
        actual = [item for item in detail.get_text("、").split("、") if item]
        if actual != expected.get(name):
            raise AssertionError(f"对象清单不一致：{name}")

    print(f"对象明细审计通过：已核对 {len(rows)} 个署名实体。")


if __name__ == "__main__":
    main()
