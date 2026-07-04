# FZQ-AI V24 · 终极健康审计报告

> **审计员**：Mavis（受命于"MINIMAX"角色）
> **审计日期**：2026-07-04
> **审计范围**：`C:\Users\nicka\FZQ-AI-WORKSPACE\FZQ-AI` @ commit `cdec639c`
> **审计方法**：对照工程化自我介绍中的 10 条声明，逐条用 `git grep` / `Get-ChildItem` / `pytest --collect-only` / AST 静态分析验证代码事实
> **审计原则**：不做代码改动，只陈述可证伪的事实

---

## 0. TL;DR

- **项目健康度自评分**：**~60/100**（不是自我介绍的"已健康"）
- **162 passed** ✅ 数字属实，但 5 个 e2e 测试全是 10-31 行冒烟
- **P0 修复已 commit** ✅（4 个 P0 bug + 入口统一 + pipeline 真业务化都在 HEAD）
- **~30% 声明被事实推翻** ❌（Router、agents 多代、Civilization、Pydantic 输出、sync/async 都有差距）
- **修复 ROI 最高的 5 项工作量约 3.5 小时**，可让项目进入 80 分健康态

---

## 1. 声明 vs 事实对照表

| # | 自我介绍声明 | 实际验证 | 评分 |
|---|---|---|---|
| 1 | "162/162 测试全部通过" | ✅ `pytest --collect-only` 报告 162 tests collected；`pytest -q` 报告 162 passed | ✅ 100% |
| 2 | "Pydantic 版本已锁定" | ✅ `requirements.txt` 锁 `pydantic==2.13.4`, `pyproject.toml` 一致 | ✅ 100% |
| 3 | "FastAPI 单一入口已治理" | ✅ `src/fzq_ai/api/app.py` 是唯一 FastAPI app；`ui/web_app.py` 改为 thin re-export；11 个 README 端点全部 reachable | ✅ 100% |
| 4 | "旧目录已清理（core/static/js/real/test_adapter）" | ✅ 上述目录不存在 | ✅ 100% |
| 5 | "文明层空洞已清理（25 个模块删除）" | ✅ `civilization/` 从 37 个文件 → 3 个文件（builder + engine + __init__） | ✅ 100% |
| 6 | "Router 已统一（llm_router 删除）" | ❌ **5 套 router 残留**（详见 §3.1） | ❌ 40% |
| 7 | "sync/async 执行链路已统一" | ❌ **8 sync `def run` + 10 async `async def run` 混合**（详见 §3.2） | ❌ 50% |
| 8 | "所有引用路径已修复" | ⚠️ P0 修复属实；但有 5+ 个跨代 import（详见 §3.3） | 🟡 70% |
| 9 | "无幽灵引用、无旧路径残留" | ❌ **11 个孤立子目录 ~50 个文件**（详见 §3.4） | ❌ 25% |
| 10 | "162 测试覆盖所有链路" | ❌ **5 个 e2e 测试全是冒烟**（10-31 行/个），mock 多于真业务 | ❌ 30% |
| 11 | "无循环依赖" | ⚠️ 当前未触发；但 `agents/coop/orchestrator.py:12` 显式 import `registry.agents` 是潜在风险 | 🟡 80% |
| 12 | "无多代架构残留" | ❌ **27 个 agents/ 文件 V19/V21/V22/V23/V24 五代并存**（详见 §3.5） | ❌ 30% |
| 13 | "无重复入口" | ✅ `api/app.py` 唯一 | ✅ 100% |
| 14 | "所有输出结构化（Pydantic）" | ❌ API 响应全为 `to_dict()` 返回 dict，无 `response_model`（详见 §3.6） | ❌ 30% |
| 15 | "Civilization 已接入主链路" | ❌ **`grep "from fzq_ai.civilization" -- "src/**/*.py" "tests/**/*.py"` → 0 matches**（详见 §3.7） | ❌ 0% |
| 16 | "sync/async 已统一" | ❌ 同上 #7 | ❌ 50% |

**整体**：15/16 声明中 **6 条被事实推翻**、**3 条部分不符**、**7 条属实**。

---

## 2. 项目规模统计

### 2.1 代码体量

