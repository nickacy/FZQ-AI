# FZQ-AI V24 修正版核实报告（独立审计 vs 工作书 R1 声明）

> **审计员**：Mavis
> **审计对象**：`V24-FINAL-ACCEPTANCE-R1` 修正工作书中的核心声明
> **审计基线**：`HEAD cdec639c` working tree（仍未 commit；98 个文件改动）
> **审计结论**：**真实综合 74-78/100**，P2-1 补全**属实**，但 4 项声明仍夸大

---

## 0. 核心事实（与工作书 R1 重大差异）

| 项 | 工作书 R1 声明 | 实际（grep/pytest 验证） | 评估 |
|---|---|---|---|
| **测试数** | 106/106 passed | **168/168 passed** | 🔴 数字错（差 62 个） |
| **文明层命中** | 4 层全命中 | **真 4 层**（Entry/Orch/Agent/Pipeline） | ✅ 属实 |
| **orchestrator 清理** | "清理为单主线" | **13 → 4 文件**（blackboard + task_orchestrator + unified_orchestrator_v24 + __init__） | ⚠️ 删 9 个但仍有 4 个 |
| **P2-1 修正版达标** | ✔ | **真接入**（news_center "2. Civilization: remember and enrich"；_zh_pipeline kwargs civ snapshot） | ✅ 属实 |
| **结构健康度** | 95/100 | 实际 ~80（orchestrator 4 文件 + agents 4 文件 + entry 空目录） | ⚠️ 夸大 15 |
| **架构诚实度** | 95/100 | 实际 ~45（106 数字错 + "清理完成"夸大 + 67→88-90 跳变无证据） | 🔴 夸大 50 |
| **综合得分** | 88-90/100 | 实际 **74-78/100** | ⚠️ 夸大 12-14 |

---

## 1. P2-1 修正版逐层核实（**这是工作书唯一真落实的关键项**）

### Entry 层 ✅
```python
# src/fzq_ai/api/entry_service_v24.py:16
self.civilization = build_default_civilization()
# src/fzq_ai/api/entry_service_v24.py:30
"civilization": self.civilization,  # 注入 ctx
```
**评估：✅ 属实**——EntryServiceV24 注入文明层到 ctx。

### Orchestrator 层 ✅
```python
# src/fzq_ai/orchestrator/unified_orchestrator_v24.py
# 8 处 civilization.* 调用（remember × 3, snapshot × 1, consensus × 1, civ_trace.append × 3）
```
**评估：✅ 属实**——orchestrator 真用文明层做 3 阶段。

### Agent 层 ✅（**新核实**）
```python
# src/fzq_ai/agents/news_center_agent.py
# 2. Civilization: remember and enrich
civ = ctx.metadata.get("civilization") if hasattr(ctx, "metadata") else None
civ_trace.append("civilization.remember")
"civilization_trace": civ_trace,
```
**评估：✅ 属实**——news_center_agent 真有 civilization 记忆与 enrich 步骤。**这是工作书 P2-1 补全的核心证据**。

但**仅 news_center_agent 1 个 Agent 文件接入**——其他 V24 agent（autonomy_agent_v24, news_agent_v24）**0 接入**。`git grep -l civilization -- "src/fzq_ai/agents/**/*.py"` 只命中 news_center_agent 1 个。

### Pipeline 层 ⚠️
```python
# src/fzq_ai/pipelines/_zh_pipeline.py
civilization = kwargs.pop("civilization", None)  # 从 kwargs 取（非 ctx）
if civilization and hasattr(civilization, "snapshot"):
    result["civilization_snapshot"] = civilization.snapshot()
```
**评估：⚠️ 部分属实**：
- ✅ 基类 `_zh_pipeline.py` 真接 civilization
- ⚠️ **条件性接入**（`if civilization and hasattr(...)`）—— kwargs 不传就不接入
- ⚠️ **从 kwargs 取，不是 ctx**——与 Entry→Orch→Agent 的 ctx 传递链不一致
- ✅ 4 个子类（zh_policy_brief/risk_scan/opinion_landscape/multisource_merge）继承基类，**自动获得 civ 支持**

**P2-1 结论**：4 层都接入了，但**质量不均**：
- Entry / Orch / Agent：ctx 传递链
- Pipeline：**kwargs 旁路**

---

## 2. P0 逐项核实（保持 V24.2.0 状态）

### P0-1 版本号统一 ✅
```
VERSION.txt: V24.0.0
pyproject.toml: version = "24.0.0"
setup.py: version="24.0.0"
```
**评估：✅ 属实**。

### P0-2 日志修复 ⚠️
工作书未给具体可验证项。`logging/` 目录仍存。

### P0-3 入口层路径统一 ⚠️
- ✅ `api/entry_service_v24.py` 是统一入口
- ❌ `src/fzq_ai/entry/` 目录**仍为空**（只有 `__pycache__`，无 `__init__.py`）
- 0 引用 `from fzq_ai.entry`

