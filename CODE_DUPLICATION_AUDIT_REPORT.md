# FZQ-AI 代码重复与死代码审计报告

> 审计时间：2026-07-01  
> 审计范围：`C:/Users/nicka/FZQ-AI-WORKSPACE/FZQ-AI`  
> 审计重点：文件重复、死代码/空文件、顶层死目录

---

## 一、重复文件分析

### 1.1 `agents/` vs `agents/tasks/` — 同名文件（4对）

| 文件 | `agents/` 版本 | `agents/tasks/` 版本 | 结论 |
|------|-------------|----------------------|------|
| `policy_brief_agent.py` | 16行，旧版 `PolicyBriefAgent` 类，简单 `run(model, text)` 接口 | 59行，新版继承 `BaseAgent`，使用 `LLMRouter` + `DeepSeekStructOptimizer` + `validate_and_fix` 多阶段链路 | **内容完全不同，tasks/ 是生产版本** |
| `risk_scan_agent.py` | 17行，旧版 `RiskScanAgent` 类，简单接口 | 43行，新版继承 `BaseAgent`，使用 `PipelineRegistry` 异步执行 `zh_risk_scan` pipeline | **内容完全不同，tasks/ 是生产版本** |
| `multisource_merge_agent.py` | 16行，旧版简单类 | 43行，新版继承 `BaseAgent`，使用 `PipelineRegistry` | **内容完全不同，tasks/ 是生产版本** |
| `opinion_landscape_agent.py` | 16行，旧版简单类 | 43行，新版继承 `BaseAgent`，使用 `PipelineRegistry` | **内容完全不同，tasks/ 是生产版本** |

**引用关系：**
- `src/fzq_ai/agents/__init__.py` 导出 `agents/` 旧版（`RiskScanAgent`, `PolicyBriefAgent`, `OpinionLandscapeAgent`, `MultiSourceMergeAgent`）
- `src/fzq_ai/agents/registry.py` 注册 `agents/tasks/` 新版（`zh_policy_brief`, `zh_risk_scan`, `zh_opinion_landscape`, `zh_multisource_merge`）
- `src/fzq_ai/utils/agent_hub.py` 引用 `agents/` 旧版（用于 `AGENT_CATALOG`）

**问题：** 旧版 `agents/` 下的4个文件已无人维护，且功能被 `agents/tasks/` 完全替代，但 `agents/__init__.py` 和 `utils/agent_hub.py` 仍在导入旧版，导致潜在的混淆和错误调用。

---

### 1.2 `agent_hub.py` — 两处独立文件

| 文件 | 内容 | 引用情况 |
|------|------|----------|
| `src/fzq_ai/agent_hub.py` | 69行，完整 `AgentHub` 类，集成 `LLMRouter` + 4个 Pipeline（news/narrative/risk/daily_report），提供 `run_news()`/`run_narrative()` 等入口 | **无生产代码引用**（grep 未找到 `from fzq_ai.agent_hub` 或 `from fzq_ai.utils.agent_hub`） |
| `src/fzq_ai/utils/agent_hub.py` | 28行，简单 `AGENT_CATALOG` 字典，仅导入 `agents/` 旧版4个智能体并实例化 | **无生产代码引用** |

**结论：** 两个文件互不引用、内容完全不同。`agent_hub.py` 是死代码；`utils/agent_hub.py` 也是死代码，且依赖已被废弃的 `agents/` 旧版。

---

### 1.3 `registry.py`（文件） vs `registry/`（目录）

| 路径 | 状态 | 说明 |
|------|------|------|
| `src/fzq_ai/registry.py` | **空文件（0字节）** | 完全无内容，属于死代码 |
| `src/fzq_ai/registry/__init__.py` | 5行，包注释 | 被 `unified_orchestrator.py` 通过 `from fzq_ai.registry.agents` 引用 |
| `src/fzq_ai/registry/agents.py` | 19行，`AgentRegistry` 类 | 被 `unified_orchestrator.py` 引用 |
| `src/fzq_ai/registry/pipelines.py` | 18行，`PipelineRegistry` 类 | 被 `unified_orchestrator.py` 引用 |
| `src/fzq_ai/registry/orchestrators.py` | 18行，`OrchestratorRegistry` 类 | 被 `unified_orchestrator.py` 引用 |

