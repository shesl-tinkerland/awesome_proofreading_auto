---
name: proofread
description: Medical document proofreading skill that uses parallel AI agents to run 10 specialized proofreading checks (language, medical terms, clinical logic, data consistency, tables, images, references, translation, consistency, expression refinement) on medical documents (Word/PDF/TXT) and generates interactive HTML reports with error highlighting. Triggered by /proofread command.
---

# Medical Proofreading Skill

全面校对医学文档，使用并行 Agent 运行所有校对技能，收集结果，生成 HTML 校对报告。

## 资源路径约定

所有资源文件已打包在本 Skill 目录（`SKILL_DIR` = `.claude/skills/proofread/`）下：

| 资源类型 | 路径 | 用途 |
|---------|------|------|
| 校对技能定义 | `references/skills/{skill_name}/skill.md` | Agent 读取技能规则 |
| 检查清单 | `references/skills/{skill_name}/checklist.md` | Agent 读取检查项 |
| 基础输出格式 | `references/skills/_base_output_format.md` | 统一 JSON 输出规范 |
| HTML 模板 | `assets/report_template.html` | 报告生成脚本读取 |
| NHC 术语查询 | `scripts/lookup_term.py` | 医学术语规范性查询 |
| 知识库 JSON | `references/knowledge_base/*.json` | 缩写、检验值、术语数据 |

下文中所有 `{SKILL_DIR}` 均指 `.claude/skills/proofread/`。

## 用法

```
/proofread <文件路径> [--layout single|double] [--mode=hard|medium|easy]
```

示例：
- `/proofread data/gexin.docx` （会询问布局模式）
- `/proofread data/gexin.docx --layout=single` （单栏 PDF）
- `/proofread data/article.pdf --layout=double --mode=hard` （双栏 PDF）

**重要**：`--layout` 参数为必选项。如果用户未指定，**必须用 AskUserQuestion 询问用户**：
- "这个文档是单栏还是双栏布局？"，选项：single（单栏）/ double（双栏）

## 文档布局

| 布局 | 提取脚本 | HTML 报告 | 适用场景 |
|------|---------|----------|---------|
| `single`（单栏） | `output/_extract_pdf.py` | 单栏连续排列 | 大多数文档、Word 导出 PDF |
| `double`（双栏） | `output/_extract_pdf_double.py` | 按页面分左右栏 | 学术期刊、教科书双栏排版 |

**区别**：
- 单栏使用原始 `_extract_pdf.py`（已稳定，不做改动）
- 双栏使用 `_extract_pdf_double.py`：自动检测每页栏数，按左栏→右栏顺序提取文本，输出 `_columns.json` 记录栏位
- 双栏 HTML 报告按页面分组，每页内左右栏并排显示，全宽标题跨栏

## 运行模式

通过 `--mode` 参数控制每个 Agent 处理的技能数量，影响 Agent 总数、校对质量和运行速度：

| 模式 | 每个 Agent 技能数 | Agent 总数 | 并行 Agent 数 | 速度 | 质量 | 适用场景 |
|------|-------------------|-----------|--------------|------|------|---------|
| `hard` | 1 | chunks × 10 | 3 | 最慢 | 最高 | 重要文档、最终出版 |
| `medium`（默认） | 2-3 | chunks × 4 | 3 | 中等 | 较高 | 常规校对 |
| `easy` | 10 | chunks | 3 | 最快 | 一般 | 快速初筛、草稿审查 |

**默认使用 `medium` 模式**。如未指定 `--mode`，则使用 medium。

### 技能分组规则

10 个技能按以下方式分组（每组内按顺序排列）。分组原则：**将职责相近但互补的技能放在同一组**，避免跨组重叠。

| 模式 | 分组方式 |
|------|---------|
| `hard` | 每个技能独立 1 组（共 10 组） |
| `medium` | 组A: language, expression_refinement（文本层面：语法+润色）<br>组B: medical_term, consistency, translation（术语层面：标准+一致+翻译）<br>组C: clinical_logic, data_consistency（医学层面：逻辑+数据）<br>组D: reference, table, image（文档元素：文献+表格+图片） |
| `easy` | 全部 10 个技能为 1 组 |

**分组逻辑**：
- **组A（文本层面）**：language 检查正确性，expression 检查优化。互补而非重叠。
- **组B（术语层面）**：medical_term 检查标准性，consistency 检查一致性，translation 检查翻译准确性。三者从不同角度处理术语，边界已明确。
- **组C（医学层面）**：clinical_logic 检查诊断逻辑，data_consistency 检查数据合理性。互补而非重叠。
- **组D（文档元素）**：reference/table/image 各自处理不同类型的文档元素，无重叠。

## 重要约束

- **并发限制（最高优先级）**：**严禁同时运行超过 3 个校对 Agent**。采用**即时补位策略**：始终保持 3 个 Agent 并行运行，任何一个完成（成功或失败）后**立即**启动下一个，不等同批其他 Agent 完成。
- **上下文保护**：主 Agent **严禁**用 Read 工具读取 `_document_text.txt`、`_tables.json`、`_images.json`、`_graphics.json` 等大文件。所有文件操作通过 Bash 执行 Python 脚本完成。
- **状态持久化（防上下文丢失）**：主 Agent 在第2步开始时用 CronCreate 设置一个每 20 分钟触发的定时任务（`durable: false`），prompt 为 `"将当前校对进度写入 output_{docname}/chunks/_progress.json，包含 pending（待执行任务列表）、running（当前运行中的任务）、completed（已完成）、failed（失败）。格式: {pending: [{chunk: N, skills: [...]}], running: [...], completed: [...], failed: [...]}。不要中断正在运行的 Agent。"`。所有校对任务完成后**立即**用 CronDelete 删除此定时任务。如果会话因上下文压缩而丢失状态，主 Agent 从 `_progress.json` 恢复 pending 队列继续执行。
- **进度透明**：主 Agent 每次收到子 Agent 完成通知时，用 Bash 快速扫描 chunks 目录汇报进度，不读取 JSON 内容。
- **分段用脚本**：Step 1.5 使用 awk 方案自动分段。
- **合并保护**：合并脚本**不得删除 chunk 文件**。合并后必须验证每个技能的 issue 数量，如果某技能显示 0 issues 但存在 chunk 文件，说明 JSON 解析失败，需要检查并修复。

