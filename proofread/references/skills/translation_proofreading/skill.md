# 中英文翻译校对技能 (Translation Proofreading Skill)

## 技能描述

专门用于校对医学翻译书籍（英译中）的翻译质量，检查术语一致性、翻译准确性、语体风格、文化适配等问题。

## 输出要求

### 简洁原则

按照问题类型采用不同的输出策略：

1. **术语错误**（术语不统一、漏译、误译等）：
   - description：简洁指出问题（10字以内）
   - suggestion：给出明确的修改建议
   - reason：简要说明依据（可选，不超过20字）
   - 示例：
     ```json
     {
       "current": "肿瘤",
       "suggested": "癌肿",
       "description": "解剖学术语使用错误",
       "reason": "tumor应为'癌肿'"
     }
     ```

2. **语言表达问题**（欧化句式、表达生硬等）：
   - description：简洁描述（15字以内）
   - suggestion：给出通顺的改写
   - reason：说明更符合中文表达习惯（可选）
   - 示例：
     ```json
     {
       "current": "这个问题是被很多研究者所关注的",
       "suggested": "很多研究者关注这个问题",
       "description": "欧化句式",
       "reason": "符合中文表达习惯"
     }
     ```

3. **漏译、多译**：
   - description：直接说明问题
   - suggestion：给出增删建议
   - reason：简单说明（10字以内）
   - 示例：
     ```json
     {
       "current": "患者出现了发热",
       "suggested": "患者出现发热",
       "description": "多译'了'",
       "reason": "语境中无需过去时"
     }
     ```

4. **格式问题**（单位、标点、缩写等）：
   - description：简短指出（5字以内）
   - suggestion：直接修改
   - reason：可省略或填写相关规范

### 避免冗余

1. **不要重复current中的内容**：
   - ❌ 错误："建议将'肿瘤'修改为'癌肿'"
   - ✅ 正确：current只写"肿瘤"

2. **不要使用模糊表达**：
   - ❌ 错误："建议对译文进行检查"
   - ✅ 正确：直接给出具体修改建议

3. **不要过度解释**：
   - ❌ 错误："该词汇在英文中表示XXX，而在中文中通常翻译为YYY，建议..."
   - ✅ 正确：简洁描述问题，给出明确建议

## 校对原则

1. **忠实原则**：准确传达原文内容和意图
2. **通顺原则**：译文符合中文表达习惯
3. **规范原则**：使用规范医学术语和表达
4. **一致原则**：全书术语和译法保持一致

## 校对项目

### 1. 术语一致性检查
- [ ] 医学术语翻译统一
- [ ] 缩写首次出现有全称
- [ ] 药品名称规范（通用名/商品名）
- [ ] 解剖名词规范
- [ ] 疾病名称规范（ICD编码）
- [ ] 检查项目名称统一
- [ ] 计量单位规范

### 2. 翻译准确性检查
- [ ] 核心信息无遗漏
- [ ] 无过度翻译
- [ ] 数字、日期准确
- [ ] 专业概念准确
- [ ] 因果关系准确
- [ ] 否定、限制准确

### 3. 语言通顺性检查
- [ ] 符合中文语法习惯
- [ ] 避免欧化句式
- [ ] 句子结构清晰
- [ ] 逻辑关系明确
- [ ] 语序自然
- [ ] 表达简洁

### 4. 语体风格检查
- [ ] 符合学术写作规范
- [ ] 用词得体
- [ ] 避免口语化表达
- [ ] 客观中立
- [ ] 正式程度适当

### 5. 特殊翻译问题
- [ ] **直译vs意译**：判断是否需要调整
- [ ] **被动语态**：中文中是否适当调整
- [ ] **长句处理**：是否需要拆分
- [ ] **定语从句**：处理是否得当
- [ ] **插入语**：位置是否合适

### 6. 专业表达检查
- [ ] 症状描述准确
- [ ] 诊断标准完整
- [ ] 治疗方案清晰
- [ ] 剂量用法明确
- [ ] 不良反应表述规范
- [ ] 注意事项完整

### 7. 文化适配检查
- [ ] 机构名称处理得当
- [ ] 人名翻译规范
- [ ] 地名翻译统一
- [ ] 特有概念有注释
- [ ] 文化差异有说明

### 8. 格式一致性检查
- [ ] 英文原文与中文对应
- [ ] 专业术语英汉对照保留
- [ ] 关键术语保留英文
- [ ] 引用文献格式统一

