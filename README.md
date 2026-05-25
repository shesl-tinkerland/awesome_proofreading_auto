<div align="center">

# Awesome Proofreading Auto

**AI 驱动的中文医学文档智能审稿系统**

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-supported-blueviolet)](https://claude.ai/code)
[![Codex CLI](https://img.shields.io/badge/OpenAI%20Codex-supported-412991)](https://github.com/openai/codex)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-supported-orange)](https://github.com/open-claw/open-claw)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-green)](https://www.python.org/)
[![Try on Socialistic](https://socialistic.ai/api/embed/awesome-proofreading-auto-f44f43)](https://socialistic.ai/zh/skill/awesome-proofreading-auto-f44f43?utm_source=github&utm_medium=readme&utm_campaign=20260524-copywriting-doctor-skills&utm_content=badge)

[功能特性](#-功能特性) · [快速开始](#-快速开始) · [使用指南](#-使用指南) · [架构设计](#-架构设计) · [迁移到其他领域](#-迁移到其他领域)

</div>

---

## 写在前面

这个项目最初是给我媳妇做的一套审稿辅助工具。她是医学编辑，每天要审大量的医学稿件，而传统的审稿方式需要逐字逐句地检查术语、数据、格式、逻辑，工作量巨大且容易遗漏。

于是我想：能不能让 AI 来帮她做这些重复性的检查工作？让 AI 负责基础审校，她只需要审核 AI 标记出来的问题，把精力集中在内容质量的判断上。

这就是 **Awesome Proofreading Auto** 的由来 —— 一个专门为中文医学文档设计的智能审稿系统，支持多种 AI Agent 平台运行。

> **Token 消耗提醒**：本系统采用"分项检查 + 通读精读结合"的策略，会对文档进行多轮、多维度、多 Agent 并行审校。一次完整的审稿流程会消耗**大量 Token**（视文档长度和模式而定），请确保你有充足的 API 额度。

## 背景

医学文档的审稿工作涉及多个专业维度：术语规范（卫健委 42,217 条标准术语）、临床逻辑一致性、数据准确性、参考文献格式（GB/T 7714-2025）、表格图片校验等。人工逐一检查耗时且易错，而通用的 AI 校对工具缺乏医学领域的专业知识和标准支撑。

本项目通过 **10 个专项审校技能** + **国家卫健委术语知识库** + **多 Agent 并行架构**，实现了覆盖全面的自动化审稿流程，并生成交互式 HTML 报告供人工最终审核。

## 功能特性

### 10 项专项审校技能

| # | 技能 | 校验内容 | 亮点 |
|---|------|---------|------|
| 1 | **语言组织校对** | 语法、标点、数字用法、单位、逻辑连贯性 | 8 大类别全覆盖 |
| 2 | **医学术语校对** | 卫健委标准术语合规性 | 42,217 条 NHC 标准术语实时查询 |
| 3 | **临床逻辑校对** | 诊断-症状-检验-治疗的逻辑一致性 | 跨段落推理验证 |
| 4 | **数据一致性校对** | 检验值、参考范围、指标关联 | 132 项检验值知识库 |
| 5 | **表格校对** | 编号、表头、数据准确性、跨页表格 | 双策略 PDF 表格提取 |
| 6 | **图片校对** | 编号、图注、图片质量、标注完整性 | 自动图片提取与匹配 |
| 7 | **参考文献校对** | GB/T 7714-2025 标准、DOI 验证 | 格式+内容双重校验 |
| 8 | **翻译校对** | 术语翻译准确性、英文缩写规范 | 中英双语对照检查 |
| 9 | **术语一致性校对** | 全文术语统一、缩写首次定义 | 跨章节一致性追踪 |
| 10 | **表达润色** | 用词精准度、冗余、搭配优化 | 不改变原意的润色建议 |

### 核心能力

- **卫健委术语知识库**：内置 42,217 条国家卫健委标准化临床术语，支持别名 → 标准名映射
- **检验值参考库**：132 项常见检验指标的正常范围，自动校验数据合理性
- **医学缩写库**：190+ 医学缩写的中英文对照
- **交互式 HTML 报告**：点击标记 ↔ 错误详情双向联动，支持表格/图片/流程图渲染
- **断点续审**：每 20 分钟自动保存进度，崩溃后可恢复
- **多格式支持**：`.docx`、`.doc`、`.pdf`、`.txt`、`.md`

## 快速开始

### 在线试用

如果只是想先看审稿效果，可以直接打开上面的 Socialistic 入口，上传 Word/PDF 医学稿件并选择单栏/双栏布局与校对力度，无需先安装本地依赖或配置 API key。

### 支持的 Agent 平台

本 Skill 采用标准的 Markdown 技能定义格式，理论上支持所有具备 Agent 调度能力的 AI 编码工具：

| 平台 | 状态 | 安装方式 |
|------|------|---------|
| [Claude Code](https://claude.ai/code) | 已验证 | 将 `proofread/` 复制到 `.claude/skills/` |
| [OpenAI Codex CLI](https://github.com/openai/codex) | 理论支持 | 将 `proofread/` 复制到 `.codex/skills/` |
| [OpenClaw](https://github.com/open-claw/open-claw) | 理论支持 | 将 `proofread/` 复制到对应 skills 目录 |
| 其他支持 Skill/Agent 的平台 | 需适配 | 技能定义为纯 Markdown，适配成本低 |

> 本项目的 Skill 定义完全采用 Markdown + JSON 格式，不依赖任何特定 Agent 平台的私有 API，因此具备良好的跨平台兼容性。

### 前置条件

- 一个支持 Agent 调度的 AI 编码工具（推荐 [Claude Code](https://claude.ai/code)）
- Python 3.8+ 环境
- 以下 Python 依赖：

```bash
pip install pymupdf pdfplumber python-docx
```

### 安装

1. 克隆仓库到本地：

```bash
git clone https://github.com/your-username/awesome_proofreading_auto.git
cd awesome_proofreading_auto
```

2. 将 skill 目录安装到你的 Agent 平台：

**Claude Code：**
```bash
mkdir -p .claude/skills
cp -r proofread .claude/skills/proofread
```

**OpenAI Codex CLI：**
```bash
mkdir -p .codex/skills
cp -r proofread .codex/skills/proofread
```

**OpenClaw / 其他平台：**
将 `proofread/` 复制到对应平台的 skills 目录即可。如果平台支持直接在项目目录加载技能，也可以不做任何复制，直接在 `awesome_proofreading_auto` 目录下启动。

3. 确保依赖已安装：

```bash
pip install pymupdf pdfplumber python-docx
```

### 运行

使用 `/proofread` 命令启动审稿（以 Claude Code 为例，其他平台命令格式类似）：

```
# 基本用法
/proofread data/your_document.docx

# 指定布局模式（单栏/双栏）
/proofread data/article.pdf --layout=double

# 指定审稿模式
/proofread data/book.pdf --layout=single --mode=hard
```

审稿完成后会自动在浏览器中打开交互式 HTML 报告。

## 使用指南

### 布局模式

| 参数 | 说明 | 适用场景 |
|------|------|---------|
| `--layout=single` | 单栏布局 | Word 导出 PDF、普通文档 |
| `--layout=double` | 双栏布局 | 学术期刊、教科书双栏排版 |

如果未指定布局，系统会询问你。双栏模式会自动检测每页栏数，按左栏 → 右栏顺序提取文本。

### 审稿模式

通过 `--mode` 参数控制每个 Agent 处理的技能数量：

| 模式 | Agent 数量 | 速度 | 质量 | 适用场景 |
|------|-----------|------|------|---------|
| `hard` | chunks × 10 | 最慢 | 最高 | 重要文档、最终出版 |
| `medium`（默认） | chunks × 4 | 中等 | 较高 | 常规审稿 |
| `easy` | chunks × 1 | 最快 | 一般 | 快速初筛、草稿审查 |

`medium` 模式下 10 个技能按职责分组为 4 组并行执行：

- **组 A（文本层面）**：语言组织 + 表达润色
- **组 B（术语层面）**：医学术语 + 术语一致性 + 翻译
- **组 C（医学层面）**：临床逻辑 + 数据一致性
- **组 D（文档元素）**：参考文献 + 表格 + 图片

### 使用小技巧

#### 1. PDF 表格处理

PDF 中的表格提取采用双策略（PyMuPDF + pdfplumber），大部分表格可自动提取。如果自动提取效果不理想：

- 系统会自动截取表格区域截图，并尝试 AI 视觉识别重建
- 对于极其复杂的表格，可能需要手动辅助
- 运行后检查终端输出的 `Total: N tables` 确认提取数量

#### 2. 大文档分块策略

系统自动将文档按 40 段落一块、10 段落重叠进行分块。重叠区域确保跨段落的错误不会被遗漏。

#### 3. Token 消耗优化

- **初筛用 `easy` 模式**：快速获取文档整体质量概况
- **重点章节用 `hard` 模式**：对需要重点审核的章节单独处理
- **利用断点续审**：中断后可从进度文件恢复，不浪费已完成的审校结果

#### 4. 报告解读

HTML 报告中的错误按三级严重度标记：

| 级别 | 颜色 | 含义 | 建议 |
|------|------|------|------|
| Critical（严重） | 红色 | 可能导致理解偏差或临床误判 | 必须修改 |
| Major（重要） | 橙色 | 影响准确性或一致性 | 建议修改 |
| Minor（轻微） | 蓝色 | 格式、表述等小问题 | 可选修改 |

#### 5. NHC 术语查询

可独立使用术语查询工具验证术语规范性：

```bash
python .claude/skills/proofread/scripts/lookup_term.py 心房颤动          # 精确查询
python .claude/skills/proofread/scripts/lookup_term.py 心房颤动 --all   # 模糊匹配
python .claude/skills/proofread/scripts/lookup_term.py --chapter 心血管   # 按科室查询
python .claude/skills/proofread/scripts/lookup_term.py --stats            # 统计信息
```

## 架构设计

### 整体架构

```
┌──────────────────────────────────────────────────────┐
│                   SKILL.md (主控)                      │
│              /proofread 命令触发入口                    │
└──────────────┬───────────────────────────────────────┘
               │
    ┌──────────▼──────────┐
    │    文档提取层         │
    │  PDF / DOCX / TXT    │
    │  表格 / 图片 / 图形    │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │    智能分块层         │
    │  40段/块, 10段重叠    │
    │  awk 稳定分块         │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │   并行 Agent 调度层    │
    │  3 Agent 并行         │
    │  即时补位策略          │
    │  进度持久化            │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │   结果合并 + 报告生成   │
    │  JSON 容错解析         │
    │  错误-段落智能匹配     │
    │  交互式 HTML 报告      │
    └──────────────────────┘
```

### 目录结构

```
.claude/skills/proofread/
├── SKILL.md                           # 主 Skill 定义（命令入口 + 执行流程）
├── assets/
│   └── report_template.html           # HTML 报告模板
├── references/
│   ├── knowledge_base/                # 知识库
│   │   ├── abbreviations.json         # 190+ 医学缩写
│   │   ├── lab_values.json            # 132+ 检验值参考范围
│   │   ├── medical_terms.json         # 126+ 医学术语
│   │   └── nhc_clinical_terms.json    # 42,217 条 NHC 标准术语
│   └── skills/                        # 10 个专项审校技能
│       ├── _base_output_format.md     # 统一 JSON 输出规范
│       ├── language_proofreading/
│       │   ├── skill.md               # 技能定义（规则 + schema）
│       │   └── checklist.md           # 检查清单
│       ├── medical_term_proofreading/
│       ├── clinical_logic_proofreading/
│       ├── data_consistency_proofreading/
│       ├── table_proofreading/
│       ├── image_proofreading/
│       ├── reference_proofreading/
│       ├── translation_proofreading/
│       ├── consistency_proofreading/
│       └── expression_refinement/
└── scripts/
    ├── lookup_term.py                 # NHC 术语查询工具
    └── parse_nhc_terms.py             # NHC 数据解析工具
```

### 技能架构

每个审校技能由两个文件组成：

- **`skill.md`**：定义校对规则、输出 JSON schema、扩展字段
- **`checklist.md`**：结构化检查清单，Agent 逐项执行

所有技能遵循统一的输出格式（`_base_output_format.md`），包含标准化的严重度分级（critical / major / minor）和字段命名。

### 并行调度策略

```
待执行队列: [Task1, Task2, Task3, Task4, Task5, ...]

Agent 1: Task1 ████████ 完成 → 立即启动 Task4
Agent 2: Task2 ████████████ 完成 → 立即启动 Task5
Agent 3: Task3 ██████ 完成 → 立即启动 Task6

始终保持恰好 3 个 Agent 并行运行
任何 Agent 完成（成功或失败）后立即补位
```

关键设计决策：

- **即时补位**：不等同批其他 Agent 完成，完成一个立即启动下一个
- **上下文保护**：主 Agent 不读取大文件，所有文件操作通过子 Agent 或 Bash 完成
- **状态持久化**：每 20 分钟自动保存进度到 `_progress.json`，支持崩溃恢复
- **容错 JSON 解析**：三级策略处理 Agent 输出的畸形 JSON

### 输出结构

```
output_{docname}/
├── _document_text.txt                 # 带编号的文档原文
├── _tables.json                       # 表格结构 + Markdown
├── _images.json                       # 图片元信息
├── _graphics.json                     # 图形内容处理结果
├── chunks/                            # 分段中间文件
│   ├── _chunk_{N}.txt                 #   分段文本
│   └── *_chunk{N}.json                #   Agent 输出结果
├── results/                           # 合并后的最终结果
│   ├── language_proofreading.json
│   ├── medical_term_proofreading.json
│   └── ...（共 10 个）
├── images/                            # 提取的图片 + 表格截图
└── {docname}.html                     # 最终 HTML 审稿报告
```

## 迁移到其他领域

本系统的架构设计是**领域无关**的，审校逻辑完全由 `references/skills/` 下的技能定义驱动。迁移到其他领域只需修改技能和知识库，不需要改动调度框架。

### 迁移步骤

#### 1. 替换知识库（`references/knowledge_base/`）

根据目标领域准备专业知识库 JSON 文件。例如迁移到**法律文档审校**：

```json
// law_terms.json
{
  "民法典": {
    "standard_name": "中华人民共和国民法典",
    "abbreviation": "民法典",
    "category": "法律名称"
  }
}
```

#### 2. 修改/替换技能定义（`references/skills/`）

每个技能由 `skill.md` + `checklist.md` 组成，定义了校对规则和输出 schema。

**保留的技能**（多数领域通用）：
- `language_proofreading` - 语言组织（语法、标点等）
- `consistency_proofreading` - 术语一致性
- `expression_refinement` - 表达润色
- `reference_proofreading` - 参考文献（调整引用标准即可）
- `table_proofreading` - 表格
- `image_proofreading` - 图片

**需要替换的技能**（领域专用）：
- `medical_term_proofreading` → 改为领域术语校对（如 `legal_term_proofreading`）
- `clinical_logic_proofreading` → 改为领域逻辑校对（如 `legal_logic_proofreading`）
- `data_consistency_proofreading` → 改为领域数据校对（如 `legal_citation_proofreading`）
- `translation_proofreading` → 按需保留或替换

#### 3. 编写技能定义

每个技能的 `skill.md` 需要包含：

```markdown
# 技能名称

## 校对范围
定义本技能负责检查的内容范围

## 校对规则
- 规则1：...
- 规则2：...

## 输出格式
遵循 _base_output_format.md 的标准 JSON schema
```

#### 4. 更新查询脚本（`scripts/`）

将 `lookup_term.py` 中的数据源替换为目标领域的术语库。

#### 5. 调整 SKILL.md 中的技能列表

在 SKILL.md 的技能列表部分更新为新技能。

### 迁移示例

| 目标领域 | 可复用技能 | 需新建/替换技能 | 知识库 |
|---------|-----------|---------------|--------|
| **法律文档** | 语言、一致性、润色、参考文献、表格、图片 | 法律术语、法条逻辑、案例引用 | 法律术语库、法条库 |
| **学术论文** | 语言、一致性、润色、参考文献、表格、图片 | 学术术语、实验逻辑、数据一致性 | 学科术语库 |
| **技术文档** | 语言、一致性、润色、表格、图片 | 技术术语、代码逻辑、API 一致性 | 技术术语库、API 规范 |
| **教育教材** | 语言、一致性、润色、参考文献、表格、图片 | 学科术语、知识点逻辑、题目准确性 | 学科知识库 |

## 声明

### 许可证

本项目采用 **[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)** 许可证。

```
本作品仅供个人学习和交流使用，严禁用于任何商业用途。
未经授权的商业使用将追究法律责任。
```

### 免责声明

- 本系统是**辅助审稿工具**，所有标记的问题均需人工最终审核确认
- AI 审校结果可能存在误报或遗漏，不保证 100% 准确
- 对于医学文档中的临床决策相关内容，请务必以专业医学人员审核为准
- 本系统不对因使用或误用产生的任何损失承担责任

## 致谢

- [Claude Code](https://claude.ai/code)、[OpenAI Codex](https://github.com/openai/codex)、[OpenClaw](https://github.com/open-claw/open-claw) 等 AI Agent 平台
- 国家卫健委 - 提供标准化临床术语数据
- 所有为医学出版质量默默付出的编辑们

---

<div align="center">

### 关注我们

了解更多 AI + 效率工具的内容，欢迎关注抖音账号

**抖音：乌卡 AI 笔记**（抖音号：37892085442）

大模型算法专家 / 大厂 AI 负责人，分享 AI 实战经验与效率工具

<img src="assets/douyin_qrcode.jpg" alt="乌卡 AI 笔记" width="200" />

**如果这个项目对你有帮助，请给个 Star ⭐**

</div>