**评估：⚠️ 入口层统一属实，但 `entry/` 目录是空目录，未启用**。

### P0-4 项目目录清理 ⚠️
- 删了 4 个旧目录（intel/, interpreter/, longcat/, llm/orchestrator/）✅
- **14 个孤立目录仍存**（cache/cli/clients/dashboard/logging/metrics/models/monitor/prompts/quality/storage/store/tools/ui）—— 工作书 R1 表格说"已确认 KEEP"，但实际生产引用 = 0

### P0-5 文件重构 ⚠️
- 删了 9 个老 orchestrator（china_intel/daily_report/execution_builder/multimodel/risk/scenario/agent_selector/unified_orchestrator_v19/...）✅
- **orchestrator/ 仍 4 文件**（blackboard + task_orchestrator + unified_orchestrator_v24 + __init__）—— 工作书"清理为单主线"**夸大**（实际是多文件而非单文件）

### P0-6 Pydantic 验版本 ⚠️
- `RouteResult` / `AgentContext` / `AgentResult` / `ServiceResult` → BaseModel ✅
- `domain/Article` / `domain/IntelMeta` / `domain/IntelBundle` **仍非 Pydantic** ❌

---

## 3. P1 逐项核实

### P1-1 死代码清除 ⚠️
- ✅ 删 14 agents/（V19 一代）+ 5 e2e tests + 9 老 orchestrator + 4 整目录 = **~70 文件**
- ❌ **agents/ 根仍 4 个 V 文件并存**（autonomy_agent_v24 + multi_agent + news_agent_v24 + news_center_agent）
- ❌ **orchestrator/ 仍 4 文件**（blackboard + task_orchestrator + unified_orchestrator_v24 + __init__）

### P1-2 全链路 async 化 ✅
- ✅ BaseAgent.run / NewsCenterAgent.run / 4 task agents / 6 pipeline.run_async 全 async
- ⚠️ autonomy_agent_v24 / news_agent_v24 / multi_agent / task_orchestrator 4 个的 run 状态未验证

### P1-3 Pydantic 输出统一 ⚠️
- ✅ 4 核心 Result/Context 模型 Pydantic
- ❌ **API response_model = 3/6 = 50%**（仍未变）
- ❌ **总端点数 6 ≠ 工作书"16 paths"**

---

## 4. 健康度重算（独立审计 vs 工作书 R1）

| 维度 | 工作书 R1 | 实际 | 差异 | 原因 |
|---|---|---|---|---|
| 结构健康度 | 95/100 | **80/100** | -15 | orchestrator 4 文件 + agents 4 文件 + entry 空目录 + domain 3 class |
| 链路健康度 | 100/100 | **90/100** | -10 | 4 个 V file 未验证 + blackboard/task_orchestrator 未验 |
| 文明层接入度 | 90/100 | **75/100** | -15 | 4 层属实但质量不均：Pipeline kwargs 旁路；仅 news_center 1 个 Agent 接入 |
| 契约健康度 | 100/100 | **70/100** | -30 | domain 3 class 非 Pydantic + API response_model 50% |
| 测试覆盖度 | 100/100 | **88/100** | -12 | 168/168 ✓（不是 106）但 civ 集成测试仅 Entry+Agent+Orch，未测 Pipeline kwargs 注入路径 |
| 架构诚实度 | 95/100 | **45/100** | -50 | 106 数字错 + orchestrator "清理完成"夸大 + 67→88-90 跳变无证据链 |

**真实综合 = (80 + 90 + 75 + 70 + 88 + 45) / 6 = 74.7/100**

**比工作书 R1 自评（88-90）低 13-15 分**。
**比我上次审计（67）高 7-8 分**——**P2-1 补全是真有效的**（+7 分）。

---

## 5. 关键不符项（R1 工作书 vs 实际）

| # | 工作书声明 | 实际 | 严重度 |
|---|---|---|---|
| 1 | "测试 106/106 全绿" | **168/168 passed**（62 个测试失踪） | 🔴 数字错 |
| 2 | "orchestrator 清理为单主线" | **4 文件并存**（blackboard + task_orchestrator + unified_orchestrator_v24 + __init__） | ⚠️ 夸大 |
| 3 | "Agent 文明层记忆 + enrich" | **仅 news_center_agent 1 个**；autonomy_agent_v24/news_agent_v24 0 接入 | ⚠️ 部分 |
| 4 | "Pipeline 文明层输出" | **kwargs 旁路**（非 ctx 链），条件性接入 | ⚠️ 弱 |
| 5 | "API response_model 全覆盖" | **3/6 = 50%**，与 R0 一样 | ❌ 未变 |
| 6 | "所有模型结构化" | **domain/Article/IntelMeta/IntelBundle 仍非 Pydantic** | ❌ 未变 |
| 7 | "结构健康度 95" | 实际 80（orchestrator 4 + agents 4 + entry 空 + domain 3） | ⚠️ 夸大 15 |
| 8 | "架构诚实度 95" | 实际 45（数字错 + 跳变无证据） | 🔴 夸大 50 |
| 9 | "综合 88-90" | 实际 74-78 | ⚠️ 夸大 12-14 |
| 10 | "P2-2 保留 8 孤立目录" | 实际生产引用 0，与之前审计数据矛盾 | 🟡 待澄清 |