**结论：**
- `src/fzq_ai/registry.py` 空文件应删除。
- `src/fzq_ai/registry/` 目录是生产注册中心，被 `unified_orchestrator.py` 引用，**应保留**。
- 注意：此处的 `registry/pipelines.py` 的 `PipelineRegistry`（简单 dict 封装）与 `src/fzq_ai/pipelines/registry.py` 的 `PipelineRegistry`（装饰器注册机制）是不同实现，存在命名冲突风险。

---

### 1.4 `pipelines/` vs `pipelines/test_adapter/` — 6对 Mock 文件

| 文件 | `pipelines/` 真实版本 | `pipelines/test_adapter/` Mock 版本 | 结论 |
|------|----------------------|-----------------------------------|------|
| `daily_report_pipeline.py` | 88行，真实业务逻辑，使用 `LLMRouter` + `PromptTemplate` 并发调用4个 LLM 任务 | 86行，`MockDailyReportPipeline`，返回固定假数据，无 LLM 调用 | **Mock 专用于测试** |
| `narrative_pipeline.py` | 65行，真实叙事分析 | 69行，`MockNarrativePipeline`，返回固定假数据 | **Mock 专用于测试** |
| `news_pipeline.py` | 126行，真实新闻抓取+翻译+LLM分析 | 77行，`MockNewsPipeline`，返回固定假数据 | **Mock 专用于测试** |
| `risk_pipeline.py` | 64行，真实风险分析 | 77行，`MockRiskPipeline`，返回固定假数据 | **Mock 专用于测试** |
| `scenario_pipeline.py` | 70行，真实情景分析 | 71行，`MockScenarioPipeline`，返回固定假数据 | **Mock 专用于测试** |
| `sentiment_pipeline.py` | 44行，真实情感分析 | 71行，`MockSentimentPipeline`，返回固定假数据 | **Mock 专用于测试** |

**引用关系：**
- `tests/test_pipelines.py` 显式导入 `fzq_ai.pipelines.test_adapter` 的 Mock 类
- `tests/test_orchestrator.py`、`tests/test_api.py`、`tests/test_llm_router.py` 等也引用 `test_adapter`
- `pyproject.toml` 中已配置 `"*/test_adapter/*"` 为忽略路径（暗示是测试专用）

**结论：** `test_adapter/` 是测试用的 Mock 适配层，被测试代码直接依赖。**当前不能直接删除**，需要先重构测试代码，将 Mock 逻辑替换为 pytest fixtures 或 unittest.mock，然后才能删除。

---

### 1.5 `llm/model_router.py` vs `core/model_router.py`

| 文件 | 内容 | 说明 |
|------|------|------|
| `src/fzq_ai/llm/model_router.py` | 55行，`ModelRouter` 类，Provider 初始化使用具体模型名（如 `GLMProvider("glm-4-flash")`） | 未被 `llm/__init__.py` 导出 |
| `src/fzq_ai/core/model_router.py` | 63行，`ModelRouter` 类，Provider 初始化使用零参数或 lazy init（如 `GLMProvider()`, `DeepSeekProvider(model="deepseek-chat")`） | 被 `core/` 顶层 bridge 引用？实际上 `core/` 顶层目录的 `model_router.py` 是 `src/fzq_ai/core/` 的 |

**关键发现：** 这两个文件**内容几乎完全相同**，仅 `__init__` 中 Provider 的构造参数有差异：
- `llm/model_router.py`: 所有 Provider 都传入具体 model 参数
- `core/model_router.py`: GLM/Qwen/Kimi 使用零参数，DeepSeek/OpenAI/Gemini 传入不同参数

**引用关系：**
- `src/fzq_ai/llm/__init__.py` 导出的是 `LLMRouter`, `Router`, `ModelSelector`，**未导出 `model_router.py` 的 `ModelRouter`**
- 无生产代码直接引用 `fzq_ai.llm.model_router` 或 `fzq_ai.core.model_router`（grep 未找到）

**结论：** 两者是同一概念的两个副本，内容高度重复。`core/model_router.py` 和 `llm/model_router.py` 应合并，或删除其中一个。由于 `llm/` 是 LLM 模块的主目录，建议保留 `llm/model_router.py` 并删除 `core/model_router.py`（因为 `core/` 已有 `llm_executor.py` 等，不重复存放路由逻辑）。

