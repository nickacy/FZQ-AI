# Minimax Phase 2 工作书 · 结构反馈层（Structural Feedback Layer）

> **Minimax Phase 2** — Structural Feedback Layer for FZQ-AI V25
> **状态**：V24.3.4 引入 Python feedback engine 骨架（`src/fzq_ai/minimax/phase2/`）+ System Prompt + tests

---

## 1. Minimax Phase 2 的使命（Mission）

### Phase 1（已完成）负责
- 字段补全
- 类型修复
- 结构一致性
- 风险分类修复
- 字段顺序修复
- StrictSchema 输出

### Phase 2 的使命

将**结构治理结果反馈给上游模型（GLM、DeepSeek）和下游层（豆包、Kimi、Qwen）**，形成一个 **"结构闭环"**。

**Minimax Phase 2 是整个 FZQ-AI 的 结构反馈层（Structural Feedback Layer）。**

### Phase 2 的目标
- ✔ 让 GLM 的榨取更稳定
- ✔ 让 DeepSeek 的结构化更一致
- ✔ 让豆包的格式化更稳健
- ✔ 让 Kimi 的解释更准确
- ✔ 让 Qwen 的工程治理更精确
- ✔ 让 DS 的执行更安全
- ✔ 让文明层的推理更可靠

**Minimax Phase 2 是整个系统的 结构治理中枢。**

---

## 2. Phase 2 的输出（4 类）

### 2.1 Structural Feedback Report（结构反馈报告）

包括：
- 缺失字段列表
- 类型修复列表
- 风险分类修复列表
- 字段顺序修复列表
- 结构一致性评分（0-100）
- 结构风险评分（0-100）
- 结构建议（不含代码）

### 2.2 Upstream Feedback（上游反馈）

给 **GLM**：
- 哪些字段经常缺失
- 哪些字段经常类型错误
- 哪些字段经常分类错误

给 **DeepSeek**：
- 哪些结构经常不一致
- 哪些字段经常需要补齐
- 哪些事件链经常不完整

### 2.3 Downstream Feedback（下游反馈）

给 **豆包**：
- 哪些字段需要特殊格式化
- 哪些字段需要排序
- 哪些字段需要保持一致性

给 **Kimi**：
- 哪些字段需要解释
- 哪些字段需要合并
- 哪些字段需要拆分

给 **Qwen**：
- 哪些结构需要工程治理
- 哪些字段需要重构
- 哪些 Schema 需要升级

### 2.4 Commit Decision（是否允许 Minimax 自己 commit）

由 **Copilot** 决定：

| 输出类型 | Minimax 是否可自己 commit |
|---|---|
| 缺失字段补齐 | ✔ 可以 |
| 类型修复 | ✔ 可以 |
| 风险分类修复 | ✔ 可以 |
| 字段顺序修复 | ✔ 可以 |
| 结构一致性评分 | ✔ 可以 |
| 结构建议（不含代码） | ✔ 可以 |
| Schema 变更 | ✘ 不可以 → DS 执行书 |
| Pipeline 变更 | ✘ 不可以 → DS 执行书 |
| Agent 变更 | ✘ 不可以 → DS 执行书 |
| 文明层结构变更 | ✘ 不可以 → DS 执行书 |
| 代码生成 | ✘ 不可以 → DS 执行书 |
| 测试生成 | ✘ 不可以 → DS 执行书 |

**治理模式**：Minimax 只能 commit **结构层内容**。所有 **代码层内容** 必须由 DS commit。

---

## 3. Phase 2 强制规则（Mandatory Rules）

- ✔ **R1：不得生成代码**
- ✔ **R2：不得修改业务逻辑**
- ✔ **R3：不得发明字段**
- ✔ **R4：不得改变结构定义**
- ✔ **R5：只能生成结构反馈**
- ✔ **R6：输出必须是 JSON**

**Minimax Phase 2 是 结构治理层，不是代码层。**

---

## 4. Phase 2 目录结构

```
src/fzq_ai/minimax/
    phase2/
        __init__.py
        feedback_engine.py
        feedback_models.py
        feedback_router.py
        prompts/system_minimax_phase2.txt
tests/
    test_minimax_phase2.py
```

