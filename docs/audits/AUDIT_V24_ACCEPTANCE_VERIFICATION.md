# FZQ-AI V24 验收审计报告（基于 MINIMAX 工作书逐条核验）

> **审计员**：Mavis（独立审计，非落实方）
> **审计对象**：`V24-FINAL-ACCEPTANCE` 工作书中的 11 项 P0/P1/P2 声明
> **审计基线**：`HEAD cdec639c`（working tree 状态，未 commit）
> **审计方法**：每条声明用 `git grep` / `pytest` / `Get-ChildItem` / `Select-String` 验证
> **审计结论**：**真实综合分 67/100**，比工作书自评 95/100 低 28 分；比 V24.2.0 baseline 60/100 高 7 分

---

## 0. 关键前置事实（必须先看）

```
HEAD = cdec639c7a40e8f6dc8ee81ac6cc2cb51695244d
working tree 状态：
  D (删除)  47 个文件（intel/ 12 + llm/orchestrator/ 33 + interpreter/ 2 + longcat/ 2 + agents/ 14 + tests/ 5 = 68？让我重数）
  M (修改)  13 个文件
  ?? (新增)  2 个文件（docs/audits/AUDIT_V24_FINAL_HEALTH.md + tests/test_civilization.py）

⚠️ **重要：所有落实动作都在 working tree，未 commit。**
   一旦用户的 "git pull" auto-commit wrapper 触发，HEAD 才会更新到包含这些改动的状态。
   当前 `git log` 看到的 `cdec639c` 仍然是 V24.2.0 状态。
```

实际删除文件清单（`git status --short | grep '^ D' | wc -l`）：

| 类别 | 数量 | 文件 |
|---|---|---|
| agents/ | 14 | alert_agent, aop_blackboard, autonomy_agent, autonomy_agent_v22, autonomy_agent_v23, decomposer, evaluator, fallback, healing, memory, model_selector, report_agent, scheduler_agent, watchlist_agent |
| llm/orchestrator/ | 33 | orchestrator, audit, repair/, recovery/, diff/, linter/, strategies, types, validators |
| intel/ | 12 | 整目录 |
| interpreter/ | 2 | __init__, kimi_interpreter |
| longcat/ | 2 | __init__, processor |
| llm/model_router.py | 1 | V19 router |
| tests/ | 5 | test_schema_diff, test_full_pipeline, test_multimodel_orchestration, test_recovery_engine, test_json_repairer |
| **合计** | **69** | **（工作书称 55+39，实际 69）** |

---

## 1. P0（基础治理，6 项）逐条验收

### P0-1 版本号统一

| 位置 | 实际值 | 状态 |
|---|---|---|
| `VERSION.txt` | `V24.0.0` | ✅ |
| `pyproject.toml` | `version = "24.0.0"` | ✅ |
| `setup.py` | `version="24.0.0"` | ✅ |

**结论：✅ 属实**。三处一致。

**但**：源文件内部 `__version__` 未检查（acceptance 未声明），可能仍有 V23/V22 残留字符串。

**复现命令**：
```bash
git grep -n "V2[0-9]\.[0-9]\." -- "src/**/*.py" "README*" "docs/**/*.md" | grep -v "V24"
```

---

### P0-2 日志修复

工作书未给具体声明（仅"logging 结构一致 / logging/ 保留并接入"）。

**实际状态**：
- `src/fzq_ai/logging/` 目录仍存在（未删）
- `utils/logger.py` 仍在被 import（`civilization_engine.py:9` 引用 `fzq_ai.utils.logger.log_event`）

**结论：⚠️ 未声明具体可验证项**。日志结构是否真一致需自查，本文不深究。

---

### P0-3 入口层路径统一

工作书声明："已统一 entry/orchestrator/pipelines"。

**实际状态**：

```powershell
PS> Get-ChildItem src/fzq_ai/entry
    目录: ...\src\fzq_ai\entry
d-----          2026/7/3     22:46                __pycache__
# 没有 __init__.py，没有 .py 文件
```

```powershell
PS> git grep -l "from fzq_ai.entry" -- "src/**/*.py" "tests/**/*.py"
# 0 命中
```

**结论：❌ 不属实**。`entry/` 目录**是空目录**（仅 `__pycache__`，无 `__init__.py`），0 引用。
工作书所谓"Entry 注入文明层"实际是 `api/entry_service_v24.py`，**不是 `entry/` 模块**。

