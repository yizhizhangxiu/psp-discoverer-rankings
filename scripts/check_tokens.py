# -*- coding: utf-8 -*-
"""定位原始页面中的 PSP 团队署名，辅助人工核对。"""
from __future__ import annotations

import re

from common import RAW_PAGE_PATH, read_text


def main() -> None:
    """输出每个 PSP 团队署名附近的简化上下文。"""
    raw_html = read_text(RAW_PAGE_PATH)
    matches = list(re.finditer(r"PSP团队", raw_html))
    if not matches:
        raise AssertionError("原始页面未找到 PSP团队 署名")

    print(f"共找到 {len(matches)} 处 PSP团队 署名：")
    for index, match in enumerate(matches, start=1):
        start = max(0, match.start() - 180)
        end = min(len(raw_html), match.end() + 90)
        context = re.sub(r"\s+", " ", raw_html[start:end])
        print(f"[{index}] …{context}…")


if __name__ == "__main__":
    main()
