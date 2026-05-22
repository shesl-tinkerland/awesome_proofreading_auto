# 标准化输出基础格式 (Standardized Base Output Format)

本文件定义所有9个校对技能的统一输出基础格式。各技能在此基础上扩展技能特有字段。

## 1. 顶层结构

所有技能的输出JSON必须包含以下基础字段：

```json
{
  "skill_name": "技能名称（如 language_proofreading）",
  "segment_id": "段落/片段编号（如 S1_3）",
  "page_number": "页码（整数或页码字符串）",
  "issues": [],
  "summary": {
    "total_issues": 0,
    "critical_count": 0,
    "major_count": 0,
    "minor_count": 0
  },
  "status": "校对状态（pass/warning/fail）"
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `skill_name` | string | 是 | 技能标识符，与目录名一致 |
| `segment_id` | string | 是 | 内容片段唯一标识。表格/图片/参考文献等使用各自的ID类型（见下文映射表） |
| `page_number` | int/string | 是 | 页码 |
| `issues` | array | 是 | 检测到的问题列表（统一使用 `issues`，不再使用技能特定数组名） |
| `summary` | object | 是 | 按严重级别统计问题数量 |
| `status` | string | 是 | 整体校对结果：`pass`（无问题）、`warning`（有minor/major）、`fail`（有critical） |

### segment_id 命名映射

| 技能 | segment_id 格式 | 示例 |
|------|----------------|------|
| language_proofreading | `S{章节}_{段落}` | `S2_5` |
| medical_term_proofreading | `S{章节}_{段落}` | `S2_5` |
| clinical_logic_proofreading | `S{章节}_{段落}` | `S2_5` |
| data_consistency_proofreading | `S{章节}_{段落}` | `S2_5` |
| consistency_proofreading | `S{章节}_{段落}` | `S2_5` |
| reference_proofreading | `REF{序号}` | `REF3` |
| table_proofreading | `TBL{章节}-{序号}` | `TBL1-2` |
| image_proofreading | `IMG{章节}-{序号}` | `IMG1-1` |
| translation_proofreading | `S{章节}_{段落}` | `S2_5` |

---

## 2. Issues 数组中的问题对象

每个 issue 对象必须包含以下标准化字段：

```json
{
  "category": "问题类别",
  "severity": "critical/major/minor",
  "issue_type": "问题类型（技能特有）",
  "location": "具体位置描述",
  "description": "简洁问题描述",
  "current": "当前内容",
  "suggested": "建议修改内容",
  "reason": "修改依据（可选）",
  "rule": "相关规范/标准（可选）"
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `category` | string | 是 | 问题大类（技能级别定义，如 `grammar`、`clinical_logic`、`data_consistency`） |
| `severity` | string | 是 | 严重程度，固定三选一：`critical`、`major`、`minor` |
| `issue_type` | string | 是 | 问题细分类（技能级别定义） |
| `location` | string | 是 | 问题在文档中的具体位置（行号、单元格、字段名等） |
| `description` | string | 是 | 简洁问题描述（遵循各技能的简洁原则字数限制） |
| `current` | string | 是 | 当前文档中的实际内容（统一字段名） |
| `suggested` | string | 是 | 建议修改后的内容（统一字段名） |
| `reason` | string | 否 | 修改的依据或医学理由（≤20字） |
| `rule` | string | 否 | 相关国家标准或规范名称（如 `GB/T 15835-2011`） |

### 各技能的 category 与 issue_type 取值

| 技能 | category 值 | issue_type 取值范围 |
|------|------------|-------------------|
| language_proofreading | `grammar` | `punctuation`, `number_usage`, `unit`, `expression`, `logic_coherence`, `typo` |
| medical_term_proofreading | `medical_term` | `non_standard`, `abbreviation_undefined`, `context_mismatch`, `translation_error` |
| clinical_logic_proofreading | `clinical_logic` | `diagnosis_mismatch`, `lab_unreasonable`, `treatment_issue`, `timeline_error`, `data_conflict` |
| data_consistency_proofreading | `data_consistency` | `lab_description_mismatch`, `indicator_inconsistent`, `timeline_logic_error`, `value_out_of_range`, `data_contradiction` |
| consistency_proofreading | `consistency` | `abbreviation_undefined`, `term_inconsistent`, `name_inconsistent`, `drug_name_mixed`, `unit_inconsistent` |
| reference_proofreading | `reference` | `format_error`, `info_missing`, `info_error`, `citation_mismatch`, `doi_invalid` |
| table_proofreading | `table` | `numbering_error`, `header_issue`, `data_error`, `format_issue`, `cross_page_issue`, `note_issue` |
| image_proofreading | `image` | `numbering_error`, `quality_issue`, `caption_issue`, `content_mismatch`, `annotation_issue` |
| translation_proofreading | `translation` | `term_error`, `omission`, `over_translation`, `expression_issue`, `bilingual_error`, `format_issue` |
| expression_refinement | `refinement` | `word_precision`, `redundancy`, `collocation`, `register`, `repetition` |

---

## 3. 严重程度统一定义

所有技能使用相同的三级严重程度：

| 级别 | 英文 | 定义 | 通用标准 |
|------|------|------|---------|
| 严重 | `critical` | 可能导致理解偏差、临床误判或患者安全问题 | 必须修改 |
| 重要 | `major` | 影响准确性或一致性，但不直接危害安全 | 建议修改 |
| 轻微 | `minor` | 格式、表述等小问题，不影响准确性 | 可选修改 |

---

## 4. 技能扩展字段规范

各技能可在基础格式之上添加技能特有的扩展字段，放置在顶层 `issues` 同级。

### 扩展字段命名规范

- 扩展字段使用 `<技能焦点>_check` 格式命名（如 `data_consistency_check`）
- 扩展的数据验证字段使用 `<数据类型>_validation` 格式命名
- 技能特有问题数组统一归入 `issues`，不再单独建数组（向下兼容旧数组名可作为别名）

### 各技能扩展字段

| 技能 | 扩展字段 |
|------|---------|
| language_proofreading | `statistics: { character_count, error_count, error_rate }` |
| medical_term_proofreading | `terms_found[]`, `abbreviations[]` |
| clinical_logic_proofreading | `clinical_domain`, `evidence{ conflicting_items[], explanation }`, `data_consistency_check{}` |
| data_consistency_proofreading | `consistency_check{}`, `reference_ranges[]`, `conflicting_data{}` |
| consistency_proofreading | `term_info{ term, first_occurrence, current_occurrence, variations[] }` |
| reference_proofreading | `reference_type`, `authors`, `title`, `source`, `year`, `verified` |
| table_proofreading | `table_title`, `row_count`, `column_count`, `data_check{}` |
| image_proofreading | `image_type` |
| translation_proofreading | `original_text`, `translated_text`, `terminology_check{}`, `bilingual_accuracy_issues[]` |

---

## 5. 字段名统一映射表（旧名 -> 标准名）

各技能原有字段名映射到标准化名称：

| 旧字段名 | 标准字段名 | 涉及技能 |
|----------|-----------|---------|
| `current_content` | `current` | clinical_logic, data_consistency, medical_term |
| `current_value` | `current` | reference |
| `current_translation` | `current` | translation (issues内) |
| `suggested_fix` | `suggested` | clinical_logic, data_consistency, medical_term |
| `correct_value` | `suggested` | reference |
| `suggested_translation` | `suggested` | translation (issues内) |
| `suggestion` | `suggested` | table, image, medical_term(terms_found内) |
| `table_id` | `segment_id` | table |
| `image_id` | `segment_id` | image |
| `reference_id` | `segment_id` | reference |
| `clinical_logic_issues` | `issues` | clinical_logic |
| `data_consistency_issues` | `issues` | data_consistency |
| `context_validation_issues` | `issues` | medical_term |

---

## 6. 完整示例

以 language_proofreading 为例，展示包含所有基础字段和扩展字段的完整输出：

```json
{
  "skill_name": "language_proofreading",
  "segment_id": "S2_5",
  "page_number": 42,
  "issues": [
    {
      "category": "grammar",
      "severity": "major",
      "issue_type": "unit",
      "location": "第3行",
      "description": "单位符号错误",
      "current": "血压102/34mmHg",
      "suggested": "血压102/34mmHg",
      "reason": "单位符号使用不规范",
      "rule": "GB/T 15835-2011"
    }
  ],
  "statistics": {
    "character_count": 256,
    "error_count": 1,
    "error_rate": "0.39%"
  },
  "summary": {
    "total_issues": 1,
    "critical_count": 0,
    "major_count": 1,
    "minor_count": 0
  },
  "status": "warning"
}
```

---

## 7. 简洁原则（所有技能通用）

| 问题复杂度 | description | reason | suggested |
|-----------|-------------|--------|-----------|
| 格式/标点/单位错误 | 5字以内 | 可省略 | 直接给出修改 |
| 术语/数据/逻辑问题 | 10字以内 | ≤20字 | 明确指出修改内容 |
| 其他较复杂问题 | 15字以内 | ≤20字 | 给出具体建议 |

避免冗余：
- 不要在 description 中重复 current 的完整内容
- 不要使用"建议将XX修改为YY"等冗长表达
- 不要使用"建议检查"、"考虑修改"等模糊表达