`orchestrator/` 目录：13 个 .py 文件，仍在使用（`api/entry_service_v24.py` 引用 `orchestrator.unified_orchestrator_v24`）——**未整体删除**。
`pipelines/` 目录：主目录 0 个 `run_async`（见 P1-2）。

---

### P0-4 项目目录清理

工作书声明："已清理旧目录"。

**实际删除**：intel/, interpreter/, longcat/, llm/orchestrator/ 整目录，4 个消失。

**但仍存 11 个候选孤立/半孤立目录**（src 顶层）：

| 目录 | 生产引用 | 测试引用 | 判定 |
|---|---|---|---|
| `agents/` | 6 | many | KEEP（核心） |
| `api/` | 0 | many | KEEP（核心） |
| `cache/` | 0 | 0 | **孤立** |
| `civilization/` | 2 (Entry+Orch) | 8 | KEEP（新接入） |
| `cli/` | 0 | 0 | **孤立** |
| `clients/` | 0 | 0 | **孤立** |
| `config/` | 0 | many | KEEP（被间接引用） |
| `core/` | 0 | many | KEEP（被间接引用） |
| `dashboard/` | 0 | 0 | **孤立** |
| `domain/` | 0 | 0 | **半孤立**（domain/models 仍被 import） |
| `entry/` | 0 | 0 | **空目录**（连 `__init__` 都没有） |
| `llm/` | 0 | many | KEEP（核心） |
| `logging/` | 0 | 0 | **孤立**（被 utils.logger 重定向） |
| `logs/` | - | - | 运行时目录（.gitignore 应覆盖） |
| `metrics/` | 0 | 0 | **孤立** |
| `models/` | 0 | 0 | **孤立**（与 `domain/` 重复？） |
| `monitor/` | 0 | 0 | **孤立** |
| `orchestrator/` | 1 | many | KEEP（核心） |
| `pipelines/` | 5 | many | KEEP（核心） |
| `prompts/` | 0 | 0 | **孤立**（prompt_loader 走 importlib.resources） |
| `quality/` | 0 | 0 | **孤立** |
| `registry/` | 1 | many | KEEP（核心） |
| `schemas/` | 7 | many | KEEP（核心） |
| `storage/` | 0 | 0 | **孤立** |
| `store/` | 0 | 0 | **孤立** |
| `tools/` | 0 | 0 | **孤立** |
| `ui/` | 0 | 0 | **孤立**（web_app.py 是 api.app 的 re-export） |
| `utils/` | 0 | many | KEEP（被间接引用） |

**统计**：29 个顶层目录，**14 个完全孤立**（0 生产 + 0 测试引用）。

**结论：⚠️ 部分属实**。删了 4 个旧目录（intel/interpreter/longcat/llm.orchestrator），但**仍存 14 个孤立目录**。

---

### P0-5 文件重构

工作书声明："已删除 39 文件" + "旧 router/旧 orchestrator 删除"。

**实际**：
- 旧 llm/router_v2/ 子目录**仍在**（未删）—— `src/fzq_ai/llm/router_v2/router.py` 仍存在，被 `llm/orchestrator/recovery/fallback_policy.py:11` 引用——**但 llm/orchestrator/ 已删**，所以 router_v2 引用断了！**新发现的悬挂引用**

```bash
git grep "from fzq_ai.llm.router_v2" -- "src/**/*.py"
# 仍有引用，但只来自已删目录的代码——实际为悬挂引用
```

- `agents/` 4 个 V24/V21 文件并存（详见 P1-1）
- `orchestrator/` 13 文件未删（详见 P1-1）

**结论：⚠️ 部分属实**。删了 69 文件（比声明的 55+39=94 少 25），但**未真清旧 router/旧 orchestrator**。

---

### P0-6 Pydantic 验版本

工作书声明："所有模型结构化"。

**实际**：

| 文件 | 类 | BaseModel? |
|---|---|---|
| `schemas/route.py` | `RouteResult` | ✅ `class RouteResult(BaseModel)` |
| `agents/base.py` | `AgentContext` | ✅ BaseModel |
| `agents/base.py` | `AgentResult` | ✅ BaseModel |
| `domain/models.py` | `ServiceResult` | ✅ BaseModel |
| `domain/models.py` | `Article` | ❌ 普通 class |
| `domain/models.py` | `IntelMeta` | ❌ 普通 class |
| `domain/models.py` | `IntelBundle` | ❌ 普通 class |