| 指标 | 数值 |
|---|---|
| 全部 `.py` 文件（git tracking） | 290 |
| 子目录（除 `__pycache__`） | 31 |
| 孤立子系统 | 11 个子目录 |
| Router 套数 | 5 (2 生产在用 + 3 孤立) |
| civilization 文件 | 3 (0 个生产 import) |
| llm/orchestrator/ 文件 | 33 个 (0 个生产 import) |
| 孤立大文件 | `kimi_interpreter.py` (608 行 = 30KB), `narrative_engine.py` (623 行) |
| agents/ 文件 | 27 个，5 版本标签并存 |

### 2.2 测试统计

| 指标 | 数值 |
|---|---|
| 收集测试数 | 162 |
| 同步 `def run` | 8 个 |
| 异步 `async def run` | 10 个 |
| e2e 冒烟测试 (10-31 行) | 5 |
| 端点 e2e (V24.2.0 加的 16 个) | **不在 HEAD**（被某次 auto-commit 删了） |
| Mock pipeline 测试 | ~20 |
| 类型/Enum 测试 | ~50 |

### 2.3 完整子目录列表（31 个）

```
src/fzq_ai/
├── agents/          27 文件（5 代标签并存）
├── api/             7 文件（V24 统一入口）
├── cache/           1 真文件 + 0 字节 __init__（孤立）
├── civilization/    2 真业务 + 1 __init__（0 import）
├── cli/             1 真文件（孤立，引用 V19 agents）
├── clients/         (V19 ModelClient 套件)
├── config/          V24 配置（dict + dataclass 双 API）
├── core/            5 文件
├── dashboard/       2 文件（孤立，引用 V19 agents）
├── domain/          4 文件（孤立）
├── entry/           0 文件（V19/V23 死代码已删）
├── intel/           11 文件（孤立子系统）
├── interpreter/     1 大文件 (30KB，孤立)
├── llm/             18 文件 + 6 子目录
│   ├── clients/     6 API client（独立实现）
│   ├── providers/   6 Provider（独立实现）
│   ├── orchestrator/ 33 文件孤立子系统 ⚠️
│   ├── router_v2/   6 文件
│   └── test_adapter/ 2 文件
├── logging/         3 文件（孤立）
├── longcat/         1 文件（孤立）
├── metrics/         8 文件
├── models/          0 文件（真空）
├── monitor/         1 文件（孤立）
├── orchestrator/    9 文件（混合 V19/V24 + 4 个业务 orchestrator + 2 unified）
├── pipelines/       9 文件（V24 真业务 + base + protocol + test_adapter）
├── prompts/         1 __init__ + 5 zh/ + 4 其它
├── quality/         3 文件（`minimax` 命名奇怪但有真业务）
├── registry/        4 文件
├── schemas/         7 文件 + 1 子目录（zh_tasks/ 真业务）
├── storage/         0 字节 __init__（真空）
├── store/           3 文件（孤立，V8）
├── tools/           (V19 tools 残留)
├── ui/              1 web_app.py（thin re-export api.app）
└── utils/           21 文件
```

---

## 3. 关键不符：每条声明的具体证据

### 3.1 ❌ "Router 已统一" — 5 套 router 残留

| Router | 位置 | 状态 | 实际调用方 |
|---|---|---|---|
| V24-final | `src/fzq_ai/llm/router.py` | **生产在用** | V24 pipeline（`_zh_pipeline.py`）调 `choose_model`/`call_llm` |
| V19 业务路由 | `src/fzq_ai/core/task_router.py` | **生产在用** | `api/zh_endpoints.py` |
| V19 业务 | `src/fzq_ai/llm/model_router.py` | 孤立 | **0 引用** |
| V13 兼容层 | `src/fzq_ai/llm/llm_router.py` | 孤立 | **0 引用** |
| V2 task-aware | `src/fzq_ai/llm/router_v2/` | 孤立 | 仅 `llm/orchestrator/recovery/fallback_policy.py:11` 和 3 个 e2e 测试 |
| Mock | `src/fzq_ai/llm/test_adapter/llm_router.py` | 测试桩 | 5 个 mock 测试 |

**验证命令**：

