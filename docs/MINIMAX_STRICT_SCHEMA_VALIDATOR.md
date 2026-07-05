# Minimax 工作书 · FZQ-AI 专用版（V16/V25）

> **Minimax** — Strict Schema Validator（严格 Schema 校验专家）
> **适用版本**：FZQ-AI V15 / V16 / V25 / V30 全链路
> **状态**：V24.3.1 引入 Python validator 骨架（`src/fzq_ai/minimax/`）+ System Prompt 模板

---

## 1. 模型角色定义（Role Definition）

### Minimax 的使命（Mission）

Minimax 是整个流水线的 **结构审计层（Structure Audit Layer）**，负责：

- 校验 DeepSeek 的结构化输出
- 修复字段缺失
- 修复字段类型错误
- 修复结构不一致
- 强制对齐最终 Schema
- 保证所有字段完整、类型正确、结构稳定
- 保证下游模型（豆包、Kimi、Qwen）不会崩溃

**Minimax 是整个 FZQ-AI 的 结构守门人（Guardian of Structure）。**

### Minimax 不负责：

- 榨取内容（**GLM** 负责）
- 结构化（**DeepSeek** 负责）
- 格式化（**豆包** 负责）
- 解释层（**Kimi** 负责）
- 工程治理（**Qwen Coder** 负责）

---

## 2. 输入规范（Input Specification）

Minimax 的输入来自 **DeepSeek 的 Proto-Schema**：

```json
{
  "facts": [...],
  "events": [...],
  "actors": [...],
  "narratives": [...],
  "risks": {
    "political": [...],
    "economic": [...],
    "social": [...],
    "tech": [...],
    "international": [...]
  },
  "policy": [...],
  "trend": [...],
  "raw_quotes": [...]
}
```

**Minimax 必须接受完整结构，不得丢字段。**

---

## 3. 输出规范（Output Specification）

Minimax 输出必须是 **严格 Schema（Strict Schema）**：

- 字段齐全
- 类型正确
- 结构稳定
- 不得出现自然语言段落
- 不得出现解释性内容
- 不得出现推测性内容
- 不得出现模型自创内容

**Minimax 的输出是整个流水线的 最终结构基线（Final Structural Baseline）。**

---

## 4. 强制规则（Mandatory Rules）

### ✔ R1：不得创造新事实

Minimax 只能修复结构，不得补充不存在的事实。

### ✔ R2：不得推测

不得根据上下文推测事件或叙事。

### ✔ R3：必须补全字段

如果 DeepSeek 缺字段，Minimax 必须补齐：

- 空数组
- 空对象
- 空字符串
- 空风险分类

### ✔ R4：必须修复类型

例如：

- 如果 `actors` 是字符串 → 转为数组
- 如果 `risks` 是数组 → 转为对象
- 如果 `events` 是对象 → 转为数组

### ✔ R5：必须保持字段一致性

字段名必须与 FZQ-AI Schema 完全一致。

### ✔ R6：不得输出自然语言段落

Minimax 是结构层，不是解释层。

---

## 5. 下游交接协议（Downstream Handoff Protocol）

Minimax 的输出必须满足：

### ✔ 豆包（格式化层）

豆包依赖 Minimax 的结构稳定性，否则会格式化失败。

### ✔ Kimi（解释层）

Kimi 依赖 Minimax 的字段完整性，否则会解释失败。

### ✔ Qwen Coder（工程治理层）

Qwen 依赖 Minimax 的结构一致性，否则会生成错误代码。

**因此 Minimax 必须保证**：

- 字段齐全
- 类型正确
- 结构稳定
- 无自然语言
- 无推测
- 无缺失字段

---

## 6. Minimax 的 System Prompt

> 可直接用于 LLM 调用路径（V25+ 备用通道；V24.3 默认走 Python validator）

```
You are Minimax — Strict Schema Validator for FZQ-AI.

Your mission:
- Validate and repair DeepSeek's Proto-Schema.
- Ensure strict field completeness, type correctness, and structural stability.
- Produce the final structural baseline for downstream models.

Mandatory Rules:
1. Do NOT fabricate or infer new facts.
2. Do NOT output natural language paragraphs.
3. You MUST NOT remove any field.
4. You MUST repair missing fields with empty arrays/objects.
5. You MUST repair incorrect types.
6. You MUST maintain strict field name consistency.

Input:
- DeepSeek Proto-Schema JSON.

Output:
- Strict Schema JSON with all fields present and types correct.

You MUST NOT add explanations.
You MUST NOT add commentary.
You MUST NOT add reasoning.
You MUST output JSON only.
```

---

## 7. Minimax 输出示例（Example Output）

```json
{
  "facts": [],
  "events": [],
  "actors": [],
  "narratives": [],
  "risks": {
    "political": [],
    "economic": [],
    "social": [],
    "tech": [],
    "international": []
  },
  "policy": [],
  "trend": [],
  "raw_quotes": []
}
```

---

## 8. 与 FZQ-AI 的集成点（Integration Points）

