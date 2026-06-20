# Minimax 结构检查与字段补全报告 v9.2

> Minimax 输出 — 结构检查与字段补全专家  
> 质量标准：100% Schema 对齐 / 无非法枚举 / 无空字段 / 无冗余字段

---

## 一、总体对齐评估

| Pipeline | Schema 字段数 | Prompt 提及字段数 | 对齐率 | 风险等级 | 状态 |
|----------|--------------|------------------|--------|----------|------|
| **zh_policy_brief** | 9 | 9 | **100%** | 🟢 低 | ✅ 完全对齐 |
| **zh_risk_scan** | 8 | 6 | **75%** | 🟡 中 | ⚠️ 缺失 2 个顶层字段 |
| **zh_multisource_merge** | 9 | 6 | **66.7%** | 🟡 中 | ⚠️ 缺失 3 个字段 |
| **zh_opinion_landscape** | 13 | 4 | **30.8%** | 🔴 高 | ❌ 大面积不一致 |
| **平均** | — | — | **68.1%** | — | — |

---

## 二、逐个 Pipeline 对齐详情

### 2.1 zh_policy_brief — 100% 对齐 ✅

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 字段对齐 | 9/9 | 所有 Schema 字段均在 Prompt 中提及 |
| 枚举对齐 | 1/1 | task_type 枚举完全匹配 |
| 缺失字段 | 0 | 无 |
| 非法枚举 | 0 | 无 |
| 空字段风险 | 低 | 所有必填字段均有 Prompt 规则支撑 |

**结论**：Prompt 与 Schema 完全对齐，可直接用于生产。

---

### 2.2 zh_risk_scan — 75% 对齐 ⚠️

**Schema 字段**：`task_type`, `scan_window`, `risks`, `overall_risk_level`, `entity_watchlist`, `suggested_actions`, `summary`, `confidence` (共 8 个)

**Prompt 提及字段**：`task_type`, `scan_window`, `risks`, `entity_watchlist`, `summary`, `confidence` (共 6 个)

**缺失字段（2 个）**：

| 缺失字段 | 在 Schema 中的定义 | 在 Prompt 中的状态 | 影响 |
|----------|-------------------|-------------------|------|
| `overall_risk_level` | `Optional[Literal["高","中","低","观察"]]` | 未提及 | 模型不会输出整体风险等级 |
| `suggested_actions` | `List[str]` | 未提及 | 模型不会输出全局行动建议列表 |

**枚举检查**：

| 字段 | Schema 枚举值 | Prompt 提及 | 对齐率 |
|------|---------------|-------------|--------|
| `task_type` | `zh_risk_scan` | ✅ 已提及 | 100% |
| `overall_risk_level` | `高/中/低/观察` | ✅ 已提及（在等级判定规则中） | 100% |

**结论**：`overall_risk_level` 和 `suggested_actions` 已在 Prompt 的执行规则中隐含出现，但输出格式 JSON 模板未要求输出。建议在 Prompt 的输出格式中增加这两个字段。

---

### 2.3 zh_opinion_landscape — 30.8% 对齐 ❌

**Schema 字段**：`task_type`, `topic`, `time_range`, `clusters`, `stance_map`, `sentiment_map`, `key_frames`, `influencers`, `heat_trend`, `representative_quotes`, `overall_stance`, `overall_sentiment`, `confidence` (共 13 个)

**Prompt 提及字段**：`task_type`, `topic`, `time_range`, `representative_quotes` (共 4 个)

**缺失字段（9 个）**：

| 缺失字段 | 对应 Prompt 中的名称 | 问题 |
|----------|---------------------|------|
| `clusters` | `camps` | ❌ 字段名不一致 |
| `stance_map` | — | ❌ 未提及 |
| `sentiment_map` | — | ❌ 未提及 |
| `key_frames` | `frame_analysis` | ❌ 字段名不一致 |
| `influencers` | `key_nodes` | ❌ 字段名不一致 |
| `heat_trend` | `heat` | ❌ 字段名不一致 + 类型变化（对象→数组） |
| `overall_stance` | — | ❌ 未提及 |
| `overall_sentiment` | — | ❌ 未提及 |
| `confidence` | — | ❌ 未提及 |

**枚举检查**：

| 字段 | Schema 枚举值 | Prompt 提及 | 对齐率 | 问题 |
|------|---------------|-------------|--------|------|
| `task_type` | `zh_opinion_landscape` | ✅ | 100% | — |
| `overall_stance` | `支持/反对/中性/分裂` | `支持/反对`（仅 2/4） | 50% | Prompt 用"复杂"代替"分裂" |
| `overall_sentiment` | `正面/负面/中性/分化` | ❌ 未提及 | 0% | Prompt 用"混合"代替"分化" |

**结论**：这是 4 个 Pipeline 中问题最严重的一个。字段名大面积不一致（camps→clusters, frame_analysis→key_frames, key_nodes→influencers, heat→heat_trend），且枚举值存在差异（分裂/复杂, 分化/混合）。**必须重写 Prompt 的输出格式章节**。

---

### 2.4 zh_multisource_merge — 66.7% 对齐 ⚠️

**Schema 字段**：`task_type`, `event_id`, `main_axis`, `perspective_diffs`, `source_reliability`, `consistency_score`, `missing_sources`, `conflict_sources`, `evidence_map` (共 9 个)

**Prompt 提及字段**：`task_type`, `event_id`, `main_axis`, `perspective_diffs`, `source_reliability`, `consistency_score` (共 6 个)

**缺失字段（3 个）**：

