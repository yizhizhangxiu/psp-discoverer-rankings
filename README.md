# PSP 发现者统计排行

本仓库将 **PSP 系统发现目标列表** 的网页转换为可审计的发现者统计数据，并生成可直接浏览的静态排行页面。项目保留原始数据、结构化处理结果、生成脚本与验证脚本，以便每次更新都能追溯到对应来源。[1]


## 项目内容

| 路径 | 用途 |
|---|---|
| `data/raw/psp_page.html` | PSP 目标列表的原始页面快照，是数据处理的唯一输入。 |
| `data/processed/discoverers.json` | 主数据，包含目标记录、发现者排行、每位署名实体参与的对象清单和数据来源元信息。 |
| `data/processed/parsed_entries.json` | 仅含目标名称和规范化类型的辅助数据，用于类别统计和交叉验证。 |
| `scripts/parse_discoverers.py` | 主解析脚本：提取目标、类型、发现者署名并生成主数据。 |
| `scripts/parse_psp.py` | 辅助解析脚本：生成规范化的“目标—类型”清单。 |
| `scripts/generate_html.py` | 发布页生成脚本：从主数据动态计算统计卡片、排行、覆盖率和对象明细。 |
| `scripts/verify_all.py` | 全量一致性验证：核对原始页面、两个 JSON 文件、排行和对象明细。 |
| `scripts/audit.py`、`scripts/audit2.py` | 深度审计：分别检查端到端数据一致性和网页对象明细。 |
| `scripts/check_html.py`、`scripts/check_tokens.py` | 快速质量检查与 `PSP团队` 署名诊断。 |
| `docs/index.html` | 生成后的静态排行页面，可直接在浏览器中打开。 |
| `requirements.txt` | 脚本运行依赖。 |

## 统计口径

每条目标按原页面列出的发现者署名进行统计。若一颗目标由多人共同发现，每位署名实体均记为参与 1 次，因此“发现参与人次”会大于独立目标数。`PSP团队` 是原列表中的集体署名，并非个人，页面会特别标识。

类型字段中的 `未证认` 和 `未获证认` 会统一规范为 **未获证认**。网页中的类别、目标总数、署名实体数和占比均从当前 `discoverers.json` 动态计算，不再写死固定数值。

## 本地运行

请使用 Python 3.11 或兼容版本，并在仓库根目录安装依赖后按下列顺序运行。所有脚本均使用相对项目根目录的跨平台路径，可在 Windows、macOS 和 Linux 中执行。

```bash
python -m pip install -r requirements.txt
python scripts/parse_discoverers.py
python scripts/parse_psp.py
python scripts/generate_html.py
python scripts/verify_all.py
python scripts/audit.py
python scripts/audit2.py
python scripts/check_html.py
```

完成后，浏览器直接打开 `docs/index.html` 即可查看最新排行页面。最后三个验证脚本都会在发现不一致时以非零状态终止，便于人工更新时进行质量把关。

## 隔月人工更新流程

| 阶段 | 操作 | 完成标准 |
|---|---|---|
| 1. 保存来源 | 将最新目标列表页面另存为 `data/raw/psp_page.html`。 | 页面完整保留目标名称、类型与发现者名单。 |
| 2. 生成数据 | 依次运行两个解析脚本与网页生成脚本。 | 两个 JSON 和 `docs/index.html` 均已更新。 |
| 3. 执行核验 | 运行 `verify_all.py`、`audit.py`、`audit2.py` 与 `check_html.py`。 | 所有脚本均报告通过。 |
| 4. 人工复核 | 重点检查新出现的类型文本、人员署名与 `PSP团队` 上下文。 | 无异常，或已记录人工处理原因。 |
| 5. 提交发布 | 将源快照、派生 JSON、网页及更新说明一次性提交。 | 提交记录能复现该次排行结果。 |

## 质量与可维护性

当前版本将公共路径、读写逻辑、类型规范化和类别归并集中在 `scripts/common.py`，避免不同脚本各自维护一套规则。验证脚本不再依赖固定的 223 条目标或固定分类卡片，而是从实际数据推导预期值。因此，后续源页面新增目标后，项目可以直接检测数据链路是否仍然一致。

原始页面使用 HTML 样式来表达关键字段：橙色目标名称和 16px 发现者名单。若来源网站改变这些结构或样式，请先检查 `parse_discoverers.py` 的提取逻辑，再进行下一次正式发布。

## 数据来源

数据源为 PSP 系统的发现目标列表。仓库内保留的是一次本地页面快照；对于最新信息，请以来源页面为准。[1]

## 参考资料

[1]: https://nadc.china-vo.org/psp/article/20171116151450 "PSP 系统发现目标列表"