## 执行流程

### 输出目录结构

每个文档对应一个独立的输出目录：`output_{docname}/`。其中 `docname` 由文件名去掉扩展名得到。

```
output_{docname}/                # 每个文档独立目录
├── _document_text.txt           # 带编号的文档原文
├── _tables.json                 # 表格结构 + AI 识别的 Markdown + 跳过范围
├── _images.json                 # 图片元信息（PDF 提取时生成）
├── _graphics.json               # 图形内容处理结果（流程图/图表/示意图）
├── _columns.json                # 双栏布局段落栏位信息（仅 --layout=double 时生成）
├── tables.md                    # 人类可读的表格 Markdown 汇总
├── chunks/                      # 分段中间文件（合并后可整体删除）
│   ├── _chunks.txt              #   分段信息
│   ├── _chunk_{N}.txt           #   各分段文本（Agent 读取）
│   └── *_chunk{N}.json          #   Agent 输出的分 chunk 校对结果（合并后删除）
├── results/                     # 合并后的校对结果（最终 JSON）
│   ├── language_proofreading.json
│   ├── medical_term_proofreading.json
│   └── ...（共 9 个文件）
├── images/                      # PDF 提取的图片 + 表格区域截图
│   ├── fig_*.{jpeg,png}         #   文档中的图片
│   └── table_*.{jpeg,png}       #   表格区域截图（供 AI 视觉识别）
├── logs/                        # Agent 执行日志
│   └── *.log
└── {docname}.html               # 最终 HTML 校对报告

output/                          # 共享脚本目录（不属于特定文档）
├── _extract_pdf.py              # PDF 提取脚本（单栏）
├── _extract_pdf_double.py       # PDF 提取脚本（双栏）
└── _generate_report.py          # 报告生成脚本（支持 --layout single|double）
```

**示例**：校对 `data/创伤救治手册第20章.pdf` 时，输出目录为 `output_创伤救治手册第20章/`。

**生命周期说明**：
- `chunks/` 是中间产物，合并完成后整个目录可删除
- `results/` 是合并后的最终校对数据，供报告生成脚本读取
- `*.html` 是最终交付物
- `_document_text.txt`、`_tables.json`、`_images.json` 是文档提取产物，报告生成需要读取
- `_graphics.json` 是 AI 视觉识别产物，报告生成需要读取

### 第1步：读取文档内容

根据文件类型提取纯文本：

- **`.docx`**：运行 `python3 -c "from docx import Document; d=Document('<文件路径>'); [print(p.text) for p in d.paragraphs]"`
- **`.doc`**：先运行 `textutil -convert docx '<文件路径>' -output /tmp/proofread_input.docx`，再按 .docx 方式读取
- **`.pdf`**：根据 `--layout` 参数选择提取脚本：
  - `single`（默认）：运行 `python3 output/_extract_pdf.py '<文件路径>' --output 'output_{docname}'`
  - `double`：运行 `python3 output/_extract_pdf_double.py '<文件路径>' --output 'output_{docname}'`（额外输出 `_columns.json`）
  - 脚本自动完成：
  - 智能段落合并（基于 x 坐标分析缩进/续行，避免物理行截断）
  - 页眉页脚过滤（"作者样"、"创伤救治手册"、纯数字页码）
  - 表格检测与匹配（`_tables.json`），含表格区域截图（`images/table_{id}.png`）和 `table_image`/`markdown` 字段
  - 图片提取（保存到 `output/images/`，元信息写入 `output/_images.json`）
  - 输出合并后的段落到 `output/_document_text.txt`
- **`.txt` / `.md`**：直接用 Read 工具读取

对于 `.pdf`，脚本完成后直接跳到第1.5步（段落已编号保存到 `output_{docname}/_document_text.txt`）。
对于其他格式，提取文本后手动为每个段落添加编号，保存到 `output_{docname}/_document_text.txt`：

```
[P0] 第一段文字
[P1] 第二段文字
...
```

确保 `output_{docname}/` 目录存在。

### 第1.2步：表格识别与处理（仅 PDF，有表格时执行）

**提取后必须验证**：PDF 提取脚本可能遗漏所有表格。必须执行以下检查：

```bash
# 1. 统计 _tables.json 中的表格数量
python3 -c "
import json
with open('output_{docname}/_tables.json') as f:
    tables = json.load(f)
print(f'_tables.json 中有 {len(tables)} 个表格')
"

# 2. 搜索文档中所有表格标题
grep "^\[P.*\] 表[0-9]" output_{docname}/_document_text.txt
```

**如果 `_tables.json` 中表格数量为 0 但文档中有表格标题**，说明 `find_tables()` 和 `pdfplumber` 都失败了。此时：
1. **先尝试手动截图**（如果有源 PDF）：对每个表格标题对应的页面区域截图
2. **否则接受乱码**：表格内容以碎片形式存在于 `_document_text.txt` 中，校对 Agent 会在 table_proofreading 中报告表格碎片化问题
3. **不要花太多时间手动重建 Markdown**：性价比低，报告生成时乱码文本仍会显示

PDF 提取脚本（`_extract_pdf.py`）已自动完成**双策略表格提取**：

