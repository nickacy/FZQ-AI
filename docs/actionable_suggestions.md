# KIMI 可执行改进建议（Actionable Suggestions）V19.2

> KIMI 输出 — 文档优化与提示词增强专家  
> 基于 Prompt ↔ Schema 一致性检查结果的改进路线图

---

## 一、总体评估

| Pipeline | Prompt-Schema 一致性 | 风险等级 | 主要问题 |
|----------|----------------------|----------|----------|
| zh_policy_brief | 95% | 🟢 低 | 仅 minor 字段约束差异 |
| zh_risk_scan | 80% | 🟡 中 | 顶层 3 个字段未在 Prompt 中要求 |
| zh_opinion_landscape | 45% | 🔴 高 | 字段名大面积不一致（camps→clusters 等） |
| zh_multisource_merge | 70% | 🟡 中 | 新增字段未提及 + 枚举值差异 |

---

## 二、P0 级建议（立即执行，阻塞生产）

### 2.1 zh_opinion_landscape：重写输出格式章节

**问题**：Prompt 中的输出字段名（`camps`, `camp_id`, `share`, `frame_analysis`, `key_nodes`, `heat`）与 Schema 中的字段名（`clusters`, `cluster_id`, `size`, `key_frames`, `influencers`, `heat_trend`）大面积不一致。

**影响**：模型按 Prompt 输出的 JSON 无法通过 Schema 验证，100% 报错。

**建议操作**：

1. 将 Prompt 的输出格式章节完全重写，与 Schema 字段名严格对齐：

```
camps → clusters
camp_id → cluster_id
share → size
core_claim → key_arguments
frame_analysis → key_frames
  frame → frame (不变)
  used_by → description
  effect → evidence_span
key_nodes → influencers
  author → name
  camp → stance
  influence_score → influence_score (不变)
heat → heat_trend
  volume → volume (不变)
  trend → trend (不变)
  peak_date → date (类型变化：单一值→时间序列)
```

2. 在 `heat_trend` 中，`peak_date` 从单一值变为时间序列中的峰值点，需要在 Prompt 中说明：
   - `heat_trend` 是一个数组，每个元素包含 `date`（YYYY-MM-DD）和 `volume`（当天讨论量）
   - 峰值日期由数组中 volume 最大的元素的 date 决定

3. 在 Prompt 中增加 Schema 新增的顶层字段输出要求：
   - `overall_stance`: 全样本立场综合判断
   - `overall_sentiment`: 全样本情绪综合判断
   - `representative_quotes`（顶层）：全局代表性引用

### 2.2 zh_opinion_landscape：统一 stance 和 sentiment 枚举值

**问题**：Prompt 的 `stance` 枚举为 `支持/反对/中立/复杂`，Schema 为 `支持/反对/中性/分裂`。`sentiment` 的 Prompt 为 `正面/负面/中性/混合`，Schema 为 `正面/负面/中性/分化`。

**建议操作**：

统一为以下值（推荐方案 A）：

```
stance:  支持 / 反对 / 中性 / 复杂
sentiment: 正面 / 负面 / 中性 / 混合
```

理由：
- "复杂"比"分裂"更中性，避免暗示阵营内部存在不可调和的裂痕
- "混合"比"分化"更直观，且与 policy_brief 的 `impact` 枚举中的"混合"保持一致
- "中性"与"中立"同义，选"中性"更简洁（单字 vs 双字）

**代码修改**：

```python
# zh_opinion_landscape.py
class ZhOpinionCluster(BaseModel):
    stance: Literal["支持", "反对", "中性", "复杂"] = ...  # 改：分裂→复杂
    sentiment: Literal["正面", "负面", "中性", "混合"] = ...  # 改：分化→混合

class ZhOpinionLandscapeOutput(BaseModel):
    overall_stance: Optional[Literal["支持", "反对", "中性", "复杂"]] = None  # 改
    overall_sentiment: Optional[Literal["正面", "负面", "中性", "混合"]] = None  # 改
```

---

## 三、P1 级建议（本周执行，影响输出质量）

