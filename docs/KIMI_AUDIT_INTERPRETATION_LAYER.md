# Kimi 解释层审计报告（KIMI 工作书执行）

> **角色**: Kimi — Explanation Layer（解释层）  
> **审计对象**: FZQ-AI V24 Pipeline 解释层现状  
> **审计日期**: 2025-07-03  
> **限制**: 不得 commit，仅输出解释建议

---

## 一、执行摘要

**解释层健康度评分：15 / 100（严重缺失）**

FZQ-AI V24 的 Pipeline 已完整构建至 **Doubao 格式化层**，但 **Kimi 解释层完全缺失**。Pipeline 在 `_zh_pipeline.py` 第 203–211 行执行完 Doubao 格式化后即终止，输出的 `result["doubao_formatted"]` 是未经解释的结构化 JSON，无法直接用于：

- 前端政策简报展示
- 风险总结报告生成
- 叙事分析文本输出
- 趋势洞察解读

---

## 二、输入验证（Input Verification）

### 2.1 上游输入确认 ✅

根据 `_zh_pipeline.py` 第 206 行，`doubao_formatted` 确实存在：

```python
result["doubao_formatted"] = fmt.format(result.get("validated") or result.get("parsed") or {})
```

**输入字段**（来自 `StrictSchema`，`src/fzq_ai/minimax/schema.py`）：

| 字段 | 类型 | 说明 | 映射目标（Kimi 输出） |
|------|------|------|---------------------|
| `facts` | `List[str]` | 事实列表 | `structured_explanation.facts` |
| `events` | `List[str]` | 事件列表 | `structured_explanation.events` |
| `actors` | `List[str]` | 参与者列表 | `structured_explanation.actors` |
| `narratives` | `List[str]` | 叙事列表 | `narrative_analysis` |
| `risks` | `StrictRisks` | 风险分类（5 子类） | `risk_summary` |
| `policy` | `List[str]` | 政策信号 | `policy_brief` |
| `trend` | `List[str]` | 趋势信号 | `trend_insights` |
| `raw_quotes` | `List[str]` | 原文引用 | `quotes_analysis` |

### 2.2 输入完整性确认 ✅

`DoubaoFormatter`（`src/fzq_ai/doubao/formatter.py`）遵守 KIMI 工作书 R1–R6：

- ✅ R1: No inference — 不添加事实
- ✅ R2: No supplementation — 不填充缺失字段
- ✅ R3: No invention — 不创建内容
- ✅ R4: No structural change — 保留字段名和顺序
- ✅ R5: Preserve field order — 输出字段顺序固定
- ✅ R6: Output must be valid JSON — 输出合法 JSON

**结论**：Doubao 输出可直接作为 Kimi 的输入，无需预处理。

---

## 三、解释层现状审计

### 3.1 缺失项清单

| # | 缺失组件 | 影响 | 优先级 |
|---|----------|------|--------|
| 1 | `src/fzq_ai/interpreter/` 目录 | 无解释层入口 | 🔴 P0 |
| 2 | `KimiInterpreter` 类 | 无解释逻辑 | 🔴 P0 |
| 3 | `policy_brief` 生成 | 前端无法展示政策简报 | 🔴 P0 |
| 4 | `risk_summary` 生成 | 风险雷达图无法渲染文本 | 🔴 P0 |
| 5 | `narrative_analysis` 生成 | 叙事分析页面为空 | 🔴 P0 |
| 6 | `trend_insights` 生成 | 趋势洞察无法展示 | 🔴 P0 |
| 7 | `quotes_analysis` 生成 | 引用卡片无内容 | 🟡 P1 |
| 8 | `structured_explanation` 生成 | 结构化解释缺失 | 🟡 P1 |
| 9 | Pipeline 中调用 Kimi 的步骤 | `result["kimi_interpreted"]` 不存在 | 🔴 P0 |
| 10 | System Prompt 文件 | `prompts/system/kimi.txt` 不存在 | 🟡 P1 |

### 3.2 Pipeline 断点分析

当前 Pipeline 执行流（`_zh_pipeline.py`）：

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   GLM       │ ──► │   LLM       │ ──► │  Parse JSON │ ──► │  Validate   │ ──► │  Minimax    │
│ Extract     │     │   Call      │     │             │     │  Pydantic   │     │  Strict     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                                          │
                                                                                          ▼
                                                                                  ┌─────────────┐
                                                                                  │   Doubao    │
                                                                                  │   Format    │
                                                                                  └─────────────┘
                                                                                          │
                                                                                          ▼
                                                                                  ┌─────────────┐
                                                                                  │   ???       │
                                                                                  │ (Kimi 缺失) │
                                                                                  └─────────────┘
