# -*- coding: utf-8 -*-
"""根据主数据生成可直接发布的 PSP 发现者统计页面。"""
from __future__ import annotations

import re
from collections import Counter
from html import escape
from typing import Any

from common import (
    DISCOVERERS_PATH,
    RANKING_PAGE_PATH,
    RAW_PAGE_PATH,
    category_for_type,
    read_json,
    read_text,
    write_text,
)

CATEGORY_ORDER = [
    "超新星 SN",
    "新星 Nova",
    "各类变星",
    "活动星系核 AGN",
    "未获证认",
]
SOURCE_TIMESTAMP_PATTERN = re.compile(r"\b20\d{{2}}-\d{{2}}-\d{{2}}\s+\d{{2}}:\d{{2}}\b")


def source_snapshot_timestamp() -> str:
    """尽可能从本地原始页面读取页面显示的更新时间。"""
    match = SOURCE_TIMESTAMP_PATTERN.search(read_text(RAW_PAGE_PATH))
    return match.group(0) if match else "未在快照中识别到"


def category_cards(entries: list[dict[str, Any]]) -> str:
    """从实际条目按统一规则汇总并生成类别卡片。"""
    counts = Counter(category_for_type(entry["type"]) for entry in entries)
    return "\n".join(
        (
            '<div class="card"><div class="card-num">'
            f"{counts.get(category, 0)}"
            f'</div><div class="card-label">{escape(category)}</div></div>'
        )
        for category in CATEGORY_ORDER
    )


def ranking_rows(data: dict[str, Any], total_entries: int) -> str:
    """生成发现者排行表格行及可展开的对象清单。"""
    rows: list[str] = []
    objects_by_discoverer = data["objects_by_discoverer"]
    for rank, item in enumerate(data["counts"], start=1):
        name = item["name"]
        count = item["count"]
        percentage = (count / total_entries * 100) if total_entries else 0
        objects = "、".join(escape(value) for value in objects_by_discoverer.get(name, []))
        team_class = " team" if name == "PSP团队" else ""
        rows.append(
            f'''<tr class="{team_class.strip()}" data-count="{count}">
  <td class="rank">{rank}</td>
  <td class="name">{escape(name)}</td>
  <td class="num">{count}</td>
  <td class="num">{percentage:.1f}%</td>
  <td class="bar-cell"><div class="bar" aria-label="参与覆盖率 {percentage:.1f}%"><div class="bar-fill" style="width:{percentage:.2f}%"></div></div></td>
  <td class="detail-cell"><details><summary>查看 {count} 颗</summary><div class="obj-list">{objects}</div></details></td>
</tr>'''
        )
    return "\n".join(rows)


