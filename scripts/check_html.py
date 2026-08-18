# -*- coding: utf-8 -*-
"""对生成的发现者排行页面执行快速结构检查。"""
from __future__ import annotations

from bs4 import BeautifulSoup

from common import DISCOVERERS_PATH, RANKING_PAGE_PATH, read_json, read_text


def main() -> None:
    """检查表格、详情、脚本和说明文字是否完整生成。"""
    data = read_json(DISCOVERERS_PATH)
    raw_html = read_text(RANKING_PAGE_PATH)
    soup = BeautifulSoup(raw_html, "html.parser")
    rows = soup.select("#tbody tr")

    expected_rows = len(data["counts"])
    if len(rows) != expected_rows:
        raise AssertionError(f"表格行数 {len(rows)}，期望 {expected_rows}")
    if len(soup.select("#tbody details")) != expected_rows:
        raise AssertionError("详情块数量与表格行数不一致")
    if "{{" in raw_html or "}}" in raw_html:
        raise AssertionError("页面仍含未渲染的模板花括号")
    if not soup.select_one("#search"):
        raise AssertionError("页面缺少发现者搜索框")
    if "function applyFilter" not in raw_html:
        raise AssertionError("页面缺少筛选逻辑")
    if "PSP团队" not in raw_html or "集体署名" not in raw_html:
        raise AssertionError("页面缺少 PSP 团队说明")

    print(f"网页结构检查通过：{expected_rows} 行排行，{expected_rows} 个详情块。")


if __name__ == "__main__":
    main()