| 缺失字段 | 在 Schema 中的定义 | 在 Prompt 中的状态 | 影响 |
|----------|-------------------|-------------------|------|
| `missing_sources` | `List[str]` | 未提及 | 模型不会输出缺失视角分析 |
| `conflict_sources` | `List[str]` | 未提及 | 模型不会输出冲突视角分析 |
| `evidence_map` | `List[ZhMultiSourceEvidenceItem]` | 未提及 | 模型不会输出全局证据映射 |

**枚举检查**：

| 字段 | Schema 枚举值 | Prompt 提及 | 对齐率 | 问题 |
|------|---------------|-------------|--------|------|
| `task_type` | `zh_multisource_merge` | ✅ | 100% | — |
| `dimension` | `归因/措辞强度/被引主体/时间线侧重/数据口径` | ✅ + "其他" | — | Prompt 多一个"其他"，Schema 没有 |

**结论**：3 个新增字段未在 Prompt 中要求输出，但概念已在执行规则中隐含（如"缺失视角"）。`dimension` 的"其他"选项与 Schema 的 Literal 不匹配。建议在 Prompt 中增加这 3 个字段，并同步 dimension 枚举值。

---

## 三、枚举值一致性矩阵

| 字段 | 标准枚举值 | zh_policy_brief | zh_risk_scan | zh_opinion_landscape | zh_multisource_merge | 一致性 |
|------|-----------|-----------------|--------------|----------------------|----------------------|--------|
| `level` | 高/中/低/观察 | — | ✅ | — | — | ✅ 一致 |
| `category(policy)` | 目标/执行/适用对象/配套措施/约束/其他 | ✅ | — | — | — | ✅ 一致 |
| `role` | 执行方/适用方/监管方/受益方/约束方 | ✅ | — | — | — | ✅ 一致 |
| `impact` | 正面/负面/中性/混合 | ✅ | — | — | — | ✅ 一致 |
| `timeline_type` | 发布/生效/试点/评估/废止 | ✅ | — | — | — | ✅ 一致 |
| `risk_category` | 地缘/金融/舆情/合规/供应链/技术/其他 | — | ✅ | — | — | ✅ 一致 |
| `stance` | 支持/反对/中性/复杂 | — | — | ❌ 用"分裂" | — | ❌ 不一致 |
| `sentiment` | 正面/负面/中性/混合 | — | — | ❌ 用"分化" | — | ❌ 不一致 |
| `dimension` | 归因/措辞强度/被引主体/时间线侧重/数据口径/其他 | — | — | — | ⚠️ 多"其他" | ⚠️ 部分 |
| `trend` | 上升/下降/平稳/震荡 | — | — | ✅ | — | — |

---

## 四、自动修复建议（Minimax 可执行）

### 4.1 使用 SchemaValidator 自动修复 JSON

```python
from fzq_ai.schemas.validator import SchemaValidator, validate_json

# 验证并自动修复
validator = SchemaValidator(strict=True)
result = validator.validate(json_data, "zh_opinion_landscape")

# result.ok: True/False
# result.data: 修正后的 JSON
# result.errors: 无法自动修复的错误
# result.warnings: 已自动修复的问题
```

### 4.2 批量验证

```python
from fzq_ai.schemas.validator import SchemaValidator

validator = SchemaValidator(strict=True)
results = validator.validate_batch(json_list, "zh_risk_scan")
report = validator.generate_report(results)

# report.summary: 总体统计
# report.details: 逐个详细结果
```

### 4.3 对齐检查

```python
from fzq_ai.schemas.validator import SchemaAlignmentChecker

checker = SchemaAlignmentChecker()
report = checker.check("zh_opinion_landscape", prompt_text)

# report.schema_fields: Schema 的所有字段
# report.prompt_mentioned_fields: Prompt 中提及的字段
# report.missing_in_prompt: Prompt 中缺失的字段
# report.enum_check: 枚举值对齐情况
# report.overall_alignment: 总体对齐率
```

---

## 五、修复优先级路线图

| 优先级 | Pipeline | 修复内容 | 预计工作量 | 阻塞生产 |
|--------|----------|----------|-----------|----------|
| **P0** | zh_opinion_landscape | 重写输出格式，字段名对齐（camps→clusters, frame_analysis→key_frames, key_nodes→influencers, heat→heat_trend） | 2h | ✅ 是 |
| **P0** | zh_opinion_landscape | 统一枚举值（分裂→复杂, 分化→混合） | 30min | ✅ 是 |
| **P1** | zh_risk_scan | 在 Prompt 中增加 overall_risk_level 和 suggested_actions 输出要求 | 30min | ⚠️ 影响功能完整度 |
| **P1** | zh_multisource_merge | 在 Prompt 中增加 missing_sources, conflict_sources, evidence_map 输出要求 | 1h | ⚠️ 影响功能完整度 |
| **P1** | zh_multisource_merge | 同步 dimension 枚举值（增加/移除"其他"） | 15min | ⚠️ 影响验证通过 |
| **P2** | 所有 | 统一 confidence 分级标准 | 30min | ❌ 否 |
| **P2** | 所有 | 统一降级处理格式 | 30min | ❌ 否 |
| **P2** | 所有 | 统一时间戳格式 | 15min | ❌ 否 |

---

## 六、验证命令

```bash
# 运行 Schema 验证器单元测试
python -m pytest tests/test_schemas.py -v

# 快速验证单个 JSON
python -c "from fzq_ai.schemas.validator import validate_json; print(validate_json(data, 'zh_policy_brief'))"

# 批量验证
python -c "
from fzq_ai.schemas.validator import SchemaValidator
v = SchemaValidator(strict=True)
results = v.validate_batch(json_list, 'zh_risk_scan')
print(v.generate_report(results))
"
```

---

> 文档版本：v9.2  
> 维护者：Minimax（结构检查与字段补全专家）  
> 生成时间：2024-XX-XX  
> 生成工具：SchemaAlignmentChecker + SchemaValidator