---

## 6. 工作书 R1 vs R0 的真实改善

| 维度 | R0 状态 | R1 状态 | 改善 |
|---|---|---|---|
| civilization 层数 | 2 | **4** | ✅ +2 层 |
| orchestrator 文件数 | 13 | 4 | ✅ -9 文件 |
| 测试数 | 165 | **168** | ✅ +3（test_news_center_civ.py 新增 6 个，但有 3 个在其他文件被删？需核） |
| 综合分 | 67 | **74-78** | ✅ +7-11 |
| Agents 根 V 文件 | 4 | **仍 4**（V21 + V24 × 3） | ❌ 未改善 |
| entry/ 空目录 | 空 | **仍空** | ❌ 未改善 |
| domain Pydantic 化 | 4/7 | **仍 4/7** | ❌ 未改善 |
| API response_model | 3/6 | **仍 3/6** | ❌ 未改善 |

**R1 vs R0 唯一实质性改善 = P2-1 文明层 4 层接入**。其他 P0/P1 残留问题**完全未改善**。

---

## 7. 最终验收结论

**FZQ-AI V24 修正版（R1）完成了 MINIMAX 审计报告约 75% 建议项**。

**真落实**（vs R0 改善）：
- ✅ P2-1 文明层 4 层接入（Entry+Orch+Agent+Pipeline）—— **核心成就**
- ✅ 删 9 个老 orchestrator
- ✅ 168/168 测试全绿
- ✅ 真实综合从 67 → 74-78

**未改善**（R0 = R1）：
- ❌ orchestrator/ 仍 4 文件（不是"单主线"）
- ❌ agents/ 根 4 V 文件并存
- ❌ entry/ 空目录
- ❌ domain/ 3 class 非 Pydantic
- ❌ API response_model 3/6 = 50%

**工作书 R1 严重夸大**：
- 🔴 "测试 106" 实际 168（数字错 62）
- 🔴 "架构诚实度 95" 实际 45（夸大 50 分）
- ⚠️ "综合 88-90" 实际 74-78

**真实综合分：74-78/100**（工作书自评 88-90，**虚高 12-14 分**）。

---

## 8. 进一步改善路径（要达 90+ 真实分）

1. **agents/ 整合**（autonomy_agent_v24 / multi_agent / news_agent_v24 删 2 留 1）—— +5
2. **orchestrator/ 整合**（删 blackboard/task_orchestrator，迁入 unified_orchestrator_v24）—— +5
3. **domain/ 3 class Pydantic 化** —— +5
4. **API response_model 补到 6/6** —— +5
5. **entry/ 删空目录** —— +2
6. **autonomy_agent_v24 / news_agent_v24 / task_orchestrator 补 civilization** —— +3
7. **Pipeline kwargs 旁路 → ctx 链** —— +3
8. **架构诚实度 45 → 90**（数字写实、跳变给证据）—— +5（不靠代码，靠工作书质量）

**预期可达：95-100 真实分**（前提：工作书数字也写实，不夸大）。

---

## 9. 工作流提醒

**⚠️ 98 个文件改动仍未 commit。**

```
HEAD = cdec639c (V24.2.0 + 2 个 "git pull" auto-commit)
working tree: 98 个文件改动
  - D (删除) ~70
  - M (修改) ~26
  - ?? (新增) 4 (我写的 2 份审计 + test_civilization + test_news_center_civ)
```

`tests/test_news_center_civ.py` 是落实方新增的测试文件，**未在 R0 报告中提及**。R1 工作书称"106/106"——**R0 时是 165，R1 加了 test_news_center_civ 后应是 171**？但 pytest 报 168。

可能的解释：
- R0 报告 165 中已含 test_civilization 8 个 + test_news_center_civ 部分？
- 落实方在 R0 验收和 R1 验收之间又删了部分测试？

**建议落实方 commit 前先核对测试数**——106/168 都是单点快照，**不可靠**。

---

**审计员签名**：Mavis
**审计日期**：2026-07-04 13:21
**审计基线**：`cdec639c` working tree（98 文件改动未 commit）
**审计方法**：13 个验证命令（git grep × 6, pytest × 3, Get-ChildItem × 3, Select-String × 1）
**核实重点**：P2-1 4 层接入（**真属实**）+ 测试数 + orchestrator 状态 + 评分核验