---

### 1.6 `llm/test_adapter/` vs `llm/router_v2/` — 完全不同

| 目录 | 内容 | 说明 |
|------|------|------|
| `llm/test_adapter/` | `MockLLMRouter`, `MockOpenAIClient`, `MockDeepSeekClient`, `MockGeminiClient` | 测试 Mock，被 `tests/test_llm_router.py` 引用 |
| `llm/router_v2/` | `RouterV2`, `TaskSelector`, `MetricsAdapter`, `rules.py`, `selectors.py`, `types.py` | 真实生产路由逻辑，基于规则+指标的智能调度 |

**结论：** 两者功能完全不同，不是重复。`test_adapter/` 是测试 Mock，`router_v2/` 是生产代码。`test_adapter/` 当前因测试依赖不能删除，但长期应重构。

---

### 1.7 其他重复/桥接文件

| 文件对 | 关系 | 建议 |
|--------|------|------|
| `core/intent_engine.py` → `src/fzq_ai/core/intent_engine.py` | 顶层 `core/intent_engine.py` 是 bridge：`from fzq_ai.core.intent_engine import *` | 保留作为顶层兼容入口（如果仍有旧代码引用），但 `core/` 目录本身应归档 |
| `core/task_router.py` → `src/fzq_ai/core/task_router.py` | 顶层 `core/task_router.py` 是 bridge：`from fzq_ai.core.task_router import *` | 同上 |
| `core/pipelines.py` → `src/fzq_ai/pipelines/` | 顶层 `core/pipelines.py` 是 bridge：`from fzq_ai.pipelines.base import BasePipeline; from fzq_ai.pipelines.registry import PipelineRegistry` | 同上 |
| `core/model_router.py` → `src/fzq_ai/core/model_router.py` | 顶层 `core/model_router.py` 和 `src/fzq_ai/core/model_router.py` 内容相同 | 顶层 `core/` 是旧版归档目录，其内容已迁移到 `src/fzq_ai/core/` |
| `entry/entry_service.py` → `src/fzq_ai/entry/entry_service.py` | 顶层 `entry/` 是旧版 V19，使用 `core.task_router`；`src/fzq_ai/entry/` 是新版 V19/V23 | 顶层 `entry/` 应归档 |
| `entry/entry_service_v23.py` → `src/fzq_ai/entry/entry_service_v23.py` | 两者内容高度相似（42行 vs 33行），`src/` 版本更精炼 | 顶层 `entry/` 应归档 |
| `app/entry_adapter.py` → `app/web_app.py` | `entry_adapter.py` 和 `web_app.py` 内容完全相同（都是 `EntryServiceV23` + FastAPI） | 两者是重复文件，`app/` 目录本身就是死目录 |

---

## 二、死代码 / 空文件清单

### 2.1 大小为 0 的 `__init__.py` 文件

| 文件 | 建议 |
|------|------|
| `app/__init__.py` | 删除（随 `app/` 目录一起归档） |
| `data/__init__.py` | 保留（`data/` 是数据目录） |
| `data/backups/__init__.py` | 保留 |
| `data/cache/__init__.py` | 保留 |
| `data/logs/__init__.py` | 保留 |
| `data/news/__init__.py` | 保留 |
| `data/output/__init__.py` | 保留 |
| `src/__init__.py` | 删除（顶层 `src/` 无实际作用） |
| `src/fzq_ai/api/__init__.py` | 删除（空包） |
| `src/fzq_ai/cache/__init__.py` | 删除（空包） |
| `src/fzq_ai/cli/__init__.py` | 删除（空包） |
| `src/fzq_ai/domain/__init__.py` | 删除（空包） |
| `src/fzq_ai/intel/__init__.py` | 删除（空包） |
| `src/fzq_ai/llm/orchestrator/__init__.py` | 删除（空包） |
| `src/fzq_ai/llm/orchestrator/diff/__init__.py` | 删除（空包） |
| `src/fzq_ai/llm/orchestrator/linter/__init__.py` | 删除（空包） |
| `src/fzq_ai/llm/orchestrator/recovery/__init__.py` | 删除（空包） |
| `src/fzq_ai/llm/router_v2/__init__.py` | 删除（空包） |
| `src/fzq_ai/logging/__init__.py` | 删除（空包） |
| `src/fzq_ai/metrics/__init__.py` | 删除（空包） |
| `src/fzq_ai/orchestrator/__init__.py` | 删除（空包） |
| `src/fzq_ai/prompts/__init__.py` | 删除（空包） |
| `src/fzq_ai/registry/__init__.py` | 保留（有注释说明，且被引用） |
| `src/fzq_ai/quality/__init__.py` | 检查是否为空 |
| `src/fzq_ai/storage/__init__.py` | 检查是否为空 |
| `src/fzq_ai/store/__init__.py` | 检查是否为空 |
| `src/fzq_ai/tools/__init__.py` | 检查是否为空 |
| `src/fzq_ai/utils/__init__.py` | 检查是否为空 |
| `tests/__init__.py` | 删除（空包） |