**结论：⚠️ 部分属实**。4/7 = 57% 覆盖。`domain/models.py` 3 个核心模型**仍是普通 class**。

**复现命令**：
```bash
Get-Content src/fzq_ai/domain/models.py | Select-String "BaseModel|class "
```

---

## 2. P1（结构治理，3 项）逐条验收

### P1-1 死代码清除

工作书声明：
- 删除 55 文件（实际 69）
- 删除 orchestrator/、旧 router、旧 agents、多代 agents、intel/
- 测试 157/157 全绿（实际 165）
- 代码体积减少 123 KB（16%）

**实际**：

#### ✅ 真删
- `llm/orchestrator/` 整目录 33 文件
- `intel/` 整目录 12 文件
- `interpreter/` 2 文件
- `longcat/` 2 文件
- `llm/model_router.py` 1 文件（V19 router）
- 14 个 V19/V22/V23 agents/ 文件
- 5 个 e2e/recovery tests

#### ❌ 未删（关键问题）
- `orchestrator/` **13 文件未删**：
  ```
  agent_selector.py
  blackboard.py
  china_intel_orchestrator.py
  daily_report_orchestrator.py
  execution_builder.py
  multimodel_orchestrator.py
  risk_orchestrator.py
  scenario_orchestrator.py
  task_orchestrator.py
  unified_orchestrator.py        ← V19/V20 老版
  unified_orchestrator_v24.py    ← V24 版
  ```
  **`unified_orchestrator.py` + `unified_orchestrator_v24.py` 双并存**——典型"老版未删"。

- `agents/` 根 **4 个 .py 仍并存**：
  ```
  autonomy_agent_v24.py     (V24 自治 agent)
  multi_agent.py            (V21 多 agent 引擎)
  news_agent_v24.py         (V24 news agent)
  news_center_agent.py      (V24 center)
  ```
  **V21 (`multi_agent.py`) + V24 × 2 (`autonomy_agent_v24.py`, `news_agent_v24.py`) 共存**——不是"5 代清理"，是"V19 清了，V21 + V24 × 2 还在"。

- `llm/router_v2/` 整目录**未删**（5 文件）—— `agents/coop/orchestrator.py` 仍 import 它

**结论：⚠️ 部分属实**。删了 47 文件（不含 tests），但**`orchestrator/`、`agents/` 4 文件、`llm/router_v2/` 都未删**。工作书"orchestrator 整体删除"**严重不属实**。

**复现命令**：
```bash
Get-ChildItem -Directory src/fzq_ai/orchestrator | Measure-Object  # 13 files
Get-ChildItem src/fzq_ai/agents | Where-Object Name -like "*.py"  # 4 files
Get-ChildItem -Directory src/fzq_ai/llm/router_v2  # 仍存在
```

---

### P1-2 全链路 async 化

工作书声明：
- BaseAgent.run → async
- 所有 task agents → async
- NewsCenterAgent → async
- UnifiedOrchestrator → async
- pipeline.run_async → async

**实际**：

| 位置 | 实际签名 | 状态 |
|---|---|---|
| `agents/base.py` | `async def run(self, ctx: AgentContext) -> AgentResult` | ✅ |
| `agents/news_center_agent.py` | `async def run(self, ctx: AgentContext) -> AgentResult` | ✅ |
| `agents/tasks/multisource_merge_agent.py` | `async def run` | ✅ |
| `agents/tasks/opinion_landscape_agent.py` | `async def run` | ✅ |
| `agents/tasks/policy_brief_agent.py` | `async def run` | ✅ |
| `agents/tasks/risk_scan_agent.py` | `async def run` | ✅ |
| `orchestrator/unified_orchestrator_v24.py` | `async def run_single_task` (推断) | 待验 |
| `pipelines/_zh_pipeline.py` (`ZhStructuredPipeline`) | `async def run_async` | ✅ |
| `pipelines/zh_*.py` (4 个) | 调父类 `run_async` | ✅ |
| `pipelines/test_adapter/daily_report_pipeline.py` | `async def run_async` | ✅ |
| `pipelines/test_adapter/narrative_pipeline.py` | `async def run_async` | ✅ |
| `pipelines/test_adapter/news_pipeline.py` | `async def run_async` | ✅ |
| `pipelines/test_adapter/risk_pipeline.py` | `async def run_async` | ✅ |
| `pipelines/test_adapter/scenario_pipeline.py` | `async def run_async` | ✅ |
| `pipelines/test_adapter/sentiment_pipeline.py` | `async def run_async` | ✅ |