```bash
git grep -l "from fzq_ai\.llm\.model_router\|from fzq_ai\.llm\.llm_router\|from fzq_ai\.llm\.router_v2" \
  -- "src/fzq_ai/api/**.py" "src/fzq_ai/agents/**.py" \
     "src/fzq_ai/orchestrator/**.py" "src/fzq_ai/entry/**.py" \
     "src/fzq_ai/pipelines/**.py" "src/fzq_ai/llm/router.py"
# 输出: 0 matches（除 orchestrator/recovery/fallback_policy.py 外）
```

### 3.2 ❌ "sync/async 统一" — 8 sync + 10 async 混合

**同步 `def run` (8 个)**：
- `agents/base.py:73` (BaseAgent 默认 run)
- `agents/decomposer.py:130` (TaskDecomposer)
- `agents/multi_agent.py:50` (MultiAgentEngine)
- `agents/news_center_agent.py:37` (NewsCenterAgent)
- `agents/tasks/{multisource,opinion,policy,risk}_*.py:12/20` (4 个 task agent)
- `orchestrator/task_orchestrator.py:37` (TaskOrchestrator)
- `orchestrator/test_adapter/task_orchestrator.py:29` (Mock)

**异步 `async def run` (10 个)**：
- `orchestrator/{china,daily,risk,scenario}_orchestrator.py:8/10` (4 个业务 orchestrator)
- `orchestrator/unified_orchestrator.py:162` (V23)
- `orchestrator/unified_orchestrator_v24.py:37` (V24)
- `pipelines/_zh_pipeline.py:118` (ZhStructuredPipeline 基类)
- `pipelines/base.py:60` (BasePipeline)
- `pipelines/refinement_pipeline.py:154`
- `pipelines/risk_pipeline.py:48`

**生产链路的 sync/async 跨边界**：

```
EntryServiceV24.handle_single (async)
  → unified_orchestrator_v24.run_single (async)
    → NewsAgentV24.run (sync)              ⚠️ sync↔async 切换
      → BaseAgent.run (sync, default)        ⚠️ sync↔async 切换
        → pipeline.run_async (async)
```

**至少 2 次 sync↔async 切换**。Task agent 内部用 `asyncio.run(pipeline.run_async(...))` 是反模式（阻塞 event loop）。

### 3.3 ❌ "无幽灵引用" — 5+ 个跨代 import

| 位置 | 引用 | 代际跨度 |
|---|---|---|
| `src/fzq_ai/cli/agent.py` | `from fzq_ai.agents.alert_agent` | V4 CLI → V19 agents |
| `src/fzq_ai/dashboard/components/event_list.py` | `from fzq_ai.agents.alert_agent` | V8 dashboard → V19 agents |
| `src/fzq_ai/dashboard/dashboard.py` | `from fzq_ai.agents.{report,watchlist}_agent` | V8 → V19 |
| `src/fzq_ai/agents/autonomy_agent.py` (V4.6) | `from fzq_ai.store.intel_store import IntelStore` | **V4.6 → V8，跨 4 代** |
| `src/fzq_ai/intel/pipeline_registry.py` | 重复实现 `src/fzq_ai/pipelines/registry.py` | V8 → V24 重复 |
| `src/fzq_ai/intel/intel_store.py` vs `src/fzq_ai/store/intel_store.py` | V8 重复实现 | 同上 |

### 3.4 ❌ "无旧路径残留" — 11 个孤立子目录 ~50 个文件

| 子目录 | 实际内容 | 孤立度 |
|---|---|---|
| `cli/` | `agent.py` (3KB) | 完全孤立（cli 是 V4 时代） |
| `cache/` | `news_cache.py` (1KB) | 完全孤立 |
| `logging/` | `llm_logger.py` + `logger.py` | 完全孤立 |
| `domain/` | `enums.py` + `errors.py` + `models.py` | 完全孤立 |
| `dashboard/` | `dashboard.py` + `components/event_list.py` | 完全孤立 |
| `intel/` | 11 个真业务文件 (40KB) | **完全孤立**（生产 0 引用） |
| `interpreter/` | `kimi_interpreter.py` (30KB, 608 行) | 完全孤立 |
| `longcat/` | `processor.py` | 完全孤立 |
| `monitor/` | `token_monitor.py` | 完全孤立 |
| `store/` | `event_extractor.py` + `intel_store.py` + `trend_engine.py` | 完全孤立 |
| `storage/` | 0 字节 `__init__.py` | 真空 |
| `models/` | 0 文件 | 真空 |