**策略1 — PyMuPDF `find_tables()`**（快速，适合有明确线条的表格）：
- 检测表格区域（`find_tables(vertical_strategy='text', horizontal_strategy='text')`）
- 质量过滤（<8列、≥2行、≥30% 行含多非空单元格）
- 匹配表格标题（空间邻近 + 跨页检测）
- 截取表格区域截图（`images/table_{id}.png`，dpi=200）
- 自动生成 Markdown（但 `data` 字段仅供参考，**经常将单元格拆错**）

**策略2 — pdfplumber 补充提取**（针对 PyMuPDF 遗漏的表格）：
- 对 PyMuPDF 未能匹配的表格标题，自动调用 pdfplumber 重新提取
- pdfplumber 基于文本位置分析，对无边框/复杂布局表格检测率更高
- 提取结果直接生成 Markdown 写入 `_tables.json`（`source: 'pdfplumber'`）
- 如果 pdfplumber 也未能提取，脚本会打印遗漏的表格 ID

**提取完成后的检查**：

```bash
# 检查 _tables.json 中有多少表格被自动提取
python3 -c "
import json
with open('output_{docname}/_tables.json') as f:
    tables = json.load(f)
for t in tables:
    has_md = '✓' if t.get('markdown') else '✗'
    src = t.get('source', 'pymupdf')
    print(f'{has_md} {t[\"table_id\"]} ({src}, {t[\"rows\"]}rows)')
print(f'Total: {len(tables)} tables')
"

# 搜索文档中所有表格标题
grep "^表[0-9]" output_{docname}/_document_text.txt
```

如果仍有表格标题不在 `_tables.json` 中，或已有表格的 `markdown` 字段为空，才需要手动重建（下方场景C）。

**表格渲染管线**：
- **有 Markdown 时**（PyMuPDF 或 pdfplumber 自动生成）：直接使用 → `<textarea>` → marked.js 渲染
- **仅有截图无 Markdown**：截图 → AI 视觉识别 → 重建 Markdown → 同上
- **完全遗漏**：从 `_document_text.txt` 乱码文本中分析列/行结构 → 重建 Markdown → 同上

#### 手动重建（仅当自动提取失败时）

**场景A：有截图但无 Markdown**（`table_image` 存在，`markdown` 为空或质量差）— 对每个需要重建的表格：

1. **读取截图**：用 Read 工具读取 `output_{docname}/images/table_{id}.png`
2. **识别结构**：仔细识别表头、合并单元格、所有行列内容（不要参考 `data` 字段，它经常是错的）
3. **确定跳过范围**：见下方方法
4. **生成 Markdown**：标准 Markdown 表格格式（`| 列1 | 列2 |` + `|---|---|` 分隔行）
5. **写入 `_tables.json`**：更新 `markdown`、`para_skip_start`、`para_skip_end` 字段

**场景B：完全遗漏**（表格标题不在 `_tables.json` 中）— 对每个遗漏的表格：

1. **定位乱码区域**：在 `_document_text.txt` 中找到表格标题段落（如 `[P221] 表28.1　...`），向下浏览找到表格乱码碎片的起止范围
2. **分析表格结构**：阅读乱码文本，识别列标题（通常是最前面的几个段落）和行数据。常见模式：
   - 第一批段落 = 列标题（跨段落断开）
   - 后续段落 = 按行列出的数据（每行数据对应多个连续段落）
   - 行标签通常出现在每行第一个单元格的末尾（与下一行的列标签粘连）
3. **重建 Markdown**：根据上下文语义还原表格内容，注意跨段落拼接同一单元格的文字
4. **确定跳过范围**：见下方方法
5. **写入 `_tables.json`**：追加新条目（见下方代码示例）

**识别要求**：
- 保持原始表格结构，不要遗漏任何单元格
- 合并单元格内容用空格连接（不换行），或用 `<br>` 换行
- 数字和单位保持原文，不要修改
- 如果表格跨页，图片可能不完整，尽可能识别可见部分
- 空单元格保留为空（两个 `|` 之间无内容）

**确定 `para_skip_start` 和 `para_skip_end` 的方法**：
```bash
# 在 _document_text.txt 中查找表格标题段落
grep -n "表28.2" output_{docname}/_document_text.txt
# 输出：362:[P361] 表28.2　生物综合征
# para_skip_start = 362（标题的下一个段落）
# 然后向下浏览，找到下一个正常正文段落（章节标题或连续正文）
# 假设表格内容到 P452，下一个正文从 P453 开始
# para_skip_end = 452
```

**写入方式**：

**更新已有表格**（场景A）：
```bash
python3 -c "
import json
with open('output_{docname}/_tables.json', 'r') as f:
    tables = json.load(f)
# 对每个表格更新以下字段：
# tables[N]['markdown'] = '''| 列1 | 列2 |\n|---|---|\n| 数据 | 数据 |'''
# tables[N]['para_skip_start'] = 362   # 标题段落的下一行
# tables[N]['para_skip_end'] = 452     # 表格内容最后一行
with open('output_{docname}/_tables.json', 'w') as f:
    json.dump(tables, f, ensure_ascii=False, indent=2)
print(f'Updated {len(tables)} tables')
"
```

**追加遗漏表格**（场景B）：
```bash
python3 -c "
import json
with open('output_{docname}/_tables.json', 'r') as f:
    tables = json.load(f)
tables.append({
    'table_id': '表28.1',
    'title_text': '表28.1　使用CRESS来识别潜在的化学剂',
    'page': 9,
    'bbox': [0, 0, 0, 0],       # 无截图时 bbox 可为空
    'rows': 7,
    'cols': 7,
    'data': [],                  # 无截图时 data 可为空
    'para_index': 221,           # 表格标题的段落编号（P221）
    'markdown': '''| CRESS | 神经毒剂 | 氰化物 | ... |\n| --- | --- | --- | ... |\n| ... |''',
    'para_skip_start': 222,      # 乱码起始段落（标题下一行）
    'para_skip_end': 270,        # 乱码结束段落
})
with open('output_{docname}/_tables.json', 'w') as f:
    json.dump(tables, f, ensure_ascii=False, indent=2)
"
```