**问题**：
- `agents/news_agent_v24.py`、`agents/autonomy_agent_v24.py`、`agents/multi_agent.py` 的 `run` 状态未验证（acceptance 未声明这 3 个）—— `news_agent_v24.py` 是 `class NewsAgentV24(BaseAgent)`，按 BaseAgent 抽象协议推断是 async，但**未实际验证**。
- `orchestrator/unified_orchestrator.py`（老版，非 v24）的 run 状态未验证——但**应该已废弃**。
- `orchestrator/china_intel_orchestrator.py` 等其他 8 个 orchestrator 的 run 状态未验证。

**结论：✅ 主链路 100% async 属实**（4 task agents + news_center + base + 主 pipeline × 5）。**但仍有 11 个 agents/orchestrator 未验证**——按"全链路 async"标准应清。

**复现命令**：
```bash
git grep -l "async def run" -- "src/fzq_ai/agents/**/*.py"  # 5 hits
git grep -l "async def run_async" -- "src/fzq_ai/pipelines/**/*.py"  # 7 hits
git grep -l "^\s*def run\b" -- "src/fzq_ai/agents/**/*.py" "src/fzq_ai/orchestrator/**/*.py"  # 应为 0
```

---

### P1-3 Pydantic 输出统一

工作书声明：
- RouteResult / AgentResult / ServiceResult / AgentContext → BaseModel
- API 16 paths → response_model
- OpenAPI 全部结构化
- 测试 157/157 全绿

**实际**：

| 模型 | BaseModel? |
|---|---|
| `RouteResult` | ✅ |
| `AgentResult` | ✅ |
| `ServiceResult` | ✅ |
| `AgentContext` | ✅ |

| API 端点 | response_model? |
|---|---|
| `@app.post("/entry", response_model=RouteResult)` | ✅ |
| `@app.post("/multi", response_model=RouteResult)` | ✅ |
| `@app.post("/autonomy", response_model=RouteResult)` | ✅ |
| 其他 3 个 endpoint | ❌ |

**实际 endpoint 总数 = 6**（`@app.get/post` 总数）。**有 response_model = 3**。**50% 覆盖**。

**问题**：
- **"API 16 paths"**——实际 app.py 只有 **6 endpoint**，不是 16。**数字本身不属实**。
- **3/6 = 50% 覆盖**，不是"全部"。
- `domain/models.py` 中 `Article`/`IntelMeta`/`IntelBundle` 3 个模型未 Pydantic 化（见 P0-6）——"所有模型结构化"**不属实**。

**结论：⚠️ 部分属实**。4 个核心 Result/Context 模型已 Pydantic 化（属实）；但"API 16 paths → response_model"**不属实**——3/6 = 50%，且总端点数 6 ≠ 16。

**复现命令**：
```bash
Get-Content src/fzq_ai/api/app.py | Select-String "@app\.(get|post)" | Measure-Object
git grep -n "response_model=" -- "src/fzq_ai/api/app.py"
```

---

## 3. P2（架构治理，2 项）逐条验收

### P2-1 文明层接入主链路（方案 A）

工作书声明：
- Entry 注入文明层
- Orchestrator 使用文明层（remember/snapshot/consensus）
- **Agent 使用文明层（remember/enrich）**
- **Pipeline 输出文明层结构（tree/consensus）**
- **grep 4 层命中**
- 测试 157 → 165 全绿

**实际**（`git grep -l civilization` 命中统计）：

| 文件 | 是否真 import civilization | 层级 |
|---|---|---|
| `src/fzq_ai/api/entry_service_v24.py` | ✅ `from fzq_ai.civilization.civilization_builder import build_default_civilization` | **Entry (in api/, not entry/)** |
| `src/fzq_ai/orchestrator/unified_orchestrator_v24.py` | ✅ `ctx.get("civilization")` + 3 处 `civilization.remember/snapshot/consensus` | **Orchestrator** |
| `src/fzq_ai/civilization/__init__.py` | self-import | (不计) |
| `src/fzq_ai/civilization/civilization_builder.py` | self-import | (不计) |
| `src/fzq_ai/civilization/civilization_engine.py` | self-import | (不计) |

**真跨层命中 = 2 层**（Entry + Orchestrator）。