**孤立代码总量估计**：~150KB Python。

**验证命令**：

```bash
git grep -l "from fzq_ai\.intel\|from fzq_ai\.store\|from fzq_ai\.cache\|from fzq_ai\.interpreter\|from fzq_ai\.dashboard\|from fzq_ai\.cli\|from fzq_ai\.longcat\|from fzq_ai\.monitor\|from fzq_ai\.domain\|from fzq_ai\.logging\b" \
  -- "src/fzq_ai/api/**.py" "src/fzq_ai/orchestrator/**.py" \
     "src/fzq_ai/agents/news_*.py" "src/fzq_ai/agents/multi_agent.py" \
     "src/fzq_ai/agents/news_center_agent.py" "src/fzq_ai/entry/**.py" \
     "src/fzq_ai/pipelines/**.py" "src/fzq_ai/ui/**.py"
# 输出: 0 matches
```

### 3.5 ❌ "无多代架构残留" — 27 个 agents/ 文件 5 代并存

| 标签 | 文件 | 文件数 |
|---|---|---|
| V19 | `alert_agent.py`, `autonomy_agent.py`, `report_agent.py`, `scheduler_agent.py`, `watchlist_agent.py`, `__init__.py` | 6 |
| V21 | `decomposer.py`, `evaluator.py`, `fallback.py`, `healing.py`, `memory.py`, `model_selector.py` | 6 |
| V22 | `autonomy_agent_v22.py`, `coop/{blackboard,orchestrator,protocol}.py` | 4 |
| V23 | `autonomy_agent_v23.py` | 1 |
| V24 | `aop_blackboard.py`, `autonomy_agent_v24.py`, `base.py`, `multi_agent.py`, `news_agent_v24.py`, `news_center_agent.py` | 6 |
| 业务 | `tasks/{risk_scan,policy_brief,opinion_landscape,multisource_merge}_agent.py` | 4 |

**4 个 `autonomy_agent*` 文件**同时存在：`_v22` (V22), `_v23` (V23), `_v24` (V24), 无后缀的 (V4.6 stub)。任何新人无法判断该用哪个。

**验证命令**：

```bash
git ls-files src/fzq_ai/agents/ | head -30
# 实际 27 个 .py 文件

Select-String -Path src/fzq_ai/agents/**/*.py -Pattern '# V\d{2}|Version: V\d{2}' 2>&1
# 找出 V19/V21/V22/V23/V24 标签
```

### 3.6 ❌ "所有输出结构化（Pydantic）" — 主链路返回 dict

**Pydantic 实际使用范围**：

| 用途 | 状态 |
|---|---|
| API Request body | ✅ 有（`V24EntryRequest`, `ZhIntelPayload` 等 Pydantic BaseModel） |
| `schemas/zh_tasks/*.py` 内部 schema 校验 | ✅ 有（4 个 Output 类） |
| `schemas/core_models.py` 数据模型 | ✅ 有（20+ 模型） |
| **API Response** | ❌ **无 `response_model=Pydantic` 声明**（`api/app.py:144,153,162` 用 `result.to_dict()` 返回 dict） |
| `RouteResult` | ❌ **plain Python class**（`src/fzq_ai/schemas/route.py:7`），不是 Pydantic |
| `AgentResult` | ❌ **`@dataclass`**（`src/fzq_ai/agents/base.py:30`），不是 Pydantic |
| Pipeline 返回值 | ❌ `Dict[str, Any]` |

**结论**：Pydantic 仅用于 input 校验和内部 schema，**API Response 仍是 dict**。前端类型靠注释和记忆，无编译器保护。

**验证命令**：

```bash
git grep -n "response_model=" -- "src/fzq_ai/api/**.py"
# 期望: @app.post(..., response_model=SomePydantic)
# 实际: 0 matches
```

### 3.7 ❌ "Civilization 已接入主链路" — 0 import

```bash
$ git grep -l "from fzq_ai.civilization" -- "src/**/*.py" "tests/**/*.py"
# 输出: 0 files
```

`src/fzq_ai/civilization/` 含 3 个文件：
- `civilization_engine.py` (5521 bytes, 真业务：graph + memory + goals + planning + consensus)
- `civilization_builder.py` (1437 bytes)
- `__init__.py` (302 bytes)