#### 表格校对技能的特殊处理

`table_proofreading` 技能（第5号）需要读取表格内容。有两种方式：
- **有 `markdown` 字段时**：Agent prompt 中指明读取 Markdown 文本进行表格校对
- **无 `markdown` 字段时**：Agent 读取原始 `_document_text.txt` 中的碎片段落（效果较差）

建议：在第2步的 Agent prompt 中，对 `table_proofreading` 技能额外补充：
```
如有表格相关数据，读取 output_{docname}/_tables.json 中的 markdown 字段辅助校对。
```

#### 图片处理（自动完成，无需手动操作）

`_extract_pdf.py` 自动提取 PDF 中的嵌入图片：
- 通过 `page.get_images()` 获取图片列表
- 通过 `doc.extract_image()` 提取图片字节
- 通过 `page.get_image_rects()` 获取图片在页面上的位置
- 自动匹配图注文字（"图XX.X"格式）
- 图片保存到 `images/` 目录，元信息写入 `_images.json`

`_generate_report.py` 自动渲染图片：在正文中遇到图注段落时，查找匹配的图片并渲染为 `<div class="image-container"><img ...><div class="image-caption">图注</div></div>`。

也可将所有表格 Markdown 合并输出为 `output_{docname}/tables.md` 供后续参考。

### 第1.3步：图形内容识别与处理（仅 PDF，有图形区域时执行）

PDF 中的流程图、示意图、数据图表等图形内容，被文本提取后会产生乱码。需要通过截图 + AI 视觉判断来处理。

**注意**：当前 `_extract_pdf.py` 没有自动检测非表格图形区域的功能。图形区域需要手动识别。

#### 检测图形区域

**方法一（推荐）：通过图注标题定位**

这是最可靠的方法。图形内容被文本提取后，图注标题（"图XX.X ..."）通常能正确提取，而图形内容变成乱码。步骤：

1. 搜索所有图注标题：
   ```bash
   grep -n "^\[P.*\] 图[0-9]" output_{docname}/_document_text.txt
   ```
2. 对照 `_images.json`：检查每个图注对应的图片是否已提取（通过 `caption` 字段匹配）
3. 未在 `_images.json` 中出现的图注 = 图形内容（流程图/图表/示意图），周围会有乱码段落
4. 在 `_document_text.txt` 中浏览每个未提取图片的图注标题前后的段落，确定乱码范围（`para_range`）

**方法二：搜索连续短碎片段落**

在 `_document_text.txt` 中搜索连续 3+ 个短段落（每段 < 15 字），这些区域通常是流程图/图表被拆解后的结果。排除已有 `_images.json` 和 `_tables.json` 覆盖的区域。

**确定 `para_range` 边界**：
- 起始：向上找到最后一个正常可读的段落（非乱码），其下一行即为起始
- 结束：图注标题所在的段落（包含在 range 内，因为标题也需被跳过并由报告渲染器处理）
- 如果图注前后都有正常文本，则 range 仅包含乱码段落 + 图注标题

**截取图形区域**（需要源 PDF 文件）：
```bash
python3 -c "
import fitz, os
doc = fitz.open('data/原始文件.pdf')
page = doc[page_num - 1]  # PDF 页码从1开始，fitz 从0开始
clip = fitz.Rect(x0, y0, x1, y1)  # 图形区域的坐标
pix = page.get_pixmap(clip=clip, dpi=200)
os.makedirs('output_{docname}/images', exist_ok=True)
pix.save('output_{docname}/images/graphic_{id}.png')
print(f'Saved: graphic_{id}.png')
"
```

如果源 PDF 不可用，**仍应创建 `_graphics.json`** 以跳过乱码文本。将 `image_path` 设为空字符串，`action` 设为 `screenshot_only`，`skip_proofread` 设为 `true`。报告渲染器会跳过 `para_range` 内的所有段落（不显示乱码文本），虽然不会显示图片，但比显示乱码好得多。

```json
{
  "id": "graphic_28_1",
  "type": "flowchart",
  "page": 8,
  "para_range": [71, 189],
  "image_path": "",
  "action": "screenshot_only",
  "skip_proofread": true,
  "mermaid_code": "",
  "extracted_text": [],
  "skip_reason": "CBRN全灾种应对流程图。源PDF不可用，无法截图。跳过乱码文本。"
}
```

#### AI 视觉判断流程

对每个图形区域的截图，执行以下 **三级判断**：

```
读取图形截图
    │
    ├─ Q1: 这是什么类型的内容？
    │   ├─ 表格 → 走第1.2步表格流程（已处理）
    │   ├─ 流程图/示意图 → 继续 Q2
    │   ├─ 数据图表（柱状图/折线图/饼图等） → 继续 Q3
    │   ├─ 照片/插画 → 标记为 image，无需文本校对
    │   └─ 无法判断 → 走「仅截图」路径
    │
    ├─ Q2（流程图）：能否准确复刻？
    │   评估标准：
    │   - 节点数 ≤ 8 个
    │   - 无复杂分支（不超过 3 个判断节点）
    │   - 无颜色编码/特殊形状（圆角、渐变等）
    │   - 文字标签完整可读
    │   │
    │   ├─ 是 → 尝试 Mermaid 复刻 + 文本校对
    │   │   同时生成 mermaid 代码和截图，报告中优先显示 Mermaid
    │   │
    │   └─ 否 → 走「仅截图」路径
    │
    ├─ Q3（数据图表）：能否可靠提取数据？
    │   评估标准：
    │   - 数值标注是否清晰可读
    │   - 坐标轴标签是否完整
    │   - 图例是否可辨认
    │   │
    │   ├─ 是 → 截图插入 + AI 提取文本标注供校对 Agent 审查
    │   │
    │   └─ 否 → 走「仅截图」路径
    │
    └─ 「仅截图」路径：
        - 将截图插入 HTML 报告替代乱码文本
        - 标记为 `skip_proofread: true`
        - 校对 Agent 不审查此区域
        - 在报告中标注「图片区域，跳过文本校对」
```