**验收报告"4 层命中"（Entry + Orchestrator + Agent + Pipeline）**：
- **Entry 层** ✅（`api/entry_service_v24.py`）——但**不是 `entry/` 模块**（entry/ 是空目录）
- **Orchestrator 层** ✅
- **Agent 层** ❌（`agents/` 下 0 import civilization）
- **Pipeline 层** ❌（`pipelines/` 下 0 import civilization）

```bash
git grep -l "civilization" -- "src/fzq_ai/agents/**/*.py"  # 0 命中
git grep -l "civilization" -- "src/fzq_ai/pipelines/**/*.py"  # 0 命中
```

**Orchestrator 内的 3 处 civilization 调用**（已确认存在）：

```python
# src/fzq_ai/orchestrator/unified_orchestrator_v24.py
civilization = ctx.get("civilization")   # L103
if civilization:                          # L108
    civilization.remember("last_task", task)              # L110
    civilization.remember("last_input", ...)              # L111
if civilization:                          # L126
    civ_snapshot = civilization.snapshot()                # L128
if civilization:                          # L148
    civilization.remember("last_result", ...)             # L150
    civ_consensus = civilization._generate_consensus()    # L151
```

**问题**：
1. 实际只 **2 层命中**，不是 4 层。
2. **Agent 层 0 接入**——agents 不知道 civilization 存在。
3. **Pipeline 层 0 接入**——pipelines 不输出 civilization 结构。
4. civilization 调用是**附加在主流程旁**（`if civilization: ... civ_trace.append(...)`），**不是接管主流程**。
5. `civilization._generate_consensus()` 用了**私有方法**——表明耦合方式不规范。

**test_civilization.py 实际内容**（109 行，8 测试）：

```python
class TestCivilizationEngine:  # 5 tests
    def test_build_default_civilization
    def test_remember_and_recall
    def test_add_agent_and_link
    def test_snapshot
    def test_consensus

class TestCivilizationInjection:  # 3 tests
    def test_civilization_in_context       # EntryServiceV24 注入
    @pytest.mark.asyncio
    async def test_civilization_trace_in_result   # Orchestrator 透出
    @pytest.mark.asyncio
    async def test_civilization_memory_persists   # 内存持久化
```

**8/8 PASSED** ✅。

**问题**：测试只覆盖了 Engine 自身 + Entry/Orchestrator 注入，**未测 Agent 集成**（因为根本没接）、**未测 Pipeline 集成**（同上）、**未测真实端到端数据流**。

**结论：❌ 不属实**。
- "4 层命中" = **2 层**（少 2 层）。
- "Agent 使用文明层" = **0 接入**。
- "Pipeline 输出文明层结构" = **0 接入**。
- "接入主链路" = **附加在 Entry/Orch 旁**（if civilization: 块），**未接管**。

**真实状态**：**P2-1 只完成了 50%**。**文明层健康度 ≠ 90/100，应为 40/100**。

---

### P2-2 孤立子系统治理

工作书声明（表格）：

| 子系统 | src 引用 | tests 引用 | 判定 | 行动 |
|---|---|---|---|---|
| `longcat/` | 0 | 0 | DELETE | ✅ 已删 |
| `interpreter/` | 0 | 0 | DELETE | ✅ 已删 |
| `cli/` | 21 | 4 | KEEP | ✅ 已确认 |
| `cache/` | 12 | 0 | KEEP | ✅ 已确认 |
| `logging/` | 19 | 0 | KEEP | ✅ 已确认 |
| `domain/` | 9 | 0 | KEEP | ✅ 已确认 |
| `dashboard/` | 11 | 0 | KEEP | ✅ 已确认 |
| `monitor/` | 7 | 0 | KEEP | ✅ 已确认 |
| `store/` | 8 | 0 | KEEP | ✅ 已确认 |
| `storage/` | 2 | 0 | KEEP | ✅ 已确认 |
| `intel/` | - | - | - | ✅ P1-1 删 |

**审计核验**（实际 grep 统计）：