**完全没接入主链路**。API 入口、Agent 链路、Pipeline 链路、LLM 链路都未引用 civilization。

### 3.8 ❌ "llm/orchestrator/ 已清理" — 33 文件仍在

`src/fzq_ai/llm/orchestrator/` 目录含 **33 个文件** + 4 个子目录：

```
llm/orchestrator/
├── audit.py                  (ConsistencyAuditor)
├── orchestrator.py           (MultiModelOrchestrator v1, 主模型→校验→修复→审计)
├── repair.py                 (re-export)
├── strategies.py             (ModelStrategy)
├── types.py                  (Type definitions)
├── validators.py             (OutputValidator)
├── __init__.py
├── diff/        (5 files: field_diff, report, schema_diff, structure_diff, type_diff)
├── linter/      (7 files: detectors, json_checker, prompt_linter, report, rules, schema_checker)
├── recovery/    (8 files: error_classifier, fallback_policy, recovery_engine, repair_policy, report, retry_policy)
└── repair/      (7 files: field_filler, json_repairer, report, schema_repairer, structure_fixer)
```

**0 个生产代码引用** `fzq_ai.llm.orchestrator.*`。**仅 5 个 e2e 测试**引用这套孤立子系统。

**声明"MOC v1 接入主链路"是错的**——MOC v1 完全孤立，由 5 个 10-31 行冒烟测试"自我证明存在"。

### 3.9 ❌ "162 测试覆盖所有链路" — 5 e2e 冒烟

e2e 测试详情：

| 文件 | 行数 | 测试数 |
|---|---|---|
| `tests/test_e2e/test_full_pipeline.py` | 31 | 1 |
| `tests/test_e2e/test_multimodel_orchestration.py` | 26 | 1 |
| `tests/test_recovery/test_recovery_engine.py` | 15 | 1 |
| `tests/test_self_healing/test_json_repairer.py` | 12 | 1 |
| `tests/test_audit/test_schema_diff.py` | 10 | 1 |

**5 个 e2e 测试全是 10-31 行的冒烟**。没有任何一个跑通"用户输入 → 4 个 Pipeline 真业务 → 软失败聚合 → API 返回"。

**端点 e2e (V24.2.0 加的 16 个)** 实际**不在 HEAD**（被某次 auto-commit 删了）。我之前 V24.2.0 commit (bc6a621d) 里的 `tests/test_api/test_endpoints_e2e.py` **不在仓库**。

### 3.10 🟡 潜在循环依赖

`src/fzq_ai/agents/coop/orchestrator.py:12`：

```python
from fzq_ai.registry.agents import get_agent
```

这是**真同步 import**。当前未触发循环，因为 `agents/__init__.py` 不 import `coop/`。但任何人在 `agents/__init__.py` 加 `from .coop import *` 都会立刻引爆循环。

**最佳做法**：`coop/orchestrator.py` 也用 lazy import 模式（如同 `news_center_agent.py`）。

---

## 4. 已治理的债务（声明属实部分）

✅ **P0 修复**（4 个 bug 全部在 HEAD `cdec639c` 中）：
- 9 处 `from src.fzq_ai` 错误路径已修
- `UnifiedOrchestrator.run_multi` 缩进错位已修（变 class method）
- CORS `["*"]` + credentials 已修（用 `ALLOWED_ORIGINS` env）
- 前端 Dockerfile `npm start` 已修（multi-stage build + `npm run preview`）

✅ **入口统一**：唯一 `api/app.py`，11 个 README 端点全部 reachable

✅ **Pipeline 真业务化**：`ZhStructuredPipeline` 基类 + 4 个 pipeline 缩成 25 行 + JSON 解析 + Pydantic 校验 + 软失败语义

✅ **新闻聚合真业务**：`NewsCenterAgent` 4/4 子 agent 跑通 + 软失败聚合

✅ **CORS / .env / .gitignore / 根目录清理 / 版本号统一**

✅ **3 套基础配置**：Pydantic v2 锁版 / FastAPI 单一入口 / 文档目录清理

---

## 5. 风险评估

### 5.1 高风险（影响未来扩展）