#### 处理结果写入

将图形内容处理结果写入 `output_{docname}/_graphics.json`：

```json
[
  {
    "id": "graphic_1",
    "type": "flowchart | chart | diagram | photo",
    "page": 5,
    "para_range": [120, 135],
    "image_path": "images/graphic_1.png",
    "action": "mermaid | screenshot_with_text | screenshot_only",
    "skip_proofread": false,
    "mermaid_code": "...",
    "extracted_text": ["文本标注1", "文本标注2"],
    "skip_reason": ""
  }
]
```

#### 报告渲染规则

| action | 报告中的渲染方式 |
|--------|----------------|
| `mermaid` | Mermaid 图表（需引入 mermaid.js CDN） |
| `screenshot_with_text` | 截图 + 下方显示提取的文本标注（可标记错误） |
| `screenshot_only` | 有 `image_path` 时：截图 + "跳过文本校对" 标注；无 `image_path` 时：跳过乱码段落，不显示图片 |

#### 能力不足时的兜底策略

当 AI 判断自身无法准确处理图形内容时（包括但不限于）：
- 流程图过于复杂（多层级嵌套、大量分支）
- 图表数值模糊、标注密集重叠
- 图形中包含特殊符号或非标准字符
- 截图分辨率不足，文字难以辨认

**一律回退到 `screenshot_only`**，不强行校对。宁可漏检，不可误报。

### 第1.5步：文档分段

使用脚本自动分段，**主 Agent 不需要读取 `_document_text.txt`**。

**优先使用 awk**（稳定，不会挂起）：

```bash
cd output_{docname}/chunks && awk '
BEGIN { chunk=1; count=0; delete buf; buf_size=0 }
{
    buf[buf_size] = $0; buf_size++; count++
    if (count == 40) {
        for (i = 0; i < buf_size; i++) print buf[i] > sprintf("_chunk_%d.txt", chunk)
        close(sprintf("_chunk_%d.txt", chunk))
        for (i = 0; i < 10; i++) buf[i] = buf[buf_size - 10 + i]
        buf_size = 10; count = 10; chunk++
    }
}
END {
    if (buf_size > 0) {
        for (i = 0; i < buf_size; i++) print buf[i] > sprintf("_chunk_%d.txt", chunk)
    }
    printf("Created %d chunks\n", chunk)
}' ../_document_text.txt
```

分段参数：`CHUNK_SIZE=40`（每段 40 个段落），`OVERLAP=10`（相邻分段重叠 10 段）。

分段完成后，手动生成 `_chunks.txt`（或用 Python 脚本读取 chunk 文件头尾段落编号生成）。

### 第2步：主 Agent 直接调度校对 Agent

分段完成后，主 Agent 构建任务列表，通过 **Agent tool 直接调度子 Agent** 并行执行校对。每个子 Agent 处理一个 chunk × 一组 skills。不使用 `claude -p` 外部进程，不依赖 `_dispatch_plan.json` 或 `_task_{id}.txt` 文件。

**10个技能列表**：

| # | 技能目录名 | 中文名 |
|---|-----------|--------|
| 1 | language_proofreading | 语言组织校对 |
| 2 | medical_term_proofreading | 医学术语校对 |
| 3 | clinical_logic_proofreading | 临床逻辑校对 |
| 4 | data_consistency_proofreading | 数据一致性校对 |
| 5 | table_proofreading | 表格校对 |
| 6 | image_proofreading | 图片校对 |
| 7 | reference_proofreading | 参考文献校对 |
| 8 | translation_proofreading | 翻译校对 |
| 9 | consistency_proofreading | 术语一致性校对 |
| 10 | expression_refinement | 表达润色 |

#### 任务列表构建

分段完成后，主 Agent 通过 Bash 获取 chunk 文件列表，结合技能分组规则构建完整任务列表：

```bash
# 获取 chunk 文件数量
ls output_{docname}/chunks/_chunk_*.txt | wc -l
```

任务列表 = chunk 文件 × 技能分组。例如 medium 模式下，32 chunks × 3 组 = 96 个任务。

每个任务 = (chunk 编号, 技能列表)。主 Agent 在内存中维护 pending 队列，初始包含所有未完成的任务。

**状态恢复**：如果 `output_{docname}/chunks/_progress.json` 存在，优先从文件恢复 pending 队列（跳过已完成的任务），而非从头构建：
```bash
# 检查是否有可恢复的进度
cat output_{docname}/chunks/_progress.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Resumable: {len(d.get(\"pending\",[]))} pending, {len(d.get(\"completed\",[]))} done, {len(d.get(\"failed\",[]))} failed')"
```

**检查已完成任务**：对每个任务，检查其技能列表对应的所有 `{skill}_chunk{N}.json` 文件是否已存在。全部存在的任务标记为已完成，不加入 pending。

```bash
# 快速统计已完成的 JSON 文件数量
ls output_{docname}/chunks/*_chunk*.json 2>/dev/null | wc -l
```

#### 子 Agent prompt 模板

每个子 Agent 使用以下 prompt 模板（主 Agent 在构建时替换变量）：