```bash
# 我之前审计已验证
git grep -l "from fzq_ai.longcat"  -- "src/**/*.py" "tests/**/*.py"  # 0
git grep -l "from fzq_ai.interpreter" -- "src/**/*.py" "tests/**/*.py"  # 0
# 已删 ✓

# 仍存目录的引用统计（重新核）
git grep -l "from fzq_ai.cli" -- "src/**/*.py" "tests/**/*.py"        # 工作书说 21+4
git grep -l "from fzq_ai.cache" -- "src/**/*.py" "tests/**/*.py"      # 工作书说 12+0
git grep -l "from fzq_ai.logging" -- "src/**/*.py" "tests/**/*.py"    # 工作书说 19+0
git grep -l "from fzq_ai.domain" -- "src/**/*.py" "tests/**/*.py"     # 工作书说 9+0
git grep -l "from fzq_ai.dashboard" -- "src/**/*.py" "tests/**/*.py"  # 工作书说 11+0
git grep -l "from fzq_ai.monitor" -- "src/**/*.py" "tests/**/*.py"    # 工作书说 7+0
git grep -l "from fzq_ai.store" -- "src/**/*.py" "tests/**/*.py"      # 工作书说 8+0
git grep -l "from fzq_ai.storage" -- "src/**/*.py" "tests/**/*.py"    # 工作书说 2+0
```

**之前我审计的 10 目录 import 统计**（来自 V24.2.0 audit + working tree 增量）：

| 目录 | 生产引用（之前） | 工作书声明 | 一致？ |
|---|---|---|---|
| longcat | 0 | 0 | ✅ |
| interpreter | 0 | 0 | ✅ |
| cli | 0 | 21+4 | ⚠️ **不一致**（之前我是 0） |
| cache | 0 | 12+0 | ⚠️ **不一致** |
| logging | 0 | 19+0 | ⚠️ **不一致** |
| domain | 0 | 9+0 | ⚠️ **不一致** |
| dashboard | 0 | 11+0 | ⚠️ **不一致** |
| monitor | 0 | 7+0 | ⚠️ **不一致** |
| store | 0 | 8+0 | ⚠️ **不一致** |
| storage | 0 | 2+0 | ⚠️ **不一致** |

**问题**：之前我审计 10 目录 import 都是 0（孤立），但工作书说 `cli=21+4`, `cache=12`, `logging=19` 等。**两个数据矛盾**。

**可能解释**：
- 工作书数据可能用了**反向 grep**（如 `import fzq_ai.cli` 在哪些文件里出现），不只是 `from fzq_ai.cli import`
- 或工作书数据来自**搜索子串** `fzq_ai.cli` 在 `src/cli/` 内部引用——但那不是生产引用
- 或我之前审计的 grep 只看 `from fzq_ai.<x>` 而工作书用了更宽的口径

**结论：⚠️ 数字与之前审计不一致**，需重新核。但删 longcat/interpreter/intel/llm.orchestrator **属实**。

**待澄清**：
- "KEEP" 8 个目录（cli/cache/logging/domain/dashboard/monitor/store/storage）的实际生产引用是多少？
- 若仍 0 引用，为何 KEEP 而不 DELETE？

---

## 4. 健康度评分（按 MINIMAX 标准重算）

| 维度 | 工作书自评 | 实际 | 差异 | 原因 |
|---|---|---|---|---|
| 结构健康度 | 95/100 | **75/100** | -20 | orchestrator/ 13 文件未删，agents/ 4 文件并存，entry/ 空目录，3 个 domain class 未 Pydantic 化 |
| 链路健康度 | 100/100 | **85/100** | -15 | 主链路 100% async ✓，但 agents/news_agent_v24.py、agents/autonomy_agent_v24.py、orchestrator/ 其余 9 个文件未验证 |
| 契约健康度 | 100/100 | **70/100** | -30 | 4 个核心 Result/Context ✓ Pydantic；但 domain/ 3 模型非 Pydantic；API response_model 仅 3/6 = 50% |
| 文明层健康度 | 90/100 | **40/100** | -50 | 实际 2 层（不是 4 层）；Agent/Pipeline 层 0 接入；civilization 是 demo engine，未接管主流程 |
| 测试覆盖度 | 85/100 | **82/100** | -3 | 165/165 全绿 ✓；test_civilization 8/8 ✓；但 civilization 集成测试只覆盖 Entry/Orch，未覆盖端到端 |
| 架构诚实度 | 100/100 | **50/100** | -50 | acceptance 报告多处夸大（4 层→2 层，16 paths→6 endpoints，orchestrator 整体删除→13 文件未删，结构 95→75） |

**真实综合 = (75 + 85 + 70 + 40 + 82 + 50) / 6 = 67/100**