> **注意：** 空 `__init__.py` 在 Python 3.3+ 中不是必需的（PEP 420），但显式保留空文件有助于明确标记为 package。对于确实没有子模块导出需求的空包，可以删除以清理目录。

### 2.2 其他空文件（0字节）

| 文件 | 建议 |
|------|------|
| `src/fzq_ai/registry.py` | **删除**（空文件，已被 `registry/` 目录替代） |
| `stdout.txt` | **删除**（临时输出文件） |
| `src/fzq_ai/metrics/aggregator.py` | 检查是否为空 |
| `src/fzq_ai/logs/fzq_ai_20260630.log` | 归档或删除（旧日志） |

### 2.3 空测试文件（0字节）

| 文件 | 建议 |
|------|------|
| `tests/test_audit/test_prompt_linter.py` | 删除（空文件） |
| `tests/test_models/test_deepseek.py` | 删除（空文件） |
| `tests/test_models/test_kimi.py` | 删除（空文件） |
| `tests/test_models/test_qwen.py` | 删除（空文件） |
| `tests/test_pipelines/test_opinion.py` | 删除（空文件） |
| `tests/test_pipelines/test_policy.py` | 删除（空文件） |
| `tests/test_pipelines/test_risk.py` | 删除（空文件） |
| `tests/test_recovery/test_error_classifier.py` | 删除（空文件） |
| `tests/test_recovery/test_fallback_policy.py` | 删除（空文件） |
| `tests/test_recovery/test_repair_policy.py` | 删除（空文件） |
| `tests/test_recovery/test_retry_policy.py` | 删除（空文件） |
| `tests/test_router/test_router_v1.py` | 删除（空文件） |
| `tests/test_router/test_router_v2.py` | 删除（空文件） |
| `tests/test_router/test_task_selector.py` | 删除（空文件） |
| `tests/test_self_healing/test_field_filler.py` | 删除（空文件） |
| `tests/test_self_healing/test_json_repairer.py` | 检查是否为空 |
| `tests/test_self_healing/test_schema_repairer.py` | 删除（空文件） |
| `tests/test_self_healing/test_structure_fixer.py` | 删除（空文件） |

---

## 三、顶层死目录分析

### 3.1 `app/` 目录

| 文件 | 内容 | 状态 |
|------|------|------|
| `app/__init__.py` | 空 | 死代码 |
| `app/entry_adapter.py` | 93行，`EntryServiceV23`（FastAPI入口） | 与 `app/web_app.py` 完全重复 |
| `app/web_app.py` | 117行，FastAPI 应用，V23 版本 | 不被任何生产代码引用 |

**引用分析：**
- `main.py` 启动 `src.fzq_ai.api.app:app`，不引用 `app/web_app.py`
- `app_legacy.py` 也不引用 `app/web_app.py`
- 仅在 `archive/deprecated_v18/app/web_app.py` 中有 `from app.entry_adapter import ...`（这是归档代码）

**结论：** `app/` 目录是 **死目录**。其中 `web_app.py` 和 `entry_adapter.py` 内容虽然完整，但已完全被 `src/fzq_ai/api/app.py` 和 `src/fzq_ai/api/entry.py` 替代。**建议将 `app/` 整体移入 `archive/`。**

### 3.2 `core/` 目录