### 3.1 zh_risk_scan：在 Prompt 中增加顶层字段要求

**问题**：Schema 在顶层新增了 `overall_risk_level`, `entity_watchlist`, `suggested_actions`, `confidence`，但 Prompt 的输出格式章节未要求输出这些字段。

**建议操作**：

在 Prompt 的【输出格式】JSON 模板中增加以下字段：

```json
{
  "task_type": "zh_risk_scan",
  "scan_window": "...",
  "overall_risk_level": "<高|中|低|观察，基于risks中最高level和数量综合评估>",
  "entity_watchlist": ["<监控实体1>", "<监控实体2>"],
  "suggested_actions": ["<全局行动建议1>", "<全局行动建议2>"],
  "confidence": "<0.0-1.0，整体扫描置信度>",
  "risks": [...],
  "summary": "..."
}
```

并在【执行规则】中增加：

```
9. overall_risk_level 判定：取 risks 中最高 level，若高/中等级风险 ≥3 条，整体升一级。
10. entity_watchlist 必须原样输出输入中的监控实体列表，无论是否识别到风险。
11. suggested_actions 从所有 risks 的 suggested_action 中提炼全局性建议，至少 1 条。
```

### 3.2 zh_multisource_merge：在 Prompt 中增加新增字段

**问题**：Schema 新增了 `missing_sources`, `conflict_sources`, `evidence_map`, `bias_hint`，Prompt 未要求输出。

**建议操作**：

在 Prompt 的【输出格式】JSON 模板中增加：

```json
{
  "task_type": "zh_multisource_merge",
  "event_id": "...",
  "main_axis": {...},
  "perspective_diffs": [...],
  "source_reliability": [
    {
      "source": "...",
      "score": "...",
      "reason": "...",
      "bias_hint": "<可能的偏向性提示，如'立场偏向政府'、'利益相关方'、'已知商业媒体'>"
    }
  ],
  "consistency_score": "...",
  "missing_sources": ["<明显缺位的视角，如'缺少官方表态'、'缺少第三方数据'>"],
  "conflict_sources": ["<存在明显矛盾的视角，如'A国官方声明 vs B国官方声明'>"],
  "evidence_map": [
    {
      "item_id": "<原始条目ID>",
      "span": "<原文片段，50字以内>",
      "source": "<信源名称>"
    }
  ]
}
```

在【执行规则】中增加：

```
6. missing_sources：扫描所有 sources，若某类关键信源（官方、第三方、独立调查）完全缺失，列出缺位类型。
7. conflict_sources：若 sources 中存在立场已知对立或事实直接矛盾的信源，列出矛盾双方。
8. evidence_map：提取每条 source 中支撑 main_axis 和 perspective_diffs 的核心证据片段，形成全局可溯源列表。
9. bias_hint：基于 source_name 的已知属性和 content 的倾向性分析，给出偏向性提示（可选，不强制）。
```

### 3.3 zh_multisource_merge：同步 dimension 枚举值

**问题**：Prompt 的 `dimension` 包含"其他"，但 Schema 的 `Literal` 不包含"其他"。

**建议操作**：二选一

**方案 A（推荐）**：Schema 增加"其他"

```python
dimension: Literal["归因", "措辞强度", "被引主体", "时间线侧重", "数据口径", "其他"]
```

理由：Prompt 已要求当差异不足 3 个时填充"其他"，Schema 应支持。

**方案 B**：Prompt 移除"其他"，改为用实际差异维度填充

若选择方案 B，需要将 Prompt 的降级处理规则改为：当差异不足 3 个时，直接输出实际差异，不再强制填充第 3 个。

---

## 四、P2 级建议（下周执行，提升体验）

### 4.1 统一时间戳格式

**问题**：4 个 Pipeline 的 Prompt 对时间戳格式要求不统一（有的要求 ISO 8601，有的要求 YYYY-MM-DD）。

**建议操作**：

统一所有时间戳为 `YYYY-MM-DD`（日期级）或 `YYYY-MM-DDTHH:MM:SSZ`（ISO 8601）。推荐在 Prompt 和 Schema 中统一标注：