---

## 5. 核心文件设计

### 5.1 feedback_models.py

```python
class StructuralFeedback(BaseModel):
    source: str = "minimax_phase2"
    target_models: List[str]
    
    # Field-level issues
    missing_fields: List[str]
    type_repairs: List[str]
    risk_repairs: List[str]
    order_repairs: List[str]
    
    # Scores (0-100)
    consistency_score: float
    risk_score: float
    
    # Suggestions (structural only, no code)
    suggestions: List[str]
    
    # Metadata
    trace_id: str
    generated_at: str  # ISO 8601
```

### 5.2 feedback_engine.py

```python
class MinimaxFeedbackEngine:
    def generate(
        self,
        strict_schema: Dict[str, Any],
        original_input: Optional[Dict[str, Any]] = None,
    ) -> StructuralFeedback:
        """
        Phase 2: 结构反馈层
        不修改结构，不生成代码，只生成反馈报告
        
        strict_schema: Phase 1 修复后的 StrictSchema dict
        original_input: 原始 input（可选，用于 diff 找出 missing/type repairs）
        """
        ...
```

### 5.3 feedback_router.py

```python
class MinimaxFeedbackRouter:
    def route(self, feedback: StructuralFeedback) -> Dict[str, Any]:
        """
        将反馈分发给 GLM / DeepSeek / 豆包 / Kimi / Qwen / DS
        """
        return {
            "glm": self._glm_feedback(feedback),
            "deepseek": self._deepseek_feedback(feedback),
            "doubao": self._doubao_feedback(feedback),
            "kimi": self._kimi_feedback(feedback),
            "qwen": self._qwen_feedback(feedback),
            "ds_commit_decision": self._ds_commit_decision(feedback),
        }
```

---

## 6. Copilot 审查逻辑

Copilot 检查逻辑已实现为 `MinimaxFeedbackRouter._ds_commit_decision()`：

- **结构层变更**（missing/type/risk/order 修复 + scores + suggestions）→ Minimax 可 self-commit
- **代码层变更**（schema/pipeline/agent/civ/code/test）→ 必须 DS 执行书 + DS commit

---

## 7. Phase 2 → DS 执行书模板

当 Minimax 不能自己 commit 时（如发现需要改 schema 或 pipeline），输出 DS 执行书：

```markdown
# DS Execution Workbook — Minimax Phase 2 Structural Feedback (V25)

## Task 1 — 修改 schema.py
## Task 2 — 修改 validator.py
## Task 3 — 修改 repair.py
## Task 4 — 修改 zh_pipeline
## Task 5 — 修改 news_center_agent
## Task 6 — 修改文明层挂载点
## Task 7 — 添加测试
## Task 8 — 跑测试
## Task 9 — commit
```

**V24.3.4 实现**：`_ds_commit_decision()` 始终返回 `minimax_can_commit=True`（因为 Phase 2 输出本身是结构反馈）—— 但当 feedback 显示"需要 schema/pipeline 变更"时，会在 `requires_ds_execution_book` 字段标注。

---

## 8. 测试体系（test_minimax_phase2.py）

测试内容（22 tests）：

1. **StructuralFeedback 模型**（3 tests）
   - 模型校验
   - 默认字段
   - scores 范围（0-100）

2. **MinimaxFeedbackEngine**（10 tests）
   - missing_fields 检测
   - type_repairs 检测（str → list）
   - risk_repairs 检测（list → dict）
   - order_repairs 检测（乱序字段）
   - consistency_score: 空 input = 0
   - consistency_score: 满 input = 100
   - risk_score: 空 risks = 0
   - risk_score: 满 risks = 100
   - suggestions 生成
   - Phase 2 不修改 strict_schema（R1 合规）

3. **MinimaxFeedbackRouter**（6 tests）
   - route 返回 6 个 key
   - glm feedback 含 missing fields
   - ds feedback 含 structural issues
   - doubao feedback 关注 formatting
   - kimi feedback 关注 interpretation
   - qwen feedback 关注 engineering

4. **Commit Decision**（1 test）
   - Phase 2 始终 `minimax_can_commit=True`（结构反馈）