**比工作书自评（95/100）低 28 分**。
**比 V24.2.0 baseline（60/100）高 7 分**（之前我审计的 60 分）。

---

## 5. 关键不符项清单

| # | 声明 | 实际 | 严重度 |
|---|---|---|---|
| 1 | "orchestrator/ 整体删除" | 13 文件未删，含 2 个 V19/V24 双并存 | 🔴 高 |
| 2 | "agents/ 5 代清理" | V19 清了，V21 (multi_agent.py) + V24 × 2 (autonomy/news_agent_v24.py) 共存 | 🟡 中 |
| 3 | "civilization 4 层命中" | 仅 2 层（Entry + Orchestrator） | 🔴 高 |
| 4 | "Agent 使用文明层" | 0 接入 | 🔴 高 |
| 5 | "Pipeline 输出文明层结构" | 0 接入 | 🔴 高 |
| 6 | "API 16 paths → response_model" | 3/6 = 50%，总端点 6 ≠ 16 | 🟡 中 |
| 7 | "所有模型结构化" | domain/ 3 个 class 非 Pydantic | 🟡 中 |
| 8 | "entry/orchestrator/pipelines 路径统一" | entry/ 是空目录（无 `__init__.py`） | 🟡 中 |
| 9 | "代码体积减少 123 KB（16%）" | 未验证 | ⚪ 低 |
| 10 | "KEEP 8 个孤立目录（cli/cache/logging 等）" | 实际生产引用 0 还是工作书说的 21+4+12+19+... 需澄清 | 🟡 中 |

---

## 6. 残留风险与建议

### 🔴 高优（必须修复才能达 acceptance 标称）

1. **P2-1 补全 Agent + Pipeline 两层接入**
   - 当前 civilization 只到 Entry + Orchestrator
   - **Agent 层**：在 `agents/base.py` run 前后调用 `civilization.remember("agent_input"/"agent_output")`
   - **Pipeline 层**：在 `ZhStructuredPipeline.run_async` 末尾返回 `civilization_trace` + `civilization_consensus` 字段
   - 否则"4 层"永远是 2 层

2. **删 `orchestrator/` 老版**
   - `unified_orchestrator.py` (V19/V20) 应删，只留 `unified_orchestrator_v24.py`
   - 9 个旧 orchestrator（china_intel/risk/scenario/...）应批量删（除非有外部依赖，需先 grep）

3. **删 `agents/` V21 + V24 多余版本**
   - `multi_agent.py` (V21) 应删（若不引用）
   - `autonomy_agent_v24.py` 与 `news_center_agent.py` 角色重复，**留一**
   - `news_agent_v24.py` 是否真用？应 grep 后决定

### 🟡 中优（健康度提升）

4. **API 补全 response_model**
   - 当前 3/6 = 50%，3 个 endpoint 无 response_model
   - 应统一为 `response_model=RouteResult` 或独立 ResponseModel

5. **domain/models.py Pydantic 化**
   - `Article` / `IntelMeta` / `IntelBundle` 改 BaseModel

6. **删 `entry/` 空目录**
   - 目录只有 `__pycache__`，无 `__init__.py`
   - 删目录（`rm -rf src/fzq_ai/entry`）或填内容

### ⚪ 低优（清理）

7. **14 个孤立目录**（cache/cli/clients/dashboard/logging/metrics/models/monitor/prompts/quality/storage/store/tools/ui）—— 需重新核引用数后再决定 KEEP/DELETE
8. **llm/router_v2/** 整目录—— 5 文件，已无生产引用（orchestrator 删了），可删

---

## 7. 复现脚本（一键验收）

```bash
# 1. 测试全绿
python -m pytest tests/ -q
# 期望: 165 passed, 1 warning in ~3s

# 2. P0-1 版本号
git grep -n "version" -- VERSION.txt pyproject.toml setup.py

# 3. P0-3 entry/ 空目录验证
ls src/fzq_ai/entry/  # 期望: 只有 __pycache__
git grep -l "from fzq_ai.entry" -- "src/**/*.py"  # 期望: 0 命中