| 文件 | 内容 | 状态 |
|------|------|------|
| `core/__init__.py` | 1行：`# Core bridge package` | bridge |
| `core/intent_engine.py` | 3行：bridge 到 `fzq_ai.core.intent_engine` | bridge |
| `core/model_router.py` | 63行：与 `src/fzq_ai/core/model_router.py` 内容相同 | bridge + 重复 |
| `core/pipelines.py` | 3行：bridge 到 `fzq_ai.pipelines` | bridge |
| `core/task_router.py` | 3行：bridge 到 `fzq_ai.core.task_router` | bridge |

**引用分析：**
- 仅被 `entry/entry_service.py`（顶层旧版入口）引用：`from core.task_router import TaskRouter`
- 不被 `src/fzq_ai/` 下的任何生产代码引用

**结论：** `core/` 目录是 **顶层 bridge 目录**，目的是兼容旧版 import 路径。但 `entry/entry_service.py` 本身也是死代码，因此 `core/` 无人使用。**建议将 `core/` 和 `entry/` 一起移入 `archive/`。**

### 3.3 `entry/` 目录

| 文件 | 内容 | 状态 |
|------|------|------|
| `entry/__init__.py` | 1行：`# FZQ-AI Entry Layer (V19)` | 空 |
| `entry/entry_service.py` | 62行，V19 入口服务，使用 `core.task_router` | 旧版，引用顶层 `core/` |
| `entry/entry_service_v23.py` | 42行，V23 入口服务 | 与 `src/fzq_ai/entry/entry_service_v23.py` 重复 |

**引用分析：**
- 无生产代码引用 `entry/` 目录（grep 仅找到 `archive/deprecated_v18/` 中的引用）
- `src/fzq_ai/entry/` 是正式入口目录

**结论：** `entry/` 是 **死目录**，内容已被 `src/fzq_ai/entry/` 完全替代。**建议将 `entry/` 整体移入 `archive/`。**

### 3.4 顶层 `app/`、`core/`、`entry/` 与 `src/fzq_ai/` 的关系

```
app/                    → 死目录，内容已迁移到 src/fzq_ai/api/
├── web_app.py          → 与 src/fzq_ai/api/app.py 功能重复
└── entry_adapter.py    → 与 src/fzq_ai/api/entry.py 功能重复

core/                   → 死目录，内容已迁移到 src/fzq_ai/core/
├── intent_engine.py    → bridge 到 src/fzq_ai/core/intent_engine.py
├── model_router.py     → 与 src/fzq_ai/core/model_router.py 重复
├── pipelines.py        → bridge 到 src/fzq_ai/pipelines/
└── task_router.py      → bridge 到 src/fzq_ai/core/task_router.py

entry/                  → 死目录，内容已迁移到 src/fzq_ai/entry/
├── entry_service.py    → 旧版 V19，被 entry/entry_service_v23.py 替代
└── entry_service_v23.py → 与 src/fzq_ai/entry/entry_service_v23.py 重复
```

---

## 四、建议删除清单（按优先级）

### 🔴 高优先级（立即删除，无风险）

| 文件/目录 | 理由 |
|-----------|------|
| `src/fzq_ai/registry.py` | 空文件，已被 `src/fzq_ai/registry/` 目录替代 |
| `stdout.txt` | 临时输出文件 |
| `app/` 目录 | 死目录，功能已迁移到 `src/fzq_ai/api/` |
| `core/` 目录 | 死目录，功能已迁移到 `src/fzq_ai/core/` |
| `entry/` 目录 | 死目录，功能已迁移到 `src/fzq_ai/entry/` |
| `src/fzq_ai/agents/policy_brief_agent.py`（旧版） | 已被 `agents/tasks/policy_brief_agent.py` 替代，且 `agents/__init__.py` 不应再导出旧版 |
| `src/fzq_ai/agents/risk_scan_agent.py`（旧版） | 同上 |
| `src/fzq_ai/agents/multisource_merge_agent.py`（旧版） | 同上 |
| `src/fzq_ai/agents/opinion_landscape_agent.py`（旧版） | 同上 |
| `src/fzq_ai/agent_hub.py` | 无引用，功能疑似被 `src/fzq_ai/api/` 替代 |
| `src/fzq_ai/utils/agent_hub.py` | 无引用，依赖已废弃的旧版 agents |
| `src/fzq_ai/core/model_router.py` | 与 `src/fzq_ai/llm/model_router.py` 内容高度重复 |
| 所有 0 字节测试文件（见 2.3） | 空测试文件，无实际作用 |