def build_page(data: dict[str, Any]) -> str:
    """构建完整静态网页。"""
    entries = data["entries"]
    total_entries = len(entries)
    entity_count = len(data["counts"])
    metadata = data.get("metadata", {})
    source_url = metadata.get(
        "source_url", "https://nadc.china-vo.org/psp/article/20171116151450"
    )
    snapshot_time = source_snapshot_timestamp()
    cards = category_cards(entries)
    rows = ranking_rows(data, total_entries)

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="PSP 系统发现目标的发现者统计排行。">
<title>PSP 系统发现目标 · 发现者统计排行</title>
<style>
:root {{
  --bg: #f6f8fb; --card: #ffffff; --ink: #1f2937; --muted: #6b7280;
  --line: #e5e7eb; --accent: #2563eb; --gold: #b45309;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; padding: 32px 20px 60px; background: var(--bg); color: var(--ink); font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif; }}
.wrap {{ max-width: 1080px; margin: 0 auto; }}
h1 {{ font-size: clamp(22px, 3vw, 28px); margin: 0 0 6px; }}
.sub {{ color: var(--muted); font-size: 13px; margin-bottom: 24px; line-height: 1.7; }}
.sub a, details summary {{ color: var(--accent); text-decoration: none; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin: 0 0 28px; }}
.card {{ background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 14px 16px; text-align: center; }}
.card-num {{ font-size: 26px; font-weight: 700; color: var(--accent); }}
.card-label {{ font-size: 13px; color: var(--muted); margin-top: 4px; }}
.toolbar {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-bottom: 14px; }}
.toolbar input {{ flex: 1; min-width: min(220px, 100%); padding: 9px 12px; border: 1px solid var(--line); border-radius: 8px; font-size: 14px; }}
.btn {{ padding: 9px 14px; border: 1px solid var(--line); border-radius: 8px; background: var(--card); cursor: pointer; font-size: 13px; color: var(--ink); }}
.btn.active {{ background: var(--accent); border-color: var(--accent); color: #fff; }}
.table-wrap {{ overflow-x: auto; background: var(--card); border: 1px solid var(--line); border-radius: 10px; }}
table {{ width: 100%; min-width: 760px; border-collapse: collapse; font-size: 14px; }}
th, td {{ padding: 9px 10px; text-align: left; border-bottom: 1px solid var(--line); }}
thead th {{ background: #eef2f7; font-size: 13px; color: var(--muted); position: sticky; top: 0; }}
tbody tr:last-child td {{ border-bottom: 0; }}
td.rank {{ color: var(--muted); width: 46px; text-align: center; }}
td.name {{ font-weight: 600; }} tr.team td.name {{ color: var(--gold); }}
td.num {{ text-align: right; font-variant-numeric: tabular-nums; width: 78px; }}
td.bar-cell {{ width: 160px; }} .bar {{ background: var(--line); border-radius: 5px; height: 8px; overflow: hidden; }}
.bar-fill {{ background: linear-gradient(90deg, #60a5fa, var(--accent)); height: 100%; }}
td.detail-cell {{ width: 120px; }} details summary {{ cursor: pointer; font-size: 13px; }}
.obj-list {{ margin-top: 8px; padding: 10px; background: #fafbfc; border: 1px solid var(--line); border-radius: 8px; font-size: 13px; line-height: 1.9; color: var(--ink); min-width: 320px; }}
.foot {{ color: var(--muted); font-size: 12px; margin-top: 20px; line-height: 1.8; }} .foot b {{ color: var(--ink); }}
.hidden {{ display: none; }}
</style>
</head>
<body>
<main class="wrap">
  <h1>PSP 系统发现目标 · 发现者统计排行</h1>
  <div class="sub">
    数据来源：<a href="{escape(source_url, quote=True)}" target="_blank" rel="noopener">PSP系统发现目标列表</a>。本仓库保存的来源快照页面标注更新时间为 {escape(snapshot_time)}。<br>
    统计口径：每颗天体按页面标注的发现者名单计数；多人共同发现时，每位署名实体各计一次，因此发现参与人次之和会大于目标总数。
  </div>

  <section class="cards" aria-label="统计概览">
    <div class="card"><div class="card-num">{total_entries}</div><div class="card-label">累计目标（颗）</div></div>
    <div class="card"><div class="card-num">{entity_count}</div><div class="card-label">署名实体（含团队）</div></div>
    {cards}
  </section>

  <div class="toolbar" aria-label="表格工具">
    <input id="search" type="search" placeholder="输入发现者姓名进行筛选" aria-label="按发现者姓名筛选">
    <button class="btn active" id="sortCount" type="button">按发现数量排序</button>
    <button class="btn" id="sortName" type="button">按姓名排序</button>
  </div>

  <div class="table-wrap">
    <table>
      <thead><tr><th>#</th><th>发现者</th><th>发现数量</th><th>覆盖率</th><th>覆盖率图示</th><th>参与发现的天体</th></tr></thead>
      <tbody id="tbody">
{rows}
      </tbody>
    </table>
  </div>

  <p class="foot"><b>说明：</b>“发现数量”是该署名实体参与发现的目标条目数（含合作发现）。“PSP团队”为原名单中的集体署名，并非个人；“未获证认”表示候选体尚未获得光谱证认；类型标签末尾的“:”表示来源页面标注的分类不确定。</p>
</main>
<script>
const tbody = document.getElementById("tbody");
const sourceRows = Array.from(tbody.querySelectorAll("tr"));
const search = document.getElementById("search");
const btnCount = document.getElementById("sortCount");
const btnName = document.getElementById("sortName");

function render(list) {{
  tbody.replaceChildren();
  list.forEach((row, index) => {{
    row.querySelector(".rank").textContent = index + 1;
    tbody.appendChild(row);
  }});
}}

function applyFilter() {{
  const keyword = search.value.trim();
  render(sourceRows.filter((row) => row.querySelector(".name").textContent.includes(keyword)));
}}

search.addEventListener("input", applyFilter);
btnCount.addEventListener("click", () => {{
  sourceRows.sort((a, b) => Number(b.dataset.count) - Number(a.dataset.count) || a.querySelector(".name").textContent.localeCompare(b.querySelector(".name").textContent, "zh"));
  btnCount.classList.add("active"); btnName.classList.remove("active"); applyFilter();
}});
btnName.addEventListener("click", () => {{
  sourceRows.sort((a, b) => a.querySelector(".name").textContent.localeCompare(b.querySelector(".name").textContent, "zh"));
  btnName.classList.add("active"); btnCount.classList.remove("active"); applyFilter();
}});
</script>
</body>
</html>'''


def main() -> None:
    """读取主数据并生成发布页面。"""
    data = read_json(DISCOVERERS_PATH)
    page = build_page(data)
    write_text(RANKING_PAGE_PATH, page)
    print(f"已写入：{RANKING_PAGE_PATH}")
    print(f"字节数：{len(page.encode('utf-8'))}")


if __name__ == "__main__":
    main()