### 9. 双语术语精确性检查 ⭐ 核心增强
- [ ] **英文缩写的中文翻译准确**
  - 例：ESR = erythrocyte sedimentation rate（红细胞沉降率）✅
  - 错误：ESR = exchangeable sodium ratio ❌
  - 例：NT-proBNP = N-terminal brain natriuretic peptide（N末端脑钠肽前体）
  - 错误：NT-proBNP = "钠尿肽前体"（漏译N-terminal）
- [ ] **同一英文术语翻译前后一致**
  - 例：tumor不混用"肿瘤"和"癌肿"（需根据上下文确定规范译法）
  - 例：physician不混用"医生"和"医师"（统一译法）
- [ ] **专业术语英文原文正确**
  - 例：brain natriuretic peptide ✅
  - 错误：brain natriuretic peptide（拼写错误需标注）
  - 例：angiotensin-converting enzyme ✅
  - 错误：angiotension converting enzyme
- [ ] **英文缩写展开后全称正确**
  - 例：ACEI = angiotensin-converting enzyme inhibitors ✅
  - 错误：ACEI = angiotensin converting enzyme inhibitor（漏s）
- [ ] **容易混淆的英文缩写正确识别**
  - 例：ACEI（血管紧张素转换酶抑制剂）vs ARB（血管紧张素II受体拮抗剂）
  - 例：CRP（C反应蛋白）vs CR（肌酐清除率）
  - 例：PT（凝血酶原时间）vs PTT（部分凝血酶时间）
- [ ] **后缀/前缀翻译准确**
  - 例：-itis = 炎，-ectomy = 切除术，-scopy = 镜检查
  - 例：hyper- = 高/过多，hypo- = 低/过少
- [ ] **希腊词根翻译准确**
  - 例：cardio- = 心，neuro- = 神经，gastro- = 胃
- [ ] **拉丁词根翻译准确**
  - 例：renal = 肾，hepatic = 肝，pulmonary = 肺
- [ ] **数字/单位翻译准确**
  - 例：10⁹/L = ×10⁹/L（每升）
  - 例：mmHg = 毫米汞柱

## 常见翻译问题

### A. 基础翻译问题
| 问题类型 | 示例 | 修改建议 |
|---------|------|---------|
| 直译生硬 | "病人经历了一个快速的恢复" | "病人恢复迅速" |
| 欧化句式 | "这个问题是被很多研究者所关注的" | "很多研究者关注这个问题" |
| 术语不统一 | tumor/肿瘤/癌肿混用 | 统一使用"肿瘤" |
| 漏译 | 原文有3点，译文只有2点 | 补充遗漏内容 |
| 过度翻译 | 添加原文没有的解释 | 删除额外内容 |
| 否定错误 | double negative理解错误 | 检查否定逻辑 |

### B. 双语术语精确性问题 ⭐ 新增
| 问题类型 | 示例 | 修正建议 |
|---------|------|---------|
| 英文缩写翻译错误 | ESR = "exchangeable sodium ratio" | ESR = erythrocyte sedimentation rate（红细胞沉降率） |
| 缩写展开错误 | ACEI = "angiotensin converting enzyme inhibitor" | ACEI = angiotensin-converting enzyme inhibitors（复数） |
| 漏译词根/前缀 | NT-proBNP = "脑钠肽前体" | NT-proBNP = N-terminal（N末端）脑钠肽前体 |
| 同一术语多种译法 | tumor译为"肿瘤"/"癌肿"/"新生物" | 统一规范译法 |
| 英文拼写错误 | "angiotension-converting" | "angiotensin-converting" |
| 缩写大小写错误 | "mg"/"Mg"/"mG"混用 | 统一使用"mg" |
| 单位符号翻译错误 | "10⁹/L"译为"10�9/L" | 保留正确上标格式 |
| 容易混淆缩写 | ACEI与ARB混淆 | 区分缩写含义 |
| 希腊词根误译 | "cardio-"译为"头"而非"心" | cardio- = 心 |
| 拉丁词根误译 | "renal"译为"肝"而非"肾" | renal = 肾，hepatic = 肝 |
| 化验值单位翻译错误 | "pg/ml"译为"纳克/毫升" | pg/ml = 皮克/毫升（ng/ml才是纳克） |
| 数字上标/下标错误 | "10⁹"写成"109" | 保留上标格式 |