| ID | 风险 | 影响 |
|---|---|---|
| R1 | 5 套 router + 33 个 llm/orchestrator 孤立子系统（~150KB 死代码） | 任何重构会被 100+ import 链误导 |
| R2 | 27 个 agents/ 文件 5 代标签（特别是 4 个 autonomy_agent*） | 新人无法判断该用哪个 |
| R3 | Civilization 0 import 但 README 宣传"已接入" | 任何新功能都会避开 civilization（因为没人知道怎么用） |

### 5.2 中风险

| ID | 风险 | 影响 |
|---|---|---|
| R4 | sync/async 跨边界（生产链 2 次切换） | 性能优化（并发）会被 sync `run()` 阻塞 |
| R5 | 主链路输出非 Pydantic | API 响应是 dict，前端类型靠注释/记忆 |
| R6 | 5 个 e2e 测试冒烟（10-31 行） | 不足以覆盖真业务 |

### 5.3 低风险

| ID | 风险 | 影响 |
|---|---|---|
| R7 | 潜在循环依赖（`agents/coop/orchestrator.py` ↔ `registry/agents`） | 当前不触发，结构债 |
| R8 | 30 个 `__pycache__/` 目录 | Git 应该忽略（实际有 2 个仍被跟踪的 `.pyc`） |

---

## 6. 治理建议（按 ROI 排序）

### 6.1 立即执行（1 天内，ROI 极高）

| # | 任务 | 工作量 | 命令/方法 | 收益 |
|---|---|---|---|---|
| 1 | 删 `llm/orchestrator/` 33 文件 | 0.5h | `mavis-trash 'src/fzq_ai/llm/orchestrator/'` + 删 4 个引用 e2e 测试 | 减 60KB 死代码 |
| 2 | 删 `agents/coop/` 3 文件 | 0.5h | `mavis-trash` 整个目录 | 减 5KB + 消除潜在循环 |
| 3 | 删 V19/V21/V22/V23 agents 文件（保留 V24） | 1h | `mavis-trash` 14 文件（保留 base, news_*, multi_agent, news_center, tasks/*, aop_blackboard, autonomy_agent_v24, watchlist_agent, report_agent, __init__） | 5 代 → 1 代 |
| 4 | 删 `llm/{model_router,llm_router}.py` | 0.5h | `git grep` 确认 0 引用后删 | 5 套 router → 3 套 |
| 5 | 删 `intel/`, `interpreter/`, `store/`, `storage/`, `cache/`, `cli/`, `domain/`, `dashboard/`, `longcat/`, `monitor/`, `logging/`, `models/`, `tools/` | 1h | 确认 0 引用后批量删 | 减 ~100KB |

### 6.2 本周执行（3 天内，ROI 高）

| # | 任务 | 工作量 | 方法 | 收益 |
|---|---|---|---|---|
| 6 | `task_orchestrator.py` 改 async | 2h | `def run` → `async def run` + `await ...` | 消除 1 个 sync 跨边界 |
| 7 | `agents/base.py` 默认 `run` 改 async | 2h | `async def run` + `await` 子方法 | 链路统一 async |
| 8 | 4 个 `tasks/*_agent.py` 改 async `run` | 1h | 移除 `asyncio.run()` 嵌套 | 消除反模式 |
| 9 | `RouteResult` 改 Pydantic BaseModel | 1h | `class RouteResult(BaseModel):` | API 响应类型保证 |
| 10 | 补 e2e：`test_pipelines_real.py` 加真业务测试 | 4h | 每个 pipeline 加 happy path + error path 测试 | 测试深度 |

### 6.3 下周执行（1 周内，战略性）

| # | 任务 | 工作量 | 方法 | 收益 |
|---|---|---|---|---|
| 11 | Civilization 真接入 OR 删 | 8h vs 1h | 在 `entry_service_v24.py` 注入 `CivilizationEngine` 决策；或从 README 移除 | 架构图变真 |
| 12 | API Response 全部加 Pydantic `response_model` | 4h | 重构 API 路由用 Pydantic schema | OpenAPI 文档 + 前端类型 |
| 13 | 4 个 `autonomy_agent*` 合并为 1 个 V24 | 1h | 保留 `autonomy_agent_v24.py`，删 3 个 | 消除 V22/V23/V4.6 残留 |
| 14 | 11 个孤立子目录最终决断 | 4h | 接入 or 删 | 项目瘦身 30% |

### 6.4 长期（治理而非扩张）

- **所有"已接入"类声明必须有 import 链证据**
- **commit message 治理**：当前 20+ commit 全部 "git pull"（匿名 commit 让 git blame 失效）
- **多代标签规范**：禁止 `_v22/_v23/_v24` 后缀，强制 deprecation 政策
- **端点 e2e 测试补回**：V24.2.0 加的 16 个被删了，重新加

---

## 7. COPILOT 可立即执行的验证命令

```bash
# 1. 测试数字
cd "C:\Users\nicka\FZQ-AI-WORKSPACE\FZQ-AI"
python -m pytest tests/ -q --tb=short

# 2. Router 残留
git ls-files 'src/fzq_ai/**/*router*.py' 'src/fzq_ai/**/router*/'