```python
# 在 Schema 中统一增加格式说明
publish_date: str = Field(..., description="发布日期，YYYY-MM-DD")
timestamp: str = Field(..., description="时间戳，ISO 8601格式：YYYY-MM-DDTHH:MM:SSZ")
```

### 4.2 统一 confidence 字段描述

**问题**：4 个 Pipeline 的 `confidence` 描述各不相同，虽然都在 0-1 范围内，但判定标准不一致。

**建议操作**：

在 `docs/glossary.md` 中定义统一的 confidence 分级标准，并在所有 Prompt 中引用：

```
confidence 统一分级（所有 Pipeline 共用）：
- 0.90–1.00：优  — 文本完整、证据充分、无歧义
- 0.70–0.89：良  — 文本完整但部分细节缺失或存在轻微噪声
- 0.50–0.69：中  — 文本为简讯/摘要，信息不完整但核心要素可提取
- 0.30–0.49：差  — 文本噪声较多或部分不可读，分析可靠性低
- 0.00–0.29：不可用 — 文本与任务无关或严重缺失，无法生成有效分析
```

### 4.3 统一降级处理格式

**问题**：4 个 Pipeline 的降级处理格式各不相同，有的改 summary，有的改字段值，有的改 event_id。

**建议操作**：

定义统一的降级处理模板，在所有 Prompt 中一致使用：

```json
{
  "task_type": "xxx",
  "degraded": true,
  "degrade_reason": "<具体原因：样本不足/噪声过高/来源单一/...>",
  "degrade_severity": "<warning|critical>",
  "confidence": 0.0
}
```

当触发降级时，输出上述结构，并附加部分字段（如果可提取）。

---

## 五、代码修改清单（可直接执行）

### 5.1 zh_opinion_landscape.py 修改

```python
# 修改前
stance: Literal["支持", "反对", "中性", "分裂"] = ...
sentiment: Literal["正面", "负面", "中性", "分化"] = ...
overall_stance: Optional[Literal["支持", "反对", "中性", "分裂"]] = None
overall_sentiment: Optional[Literal["正面", "负面", "中性", "分化"]] = None

# 修改后
stance: Literal["支持", "反对", "中性", "复杂"] = ...
sentiment: Literal["正面", "负面", "中性", "混合"] = ...
overall_stance: Optional[Literal["支持", "反对", "中性", "复杂"]] = None
overall_sentiment: Optional[Literal["正面", "负面", "中性", "混合"]] = None
```

### 5.2 zh_multisource_merge.py 修改

```python
# 修改前
dimension: Literal["归因", "措辞强度", "被引主体", "时间线侧重", "数据口径"] = ...

# 修改后
dimension: Literal["归因", "措辞强度", "被引主体", "时间线侧重", "数据口径", "其他"] = ...
```

### 5.3 zh_risk_scan.py 修改（已在 Schema 中，Prompt 需同步）

Schema 中已有以下字段，Prompt 需增加输出要求：
- `overall_risk_level`
- `entity_watchlist`
- `suggested_actions`
- `confidence`（顶层）

---

## 六、验证清单（修改后必须检查）

| 检查项 | 验证方法 | 通过标准 |
|--------|----------|----------|
| Prompt 字段名与 Schema 一致 | 逐字段对比 | 100% 一致 |
| 枚举值一致 | 对比所有 Literal 字段 | 100% 一致 |
| 降级处理一致 | 检查所有降级条件 | 格式统一、触发条件明确 |
| confidence 分级一致 | 检查所有 Prompt 的 confidence 规则 | 使用统一的 5 档标准 |
| 时间戳格式一致 | 检查所有时间相关字段 | 统一为 YYYY-MM-DD 或 ISO 8601 |
| 无 Schema 未定义字段 | 运行 Schema 验证器 | 100% 通过 |
| 无空字符串字段 | 运行 Schema 验证器 | 100% 通过 |
| 无非法枚举值 | 运行 Schema 验证器 | 100% 通过 |

---

> 文档版本：V19.2  
> 维护者：KIMI（文档优化与提示词增强专家）  
> 最后更新：2024-XX-XX