```
你是医学文档校对专家。请完成以下校对任务：

## 文本格式说明

提取的文本中存在以下特殊标记，校对时应正确处理：

1. **上角标引用标记**：`<sup>[N]</sup>` 标记是原文中的上角标引用编号（如参考文献角标）。
   - **不要**对 `<sup>` 包裹的内容标记括号类型错误（全角/半角）
   - **不要**对 `<sup>` 内容标记位置、间距或格式问题
   - 引用编号的正确性由 reference_proofreading 技能单独负责
2. **段落标识符**：每行开头的 `[PN]`（如 `[P0]`、`[P1]`）是段落编号标记，不是正文内容，校对时忽略。

## 文档分段
读取文件: {chunk_file_path}

## 校对技能

对以下每个技能，依次执行校对：

{for each skill in group}

### 技能: {skill_name}
1. 读取技能定义: {SKILL_DIR}/references/skills/{skill_name}/skill.md
2. 读取检查清单: {SKILL_DIR}/references/skills/{skill_name}/checklist.md（如存在）
3. 阅读文档分段内容，按照 skill.md 中的规则和检查清单逐项检查
4. 将发现的 issues 写入 JSON 文件: {output_json_path}
   - JSON 格式必须遵循 skill.md 中定义的 schema
   - 直接输出纯 JSON，不要用 ```json 代码块包裹
   - 如果未发现任何问题，输出: {"issues": []}

{end for}

{可选：仅当技能组包含 table_proofreading 时添加}
## 表格辅助数据
如有表格相关数据，读取 output_{docname}/_tables.json 中的 markdown 字段辅助校对。
读取 para_skip_start/para_skip_end 了解表格段落范围。

{可选：仅当技能组包含 medical_term_proofreading 时添加}
## NHC术语知识库
文档中出现的疾病名、症状名、手术名、临床检查名等术语，使用以下工具查询其规范性：
```bash
python3 {SKILL_DIR}/scripts/lookup_term.py <术语名>      # 精确查询（查不到则非规范名）
python3 {SKILL_DIR}/scripts/lookup_term.py <术语名> --all # 含模糊匹配
```
查询结果中：
- "✓ 规范名" = 术语正确，无需修改
- "→ 别名" = 术语是NHC记录的又称，建议改为标准名
- "未找到" = 术语不在NHC库中（仅临床术语触发此规则，基础科学术语不触发）

注意：对文档中每个疑似非规范术语执行查询，但不要过度查询常见/明确规范的术语。