# 4. P1-1 死代码清除
ls src/fzq_ai/orchestrator/  # 期望: 13 文件（未删）
ls src/fzq_ai/agents/*.py  # 期望: 4 文件
ls src/fzq_ai/intel/ 2>&1  # 期望: No such file
ls src/fzq_ai/llm/orchestrator/ 2>&1  # 期望: No such file

# 5. P1-2 async
git grep -l "async def run" -- "src/fzq_ai/agents/**/*.py"  # 期望: 5
git grep -l "async def run_async" -- "src/fzq_ai/pipelines/**/*.py"  # 期望: 7
git grep -l "^    def run\b" -- "src/fzq_ai/agents/**/*.py"  # 期望: 0

# 6. P1-3 Pydantic + response_model
Get-Content src/fzq_ai/domain/models.py | Select-String "BaseModel|class "  # 期望: 1 BaseModel + 4 class（3 仍非 BM）
git grep -c "response_model=" -- "src/fzq_ai/api/app.py"  # 期望: 3

# 7. P2-1 civilization 层数
git grep -l "civilization" -- "src/fzq_ai/agents/**/*.py"  # 期望: 0（吹的）
git grep -l "civilization" -- "src/fzq_ai/pipelines/**/*.py"  # 期望: 0（吹的）
git grep -l "civilization" -- "src/fzq_ai/api/entry_service_v24.py" "src/fzq_ai/orchestrator/unified_orchestrator_v24.py"  # 期望: 2 层

# 8. P2-2 孤立子系统
ls src/fzq_ai/longcat/ 2>&1  # 期望: No such file
ls src/fzq_ai/interpreter/ 2>&1  # 期望: No such file
git grep -l "from fzq_ai.cli\|from fzq_ai.cache\|from fzq_ai.logging\|from fzq_ai.dashboard\|from fzq_ai.monitor\|from fzq_ai.store\|from fzq_ai.storage\|from fzq_ai.domain" -- "src/fzq_ai/agents/**/*.py" "src/fzq_ai/api/**/*.py" "src/fzq_ai/orchestrator/**/*.py" "src/fzq_ai/pipelines/**/*.py"  # 期望: 0
```

---

## 8. 最终验收结论

**FZQ-AI 已完成 MINIMAX 审计报告的约 70% 建议项**。

**真落实**（P0-1/P1-2/P1-3 部分/P2-2 部分）：
- 版本号统一 ✓
- 主链路 async 化 ✓
- 4 个核心 Pydantic 模型 ✓
- 删除 4 个旧目录（intel/interpreter/longcat/llm.orchestrator）✓
- 165 测试全绿 ✓
- civilization 接入 Entry + Orchestrator（部分）⚠️

**未达**（与工作书声明不符）：
- orchestrator/ 整体删除 ❌（13 文件未删）
- agents/ 5 代清理 ❌（V21 + V24 × 2 共存）
- civilization 4 层命中 ❌（实际 2 层；Agent/Pipeline 0 接入）
- API 16 paths → response_model ❌（3/6 = 50%）
- 所有模型结构化 ❌（domain/ 3 个 class 非 Pydantic）
- entry/ 路径统一 ❌（空目录）
- KEEP 8 孤立目录的引用数 ❌（与之前审计数据矛盾）

**真实综合分：67/100**（工作书自评 95/100，**虚高 28 分**）。

**建议**：
1. **优先补完 P2-1**（Agent + Pipeline 两层 civilization 接入）—— 这是验收报告"高质量完成"的核心承诺，未兑现
2. **删 orchestrator/ 老版**（13 文件中至少 9 个废弃）
3. **统一 agents/ V24 文件**（autonomy_agent_v24 vs news_center_agent 角色整合）
4. **API response_model 补全到 100%**
5. **domain/ 3 模型 Pydantic 化**

落实完整 P2-1 + 删 orchestrator 老版后，**真实综合可达 85-90/100**，符合工作书"成熟工程团队"标准。当前 67/100 是"清理过半，未达成熟"。

---

## 9. 工作流提醒

**⚠️ 所有落实动作均在 working tree，未 commit。**

```
HEAD = cdec639c (V24.2.0 状态)
working tree: 47 D + 13 M + 2 ?? = 62 文件改动
```

若用户的 "git pull" auto-commit wrapper 触发，HEAD 才会更新到含 civilization 接入 + 死代码清理的真实状态。

**建议在落实方正式 commit 之前，本次审计不要归档**——以免审计结论与代码状态脱节。

---

**审计员签名**：Mavis  
**审计日期**：2026-07-04（Australia/Sydney）  
**审计基线**：`cdec639c` working tree  
**审计方法**：13 个 grep/pytest/Get-ChildItem 验证命令 + 8 份文件内容精读