## 医学术语翻译规范

### 1. 常用后缀翻译
| 英文后缀 | 中文翻译 | 示例 |
|---------|---------|------|
| -itis | 炎 | hepatitis 肝炎 |
| -oma | 瘤 | carcinoma 癌 |
| -ectomy | 切除术 | appendectomy 阑尾切除术 |
| -scopy | 镜检查 | endoscopy 内镜检查 |

### 2. 缩写处理原则
- 首次出现：写出全称，括号内注明缩写
  - 例：经皮冠状动脉介入治疗（Percutaneous Coronary Intervention，PCI）
- 后续使用：可直接使用缩写
- 常见缩写：可直接使用（DNA、RNA、CT、MRI等）

### 3. 药品名称翻译
- 通用名：翻译并保留英文
  - 例：阿司匹林（Aspirin）
- 商品名：首次出现标注
  - 例：泰诺（Tylenol，对乙酰氨基酚）

### 4. 计量单位翻译
- 使用国际单位制（SI）
- 保留原文单位并标注中文
  - 例：血压 120/80 mmHg
  - 例：体温 37.5℃

## 输出格式

```json
{
  "issues": [
    {
      "category": "问题类别",
      "severity": "critical/major/minor",
      "location": "P{段落编号}",
      "description": "简短问题描述",
      "current": "当前译文",
      "suggested": "建议译文",
      "reason": "修改依据",
      "english_term": "对应英文术语（可选）",
      "issue_type": "缩写翻译错误/英文拼写错误/缩写展开错误/术语不统一（可选）"
    }
  ],
  "terminology_check": {
    "new_terms": ["新发现的术语"],
    "inconsistent_terms": ["不一致的术语"],
    "missing_english": ["应保留英文的术语"],
    "incorrect_abbreviation_expansion": [
      {
        "abbr": "ESR",
        "current_expansion": "exchangeable sodium ratio",
        "correct_expansion": "erythrocyte sedimentation rate",
        "chinese": "红细胞沉降率"
      }
    ]
  }
}
```

注意：
- 所有翻译质量问题（包括原 `bilingual_accuracy_issues` 中的条目）统一放入 `issues` 数组，通过 `category` 或 `issue_type` 字段区分子类型。
- `terminology_check` 作为附加元数据保留，不参与 issues 扁平化。

## 双语术语精确性优先级

### critical（严重）
- **核心术语翻译错误**：如ESR、NT-proBNP等常用缩写翻译错误
- **英文原文拼写错误**：可能导致读者查阅困难
- **单位符号翻译错误**：可能导致临床用药错误

### major（重要）
- **缩写展开不完整或错误**：如ACEI展开为单数形式
- **词根/前缀漏译**：如NT-、hyper-等
- **同一术语多种译法**：影响阅读体验

### minor（轻微）
- **非核心术语的小问题**：不影响理解
- **大小写格式不统一**：但不影响准确性

## 翻译质量评分标准

| 等级 | 描述 | 差错率 |
|-----|------|--------|
| 优秀 | 信达雅兼备，术语准确统一 | < 0.1% |
| 良好 | 基本准确，少量可改进之处 | 0.1-0.5% |
| 合格 | 主要信息准确，有些问题 | 0.5-1% |
| 不合格 | 有明显错误，需重译 | > 1% |

## 工具和资源

1. **医学术语词典**
   - 《英汉医学词典》
   - 《中医药名词词典》
   - MeSH数据库（医学主题词表）

2. **平行文本库**
   - 类似著作的权威译本
   - 医学期刊双语文章
   - 指南共识双语版

3. **专业网站**
   - WHO官网
   - 美国CDC官网
   - Cochrane Library

## 不检查范围

以下检查由其他技能负责，本技能不涉及：
- **术语标准性（NHC规范）**：由 medical_term_proofreading 负责
- **术语跨章节一致性**：由 consistency_proofreading 负责
- **语言语法和标点**：由 language_proofreading 负责
- **参考文献格式**：由 reference_proofreading 负责

## 注意事项

1. 医学翻译准确性关乎患者安全，容错率极低
2. 不确定的内容需加注说明，不能猜测
3. 保留必要的英文原文便于读者对照
4. 注意区分英式英语和美式英语的差异
5. 新兴术语需查阅最新文献