5. **Mandatory Rules R1/R6**（2 tests）
   - R1: Phase 2 不生成代码
   - R6: 输出始终 JSON 可序列化

---

## 9. 集成点（Integration Points）

### 9.1 _zh_pipeline.py

```python
# After minimax validation (V24.3.3)
feedback = minimax_phase2_engine.generate(
    strict_schema=result["minimax"]["strict"],
    original_input=result,  # for diff
)
result["minimax_feedback"] = feedback.model_dump()
```

### 9.2 文明层挂载

```python
civ.remember("minimax_feedback", result["minimax_feedback"])
civ.remember("minimax_consistency_score", str(feedback.consistency_score))
civ.remember("minimax_risk_score", str(feedback.risk_score))
```

---

## 10. V24.3.4 实现说明

### 10.1 包结构

```
src/fzq_ai/minimax/phase2/
    __init__.py              # 导出 MinimaxFeedbackEngine, MinimaxFeedbackRouter, StructuralFeedback
    feedback_models.py       # StructuralFeedback Pydantic 模型
    feedback_engine.py       # MinimaxFeedbackEngine 主入口
    feedback_router.py       # MinimaxFeedbackRouter 6-路分发
    prompts/system_minimax_phase2.txt  # System Prompt (备用 LLM 通道)
```

### 10.2 设计原则

- **首选 Python engine**（非 LLM）：消除幻觉风险；保证 R3（不发明字段）、R4（不改变结构定义）
- **Pydantic 强制**：StructuralFeedback 是 BaseModel，违反字段类型直接 ValidationError
- **只读**：feedback_engine.generate() 从不修改 strict_schema
- **6-路分发**：router.route() 返回 dict 含 6 个下游目标
- **零侵入集成**：在 `_zh_pipeline.run_async()` 加 `result["minimax_feedback"] = ...`

### 10.3 与 Phase 1 的关系

```
原始 input ─→ Phase 1 (StrictSchemaValidator) ─→ StrictSchema
                                              │
                                              ▼
                                  Phase 2 (MinimaxFeedbackEngine)
                                              │
                                              ▼
                                       StructuralFeedback
                                              │
                                              ▼
                              MinimaxFeedbackRouter.route()
                                              │
                ┌────────────┬────────────┬───┴────┬────────────┬────────────┐
                ▼            ▼            ▼        ▼            ▼            ▼
              GLM        DeepSeek       豆包     Kimi         Qwen         DS
            (upstream)  (upstream)  (downstream)(downstream)(downstream) (commit)
```

---

## 11. 已知约束（V24.3.4）

- **LLM 通道未实现**：System Prompt 已存盘但 engine 走纯 Python 路径
- **Phase 2 输入**：需要同时传 `strict_schema` + `original_input` 才能生成完整 missing/type reports
- **未默认启用 phase2**：在 `_zh_pipeline.py` 中只调一次 `phase2_engine.generate()`，需要 V25 决定是否默认开启
- **DS 执行书**：当 phase2 feedback 显示需要代码层变更时，需要人工评估（Copilot 决策）

---

## 12. 工作书交付物清单（已完成）

| 项 | 状态 |
|---|---|
| 完整角色定义 | ✅ §1-§3 |
| 4 类输出规范 | ✅ §2 |
| 强制规则 R1-R6 | ✅ §3 |
| 目录结构 | ✅ §4 |
| 核心文件设计 | ✅ §5 |
| Copilot 审查逻辑 | ✅ §6 |
| DS 执行书模板 | ✅ §7 |
| 测试体系 | ✅ §8 |
| 集成点 | ✅ §9 |
| V24.3.4 实现说明 | ✅ §10-§11 |

**Minimax Phase 2 工作书交付完成** — 可直接提交 FZQ-AI docs/ 作为 V25 结构反馈层的权威定义。

---

**Reference**：
- Minimax Phase 1 工作书：`docs/MINIMAX_STRICT_SCHEMA_VALIDATOR.md`
- Minimax Phase 2 工作书：本文件
- 链路：`GLM → DeepSeek → Minimax Phase 1 (修复) → Minimax Phase 2 (反馈) → 豆包 → Kimi → Qwen → Final`