## 输出要求
- 每个技能的输出必须是合法 JSON
- JSON 中不要包含未转义的引号或控制字符
- 如果某个技能在当前分段中未发现任何问题，输出: {"issues": []}
```

#### 调度策略

**核心原则：始终保持恰好 3 个 Agent 并行运行，即时补位。**

0. **启动定时保存**：调度开始前，用 CronCreate 设置每 20 分钟自动保存进度的定时任务：
   ```
   CronCreate(cron: "*/20 * * * *", recurring: true, durable: false,
     prompt: "将当前校对进度写入 output_{docname}/chunks/_progress.json，包含 pending（待执行任务列表）、running（当前运行中的任务）、completed（已完成）、failed（失败）。格式: {pending: [{chunk: N, skills: [...]}], running: [...], completed: [...], failed: [...]}。不要中断正在运行的 Agent。")
   ```

1. **构建待执行队列**：
   - 扫描 chunks 目录，对每个任务检查其所有输出 JSON 是否已存在
   - 所有 JSON 都已存在的任务标记为已完成
   - 未完成的任务按 (chunk 编号, 组编号) 排序加入 pending 队列

2. **启动 Agent**：
   - 使用 Agent 工具，设置 `run_in_background: true`，`subagent_type: "general-purpose"`
   - 初始启动时，在**同一条消息**中发出最多 3 个 Agent 调用
   - 每个 Agent 的 prompt 使用上方模板生成

3. **即时补位**：当收到某个后台 Agent 完成通知时：
   a. 用 Bash 检查该任务的输出 JSON 文件是否存在
   b. 从 pending 队列取下一个任务
   c. **立即**启动新 Agent（不等其他正在运行的 Agent 完成）
   d. 始终保持 3 个后台 Agent 运行（直到 pending 不足 3 个）

4. **完成条件**：pending 为空且所有后台 Agent 都完成。完成后**立即用 CronDelete 删除定时保存任务**。

5. **重试**：对失败的 Agent（输出 JSON 不存在），重新加入 pending 队列尾部，最多重试 1 次

#### 进度跟踪

每次 Agent 完成后，主 Agent 用 Bash 快速扫描进度：

```bash
total=$(ls output_{docname}/chunks/*_chunk*.json 2>/dev/null | wc -l | tr -d ' ')
echo "Progress: $total JSON files"
```

主 Agent **严禁读取** JSON 文件内容，只统计文件数量。

### 第2.5步：合并 chunk JSON 文件

所有 Agent 完成后，通过 Python 脚本将同一 skill 的多个 chunk JSON 合并为单个文件。

**关键改进**（基于实际运行经验）：
1. **使用绝对路径**：避免 CWD 依赖导致 glob 匹配失败
2. **不删除 chunk 文件**：合并后保留 chunk 文件，以便验证和重试
3. **增强 robust_load**：先用 `json.loads` 直接尝试，失败后再尝试修复（而非先修复再解析）
4. **合并后验证**：如果某技能有 chunk 文件但合并后 0 issues，打印警告
5. **逐文件记录**：记录每个 chunk 文件的 issue 数，便于定位问题

```bash
python3 -c "
import json, glob, re, os

# 必须使用绝对路径
import os
BASE = os.getcwd()
DOCNAME = '{docname}'
CHUNKS_DIR = os.path.join(BASE, f'output_{DOCNAME}', 'chunks')
RESULTS_DIR = os.path.join(BASE, f'output_{DOCNAME}', 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

SKILLS = [
    'language_proofreading', 'medical_term_proofreading', 'clinical_logic_proofreading',
    'data_consistency_proofreading', 'table_proofreading', 'image_proofreading',
    'reference_proofreading', 'translation_proofreading', 'consistency_proofreading',
    'expression_refinement',
]

def robust_load(path):
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read().strip()
    # 策略1: 去掉 markdown 代码块包裹
    if raw.startswith('\`\`\`'):
        raw = re.sub(r'^\`\`\`json?\s*\n?', '', raw)
        raw = re.sub(r'\n?\s*\`\`\`\s*$', '', raw)
    # 策略2: 直接解析
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    # 策略3: 修复字符串内未转义引号（保守策略，仅处理明显情况）
    fixed = raw
    # 修复控制字符
    fixed = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', fixed)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass
    # 策略4: 更激进的引号修复
    result, i = [], 0
    while i < len(raw):
        if raw[i] == '\"':
            result.append('\"'); i += 1
            buf = []
            while i < len(raw):
                if raw[i] == '\\\\' and i+1 < len(raw):
                    buf.append(raw[i:i+2]); i += 2
                elif raw[i] == '\"':
                    rest = raw[i+1:].lstrip()
                    if not rest or rest[0] in ',:]}':
                        break
                    else:
                        buf.append('\\\\\"'); i += 1
                else:
                    buf.append(raw[i]); i += 1
            result.append(''.join(buf))
            if i < len(raw): result.append('\"'); i += 1
        else:
            result.append(raw[i]); i += 1
    try:
        return json.loads(''.join(result))
    except:
        return None

for skill in SKILLS:
    pattern = os.path.join(CHUNKS_DIR, f'{skill}_chunk*.json')
    chunk_files = sorted(glob.glob(pattern))
    if not chunk_files:
        print(f'SKIP: {skill} (no chunk files)')
        continue

    all_issues = []
    parse_errors = 0
    for cf in chunk_files:
        data = robust_load(cf)
        if data:
            # 兼容多种 issues key（canonical: 'issues'，legacy: 其他 key）
            issues = []
            if isinstance(data, dict):
                for key in ['issues', 'clinical_logic_issues', 'data_consistency_issues',
                            'context_validation_issues', 'bilingual_accuracy_issues']:
                    val = data.get(key, [])
                    if val:
                        issues = val
                        break
            elif isinstance(data, list):
                issues = data
            all_issues.extend(issues)
        else:
            parse_errors += 1
            print(f'  WARN: failed to parse {os.path.basename(cf)}')

    with open(os.path.join(RESULTS_DIR, f'{skill}.json'), 'w', encoding='utf-8') as f:
        json.dump({'issues': all_issues}, f, ensure_ascii=False, indent=2)

    status = f'OK: {skill}.json (merged {len(chunk_files)} chunks, {len(all_issues)} issues'
    if parse_errors:
        status += f', {parse_errors} parse errors'
    # 验证：有 chunk 文件但 0 issues 需要警告
    if len(all_issues) == 0 and len(chunk_files) > 0:
        status += ' ** WARNING: 0 issues from non-zero chunks, possible JSON format problem **'
    print(status)

# chunk 文件保留不删除，合并成功后可手动清理：
# rm output_{docname}/chunks/*_chunk*.json
"
```

**合并后必须检查**：如果任何技能显示 `** WARNING: 0 issues **`，说明 JSON 解析可能失败。此时需要：
1. 检查问题 chunk 的 JSON 文件格式：`head -5 chunks/{skill}_chunk1.json`
2. 如果格式损坏，对问题 chunk 重新运行 agent
3. 重新合并

合并完成后，进入第3步。

### 第3步：通过脚本合并结果，生成 HTML 报告

> **注意**：主 Agent 在所有校对 Agent 完成后执行此步骤。

**核心原则：不要用 Read 工具读取 JSON 文件。** JSON 内容全部由 Python 脚本在 Bash 中处理，不进入主 Agent 上下文。

#### 执行方式

编写一个 Python 脚本（写到 `output/_generate_report.py`），通过 Bash 执行。脚本接受命令行参数：
```
python3 output/_generate_report.py <输出文件名> [文档标题] [--layout single|double]
```
例如：`python3 output/_generate_report.py gexin "第1章 创伤流行病学"`（单栏，默认）
双栏：`python3 output/_generate_report.py article "双栏文档" --layout double`（自动读取 `_columns.json`，按页面分左右栏渲染）

脚本负责：
1. 读取所有 `output_{docname}/results/*.json`
2. 容错解析 JSON（见下方「JSON 容错」）
3. 合并、去重、排序
4. 读取 `output_{docname}/_document_text.txt` 获取原文
5. 读取 `output_{docname}/chunks/_chunks.txt`（如有）获取章节分段
6. 读取 `output_{docname}/_tables.json` 获取表格 Markdown 和段落跳过范围
7. 读取 `output_{docname}/_images.json` 获取图片数据和图注
8. 读取 `output_{docname}/_graphics.json` 获取图形内容处理结果（如有）
9. 生成 `output_{docname}/{docname}.html`
10. 打印简要统计（主 Agent 只需看到这个输出）

**禁止**：在主 Agent 中使用 Read 工具读取任何 JSON 文件。

#### JSON 容错策略

Agent 生成的 JSON 常见问题：字符串内含未转义引号、控制字符等。脚本必须内置容错：

```python
def robust_json_load(filepath):
    """容错加载JSON文件，自动修复常见问题"""
    with open(filepath, 'r', encoding='utf-8') as f:
        raw = f.read()

    # 第1次尝试：直接解析
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # 第2次：修复字符串内未转义的引号
    fixed = fix_inner_quotes(raw)
    fixed = fix_control_chars(fixed)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    # 第3次：逐字段修复（逐个 "key": "value" 对处理）
    fixed = fix_field_by_field(raw)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError as e:
        print(f"SKIP {filepath}: {e}")
        return None  # 返回None表示跳过该文件
```

脚本对每个 JSON 文件的处理流程：
- 成功解析 → 提取 issues，打印 `OK: filename (N issues)`
- 修复后解析 → 提取 issues，打印 `OK: filename (N issues, fixed X errors)`
- 无法解析 → 跳过该文件，打印 `SKIP: filename (reason)`

#### 合并规则

1. **收集**：脚本读取 output/ 下所有技能的 JSON 文件，提取所有 issues
2. **归一化**：不同技能的 JSON 结构不同，脚本需统一为 `{skill, category, severity, location, current, suggested, reason, para_num}` 格式
3. **去重**：段落号相同 + 错误文本前20字相同 → 合并为一条，取 severity 最高的，合并 skill 名
4. **排序**：从 location 字段解析 `P(\d+)` 提取段落号作为排序键，无段落号的排末尾
5. **编号**：排序后依次分配 error1, error2, ..., errorN

#### HTML 模板

HTML 模板存放在 `{SKILL_DIR}/assets/report_template.html`（CSS + JS + 占位符）。脚本读取模板，填充数据后输出。

如果 `{SKILL_DIR}/assets/report_template.html` 不存在，脚本内联生成（模板见下方）。

#### 错误类型映射

| JSON category 字段 | CSS class | 中文标签 |
|---|---|---|
| grammar / expression | grammar | 语法/逻辑 |
| punctuation | punctuation | 标点符号 |
| typo / wording | typo | 错别字 |
| format | format | 格式问题 |
| terminology | terminology | 术语错误 |
| translation | translation | 翻译问题 |
| clinical_logic | clinical_logic | 临床逻辑 |
| data_consistency | data_consistency | 数据一致性 |
| table | table | 表格问题 |
| image | image | 图片问题 |
| reference | reference | 参考文献 |
| consistency | consistency | 术语一致性 |
| refinement | refinement | 表达润色 |

#### 错误-段落智能匹配

Agent 输出的 `location` 字段（如 `P161`）可能不准确。脚本内置智能匹配机制，通过 `find_error_paragraph()` 函数实现：

1. **解析位置范围**：从 location 字段提取段落号范围（如 `P6-P10` → [6,7,8,9,10]）
2. **三阶段匹配**：
   - Phase 1：在 location 指定范围内精确搜索 `current` 文本
   - Phase 2：在全文所有段落中精确搜索
   - Phase 3：去空白模糊匹配（应对 Agent 输出中的空格差异）
3. **预计算**：渲染前为每个错误计算 `matched_para` 字段，渲染时直接查表
4. **匹配率统计**：输出如 `Error-paragraph matching: 85/100 (85%)`

#### HTML 生成规则

1. **内容区域**：将原文按章节（从 _chunks.txt 解析）组织在 `.section` 中，有错误的位置用 `<span class="error-mark {type}" data-error="errorN">标记文本</span>` 标注
2. **多错误合并标记**：同一段落中指向相同文本的多个错误合并到同一 `<span>`，`data-error` 属性用空格分隔多个 ID（如 `data-error="error1 error3"`）
3. **尾标点容错**：错误文本末尾的 `。` `，` `、` `；` `：` 等标点在原文中不存在时仍可匹配
4. **表格渲染**：有 `markdown` 字段的表格 → `<textarea class="md-table-src">` + marked.js 转换为 HTML `<table>`；同时跳过 `para_skip_start` 到 `para_skip_end` 范围内的段落
5. **图片渲染**：匹配图注段落 → `<div class="image-container"><img src="images/..."> + 图注</div>`
6. **图形渲染**：根据 `_graphics.json` 中 `action` 字段 — `mermaid` → mermaid.js 图表；`screenshot_with_text` → 截图 + 提取文本；`screenshot_only` → 截图 + "跳过文本校对" 标注
7. **错误面板**：右侧固定面板，扁平列表，按段落号升序排列，每条错误显示来源技能标签（`.error-skill-tag`）
8. **统计区**：按错误类型汇总数量
9. **图例**：只显示实际出现过的错误类型
10. **交互**：点击文中错误标记 ↔ 右侧面板高亮联动

#### 脚本预期输出

主 Agent 只需看到 Bash 的 stdout：

```
OK: language_proofreading.json (81 issues)
OK: medical_term_proofreading.json (10 issues)
SKIP: clinical_logic_proofreading.json (empty)
OK: reference_proofreading.json (34 issues, fixed 2 quotes)
...
Total: 193 issues after dedup
Categories: {'语法/逻辑': 81, '翻译问题': 59, ...}
Error-paragraph matching: 180/193 (93%)
Report: output/gexin.html
```

如果脚本输出包含 `RETRY_FAILED:` 行（exit code 1），说明部分 JSON 解析失败。进入第3.5步重试。

### 第3.5步：重试失败的技能（仅在脚本报告失败时执行）

脚本输出的 `RETRY_FAILED:` 行会列出解析失败的技能名（逗号分隔），例如：
```
RETRY_FAILED: clinical_logic_proofreading,reference_proofreading
```

**重试流程**：
1. 删除失败的 JSON 文件：`rm output_{docname}/results/{skill_name}.json`
2. 对每个失败的技能，用 Agent 工具重新执行（使用第2步中相同的 prompt 模板），可并行启动
3. 在 Agent prompt 中**额外强调**：
   ```
   重要：输出必须是合法 JSON。不要在 JSON 中包含未转义的引号、控制字符或 markdown 格式标记。
   直接输出纯 JSON，不要用 ```json 代码块包裹。
   ```
4. 所有重试 Agent 完成后，重新运行生成脚本：
   ```
   python3 output/_generate_report.py <输出文件名> [文档标题] [--layout single|double]
   ```
5. 如果仍然失败，**最多重试 2 次**。第 2 次仍失败的技能直接跳过，用已有结果生成报告

### 第4步：汇报结果

用 `open output_{docname}/{docname}.html` 在浏览器中打开报告。

向用户汇报：共运行了几个技能，发现了多少问题，报告已保存到 output_{docname}/{docname}.html。