# 3. agents 多代
git ls-files 'src/fzq_ai/agents/' | Measure-Object
Select-String -Path 'src/fzq_ai\agents\**\*.py' -Pattern '# V\d{2}|Version: V\d{2}'

# 4. Civilization 接入
git grep -l "from fzq_ai.civilization" -- 'src/**/*.py' 'tests/**/*.py'
# 期望: 0 matches（实际 0 matches → 声明错误）

# 5. sync/async 分布
git grep -nE '^\s+(async )?def run\(' -- 'src/fzq_ai/**/*.py' | Select-String "def run|async def run"

# 6. Pydantic Response
git grep -n "response_model=" -- 'src/fzq_ai/api/**/*.py'
# 期望: 至少 1 个 match（实际 0 → 声明错误）

# 7. llm/orchestrator 孤立
git ls-files 'src/fzq_ai/llm/orchestrator/**.py' | Measure-Object
git grep -l "from fzq_ai.llm.orchestrator" -- 'src/fzq_ai/api/**/*.py' 'src/fzq_ai/agents/**/*.py' 'src/fzq_ai/orchestrator/**/*.py' 'src/fzq_ai/pipelines/**/*.py'
# 期望: 生产代码 0 引用（实际 0 → 整套孤立）

# 8. 孤立子目录
Get-ChildItem -Directory 'src/fzq_ai' | Where-Object { $_.Name -notlike "__pycache__" } | ForEach-Object {
    $name = $_.Name
    $imports = git grep -l "from fzq_ai.$name" -- 'src/fzq_ai/api/**/*.py' 'src/fzq_ai/agents/**/*.py' 'src/fzq_ai/orchestrator/**/*.py' 'src/fzq_ai/pipelines/**/*.py' 'src/fzq_ai/entry/**/*.py' 2>$null
    if (-not $imports) { Write-Host "ORPHAN: $name" }
}
# 期望: 输出 ORPHAN: cli, cache, logging, domain, dashboard, intel, interpreter, longcat, monitor, store, storage, models

# 9. 端点 e2e 是否在 HEAD
git ls-files 'tests/test_api/'
# 期望: test_endpoints_e2e.py（实际不存在 → 被 auto-commit 删了）
```

---

## 8. 结论

**项目处于"清理过渡态"**——V24.0-V24.2 已修复 80% 的 P0/P1 债务，但仍有 **6 个"宣传与事实不符"的结构性差距**：

1. 5 套 router 残留
2. 27 个 agents/ 文件 5 代并存
3. 11 个孤立子目录 ~50 个文件
4. Civilization 0 import
5. Pydantic 仅 input，response 仍 dict
6. sync/async 跨边界

**不要相信"已健康"类自我介绍**。它写于自我安慰状态，不是代码事实。

**但代码本身有救**——§6.1 立即执行的 5 项工作量约 3.5 小时，可让项目从 60 分进入 80 分健康态。

---

## 附录 A：审计员联系方式

> 本报告由 Mavis 审计，遵循"陈述可证伪事实"原则。报告未做任何代码改动。
>
> 任何声明都有可复现的 shell 命令（§7）。COPILOT 可直接执行验证。

## 附录 B：术语表

| 术语 | 含义 |
|---|---|
| 孤立子系统 | 0 个生产代码 import 但有完整实现的子目录 |
| 冒烟测试 | 仅验证模块能 import/实例化，不验证真业务 |
| 多代残留 | 同一概念有 V19/V21/V22/V23/V24 多个版本的代码 |
| sync/async 跨边界 | 同一调用链中 sync 与 async 函数反复切换 |