### 🟡 中优先级（需确认后删除）

| 文件/目录 | 理由 |
|-----------|------|
| `src/fzq_ai/llm/model_router.py` | 如果确定 `core/model_router.py` 是主版本，则删除此副本；建议保留 `llm/` 版本，删除 `core/` 版本 |
| `src/fzq_ai/agents/__init__.py` | 当前导出旧版 agents，应改为导出 `tasks/` 版本或删除旧版导入 |
| 大量空 `__init__.py`（见 2.1） | 无子模块导出需求的空包可删除 |

### 🟢 低优先级（需重构后删除）

| 文件/目录 | 理由 |
|-----------|------|
| `src/fzq_ai/schemas/test_adapter/` | 被测试直接依赖，需先重构测试使用 pytest fixtures/mock |
| `src/fzq_ai/pipelines/test_adapter/` | 同上 |
| `src/fzq_ai/llm/test_adapter/` | 同上 |
| `src/fzq_ai/orchestrator/test_adapter/` | 同上 |

---

## 五、建议保留清单

| 文件/目录 | 保留理由 |
|-----------|----------|
| `src/fzq_ai/agents/tasks/` | 生产版本的智能体实现，被 `agents/registry.py` 注册 |
| `src/fzq_ai/agents/base.py` | V21 基类，定义 `AgentContext` / `AgentResult` / `BaseAgent` |
| `src/fzq_ai/agents/registry.py` | V23 统一注册中心，注册所有生产 agents |
| `src/fzq_ai/registry/` 目录 | 被 `unified_orchestrator.py` 引用，生产注册中心 |
| `src/fzq_ai/llm/router_v2/` | 生产路由逻辑，与 `test_adapter/` 无关 |
| `src/fzq_ai/pipelines/`（非 test_adapter） | 真实 Pipeline 实现，是核心业务逻辑 |
| `src/fzq_ai/core/`（非 model_router.py） | 生产核心：`intent_engine.py`, `task_router.py`, `llm_executor.py` |
| `src/fzq_ai/entry/` | 正式入口层，被 `api/app.py` 引用 |
| `src/fzq_ai/api/` | FastAPI 应用主入口，被 `main.py` 启动 |
| `archive/` | 已归档的旧版本，作为历史备份保留 |
| `tests/`（非空文件） | 有效测试代码，如 `test_api.py`, `test_llm_router.py`, `test_pipelines.py` 等 |

---

## 六、关键风险提醒

1. **旧版 agents 仍被导出：** `src/fzq_ai/agents/__init__.py` 导出旧版 `RiskScanAgent` 等，如果外部代码通过 `from fzq_ai.agents import RiskScanAgent` 引用，会拿到错误版本（旧版）。**建议立即修改 `__init__.py` 指向 `tasks/` 版本。**

2. **命名冲突：** `src/fzq_ai/registry/pipelines.py` 的 `PipelineRegistry` 与 `src/fzq_ai/pipelines/registry.py` 的 `PipelineRegistry` 同名但实现不同。`agents/tasks/` 的 agent 使用 `pipelines.registry.PipelineRegistry`，而 `unified_orchestrator.py` 使用 `registry.pipelines.global_registry`。这可能导致注册表不同步。

3. **ModelRouter 双副本：** `llm/model_router.py` 和 `core/model_router.py` 内容高度重复，维护时可能修改其中一个而遗漏另一个。

4. **测试依赖 test_adapter：** 当前测试代码直接依赖 `test_adapter/` 的 Mock 类，不能简单删除。建议重构测试使用 `unittest.mock` 或 `pytest-mock`，逐步消除 `test_adapter/` 目录。

5. **顶层死目录的 import 污染：** 如果 PYTHONPATH 包含项目根目录，旧代码可能意外导入 `app/`, `core/`, `entry/` 的死代码。建议尽快归档或删除。

---

> 报告生成完毕。建议按优先级分批次执行清理，每次清理后运行测试验证。