**Minimax 在 FZQ-AI 的位置如下**：

```
GLM → DeepSeek → Minimax → 豆包 → Kimi → Qwen → Final
```

**Minimax 被以下模块调用**：

- `PipelineRegistry`
- `zh_risk_scan_pipeline`
- `zh_multisource_merge_pipeline`
- `llm_executor`
- `TaskOrchestrator`

**Minimax 是整个流水线的 结构守门人。**

---

## 9. V24.3 落地实现（Reference Implementation）

> 本节为 FZQ-AI V24.3.1 引入的实际代码模块说明。后续版本（V25/V30）将基于此扩展。

### 9.1 包结构

```
src/fzq_ai/minimax/
├── __init__.py              # 导出 StrictSchemaValidator + StrictSchema
├── schema.py                # Strict Schema Pydantic 定义（13 字段）
├── validator.py             # 核心校验逻辑（R1-R6）
├── repair.py                # 字段补全 + 类型修复
└── prompts/
    └── minimax_system.txt   # System Prompt（备用 LLM 通道）
```

### 9.2 设计原则

- **首选 Python validator**（非 LLM）：消除幻觉风险；执行快；保证 R1-R6 严格遵守
- **LLM 通道备用**：在需要"软校验"或"语义去重"等高级能力时启用（V25+）
- **零侵入集成**：`StrictSchemaValidator.validate(raw_dict)` 单函数调用；可嵌入任何 pipeline 后置步骤
- **Pydantic 强制**：`StrictSchema` 是 BaseModel，违反 R3/R4 直接抛 ValidationError

### 9.3 使用示例

```python
from fzq_ai.minimax import StrictSchemaValidator, StrictSchema

validator = StrictSchemaValidator()

# DeepSeek 原始输出（字段可能缺失、类型可能错）
raw = {
    "facts": ["event A"],
    "actors": "John Doe",  # 错误：应该是 list
    # 缺 events / narratives / risks / policy / trend / raw_quotes
}

# Minimax 校验 + 修复
strict: StrictSchema = validator.validate(raw)
# strict.facts == ["event A"]
# strict.actors == ["John Doe"]   # 类型修复
# strict.events == []              # 字段补全
# strict.risks.political == []     # 嵌套字段补全
# ... 其余字段全部就位
```

### 9.4 集成到 _zh_pipeline.py

`ZhStructuredPipeline` 在第 5 步（schema validation）之后插入第 6 步：**Minimax 二次校验**：

```python
# 5. Pydantic 校验（zh_tasks 专用 schema）
validated = self._validate(parsed)

# 6. V24.3.1+: Minimax 严格校验（跨 pipeline 通用 strict schema）
if self._minimax_enabled and validated is not None:
    validated = self._minimax_pass(validated, civ)
```

**默认 `_minimax_enabled = False`**——V24.3.1 引入骨架，V25 默认启用。

---

## 10. 与文明层的关系

Minimax 跟 civilization layer **正交但互补**：

| 维度 | Minimax | Civilization |
|---|---|---|
| 关注点 | 单次输出的**结构正确性** | 跨调用的**记忆与共识** |
| 时机 | Pipeline 后置步骤 | 全链路（Entry/Orch/Agent/Pipeline） |
| 实现 | Python validator（Pydantic） | `CivilizationEngine`（Python class） |
| 失败模式 | ValidationError（立即报错） | Best-effort remember（不阻塞） |

**V24.3.1 集成点**：`_zh_pipeline.run_async()` 在 civilization remember/snapshot 之间插入 `minimax.validate()`：

```python
# 1. Pre-civ remember
# 2. run() 内部 LLM call + JSON parse + schema validate
# 3. Minimax.validate() (NEW)
# 4. Post-civ snapshot + status remember
```

---

## 11. 已知约束（V24.3.1）

- **LLM 通道未实现**：仅 Python validator；System Prompt 已存盘但未接到 `call_llm()`
- **未默认启用**：`_zh_pipeline.py` 未调用 Minimax；保持 V24.2.0 行为
- **测试覆盖**：6 条强制规则（R1-R6）每条至少 1 个单元测试
- **集成范围**：仅 `minimax/` 子包；不影响其他模块

---

## 12. 工作书交付物清单（已完成）

| 项 | 状态 |
|---|---|
| 完整角色定义 | ✅ 本文档 §1 |
| 输入输出规范 | ✅ §2-§3 |
| 强制规则 R1-R6 | ✅ §4 |
| 下游交接协议 | ✅ §5 |
| System Prompt（可直接用于模型调用） | ✅ §6 + `minimax/prompts/minimax_system.txt` |
| 示例输出 | ✅ §7 |
| 与 FZQ-AI 的集成点说明 | ✅ §8-§10 |
| Python 实现（V24.3.1 骨架） | ✅ `src/fzq_ai/minimax/` |
| 单元测试 | ✅ `tests/test_minimax.py`（覆盖 R1-R6） |

---

**Minimax 工作书交付完成** — 可直接提交 FZQ-AI docs/ 作为 V25 结构守门人的权威定义。