```

**Doubao 输出示例**（当前实际产出）：

```json
{
  "facts": ["美国扩大对华芯片出口管制", "中国加速国产替代研发"],
  "events": ["2025年6月 BIS 发布新禁令", "2025年7月 中国半导体投资增长 40%"],
  "actors": ["美国商务部 BIS", "中国工信部", "华为", "中芯国际"],
  "narratives": ["美方：国家安全优先", "中方：技术自主可控"],
  "risks": {
    "political": ["外交摩擦升级", "制裁反制循环"],
    "economic": ["供应链成本上升", "全球芯片短缺"],
    "social": ["就业岗位转移"],
    "tech": ["技术脱钩加速"],
    "international": ["盟友选边压力"]
  },
  "policy": ["美国《芯片与科学法案》延续", "中国大基金三期启动"],
  "trend": ["地缘政治技术化", "供应链区域化"],
  "raw_quotes": [""美方表示：'国家安全不容妥协'"", ""中方回应：'自主创新是唯一出路'""]
}
```

**问题**：前端收到的是以上 JSON，用户看到的是原始字段名和列表，**不是自然语言解释**。

---

## 四、解释质量评估

### 4.1 当前解释质量：0 / 100

原因：解释层完全缺失。Pipeline 输出的 `doubao_formatted` 是结构化 JSON，不是人类可读文本。

### 4.2 期望解释质量目标

| 输出字段 | 输入来源 | 解释目标 | 质量指标 |
|----------|----------|----------|----------|
| `policy_brief` | `facts` + `policy` + `actors` | 政策摘要文本 | 信息完整度 ≥ 90% |
| `risk_summary` | `risks` (5 子类) | 风险分级总结 | 分类覆盖率 100% |
| `narrative_analysis` | `narratives` + `events` | 叙事冲突分析 | 立场识别准确率 ≥ 85% |
| `trend_insights` | `trend` + `events` | 趋势解读 | 时间线逻辑一致性 |
| `quotes_analysis` | `raw_quotes` | 引用来源分析 | 溯源完整性 |
| `structured_explanation` | 全部字段 | 结构化总览 | 字段覆盖率 100% |

---

## 五、可读性风险（10 条）

1. **前端直接展示 JSON**：用户看到 `{"risks": {"political": [...]}}` 而不是"政治风险：外交摩擦升级、制裁反制循环"。

2. **字段名未翻译**：`raw_quotes`、`narratives` 等英文字段名直接暴露给用户。

3. **列表无连接词**：`["摩擦升级", "制裁循环"]` 无"和""以及"等连接词，读起来像机器人。

4. **风险无优先级**：5 类风险平铺，无"高风险""中风险""低风险"分级。

5. **时间线无因果**：`events` 是列表，无"因为...所以...""导致..."等因果连接。

6. **叙事无立场对比**：`narratives` 是两条独立文本，无"美方认为...而中方认为..."的对比结构。

7. **引用无上下文**：`raw_quotes` 是孤立的引号，无"据 XX 报道""XX 在 XX 场合表示"等上下文。

8. **无执行摘要**：用户必须阅读全部 JSON 才能理解核心结论。

9. **无行动建议**：输出止于描述，无"建议关注""需警惕"等 actionable insight。

10. **语言不一致**：` StrictSchema` 字段名为英文，但内容是中文，混合语言降低可读性。

---

## 六、解释优化建议（Kimi → DS 执行书建议）

### 6.1 架构建议（供 DS 执行）

```
建议创建：src/fzq_ai/interpreter/
├── __init__.py
├── kimi_interpreter.py      # KimiInterpreter 类
└── prompts/
    └── system_kimi.txt      # System Prompt
```

### 6.2 Pipeline 集成建议（供 DS 执行）

在 `_zh_pipeline.py` 第 211 行（Doubao 格式化后）添加：

```python
# V24: Kimi 解释层（Explanation Layer）
try:
    from fzq_ai.interpreter.kimi_interpreter import KimiInterpreter
    interpreter = KimiInterpreter()
    result["kimi_interpreted"] = interpreter.interpret(result["doubao_formatted"])
except Exception:
    _logger.warning("Kimi interpretation skipped", exc_info=True)
```

### 6.3 System Prompt 建议（供 DS 执行）

```
You are Kimi — Explanation Expert for FZQ-AI.
Your mission is to interpret StrictSchema without altering facts or structure.
Input: StrictSchema JSON (facts, events, actors, narratives, risks, policy, trend, raw_quotes)
Output: JSON only, with fields: policy_brief, risk_summary, narrative_analysis, trend_insights, quotes_analysis, structured_explanation
Rules:
- R1: 不得改变输入结构
- R2: 不得补充事实
- R3: 不得发明事件
- R4: 不得修改字段值
- R5: 解释必须基于 StrictSchema
- R6: 输出必须是合法 JSON
```

### 6.4 输出 Schema 建议（供 DS 执行）

```python
class KimiInterpretedOutput(BaseModel):
    policy_brief: str          # 政策简报（自然语言段落）
    risk_summary: str          # 风险总结（分级+描述）
    narrative_analysis: str    # 叙事分析（立场对比）
    trend_insights: str        # 趋势洞察（因果链）
    quotes_analysis: str       # 引用分析（溯源+上下文）
    structured_explanation: Dict[str, Any]  # 结构化总览
```

---

## 七、最终结论（一句话）

> **FZQ-AI V24 的 Pipeline 已完成至 Doubao 格式化层，但 Kimi 解释层完全缺失，导致前端只能展示原始 JSON 而非人类可读的分析文本；建议在 `_zh_pipeline.py` 第 211 行后插入 `KimiInterpreter.interpret()` 调用，并创建 `src/fzq_ai/interpreter/` 目录实现解释层。**

---

*审计完成 — Kimi（解释层）*  
*不执行代码修改，仅输出解释建议*  
*建议由 Copilot 转换为 DS 执行书后实施*
