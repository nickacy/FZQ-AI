# FZQ‑AI 系统架构总览 (V24)

> **版本**：V24 · **状态**：生产就绪 · **最后更新**：2026-07-03
> 与根目录 `ARCHITECTURE_OVERVIEW.md` 保持一致（双语版）。
> 历史 V19 中文版本（含 v6/v7/v8 路线图、`real/` 双层目录、`task_registry/`）已归档于 `archive/`。

---

## 1. 分层架构 (Layered Architecture)

```
Layer 8 ▐  FRONTEND         React + TypeScript (schemaAdapter, entryService, Zustand)
Layer 7 ▐  ENTRY            FastAPI routes (/entry, /multi, /autonomy, /api/zh/*)
Layer 6 ▐  ORCHESTRATOR     V24 Orchestrator (AgentSelector → ExecutionBuilder)
Layer 5 ▐  AGENT DECA       Loop, StateMachine, Healing, Reflection, Planning,
          ▐  SYSTEM         Goals, Personality, Memory (+ MultiAgent)
Layer 4 ▐  LLM INTELLIGENCE Router (choose_model), Failover (3-tier), PromptEngine (13)
Layer 3 ▐  PROVIDERS        DeepSeek, GLM, Qwen, OpenAI, Gemini, Kimi, Moonshot
Layer 2 ▐  CIVILIZATION     Parliament, Consensus, KnowledgeGraph, Evolution, Federation
Layer 1 ▐  OBSERVABILITY    Structlog JSON, Tracing, Prometheus /metrics
Layer 0 ▐  INFRASTRUCTURE   Pydantic v2, Registry, Config, Schemas
```

> 详细模块树、模块依赖、数据流、Agent 生命周期与 LLM 智能路由表，参见根目录 `ARCHITECTURE_OVERVIEW.md`（内容更完整，含架构图）。

---

## 2. 入口路由表 (V24 兼容层)

| 端点 | 版本 | 用途 |
|------|------|------|
| `/entry` | V24 | 单智能体执行 |
| `/multi` | V24 | 多智能体协作 |
| `/autonomy` | V24 | 自治智能体循环 |
| `/api/zh/policy_brief` | V24 | 中文政策简报 |
| `/api/zh/risk_scan` | V24 | 中文风险扫描 |
| `/api/zh/opinion_landscape` | V24 | 中文舆论版图 |
| `/api/zh/multisource_merge` | V24 | 中文多源合并 |
| `/api/v1/entry` | V24 (frontend) | 前端契约入口 |
| `/v23/entry` | V23 (legacy) | V23 兼容入口 |
| `/metrics` | observability | Prometheus metrics |
| `/health` | observability | Health check |

> 历史 V19 顶层模块图（含 `real/` 与 `task_registry/`）已被本版本淘汰，参见 `archive/` 与 `docs/audits/REAUDIT_REPORT_20250703.md`。

---

## 3. 文档地图

| 文档 | 用途 |
|------|------|
| `API_GUIDE.md` | REST API 用法 |
| `DATA_FLOW_PIPELINES.md` | Pipeline 数据流细节 |
| `ENTRY_FLOW.md` / `ENTRY_PROTOCOL.md` / `ENTRY_SCHEMA.md` | V24 入口层三件套 |
| `LLM_CALL_GRAPH.md` | LLM 调用图 |
| `METRICS_AND_OBSERVABILITY.md` | 监控/Prometheus |
| `MODULE_DEPENDENCIES.md` | 模块依赖图 |
| `NEWS_INTAKE_SYSTEM.md` | News 抓取系统 |
| `PROMPT_SYSTEM.md` | Prompt 模板系统 |
| `REGION_LANGUAGE_LOGIC.md` | 区域/语言逻辑 |
| `SCHEMAS_MAP.md` | Pydantic Schema 地图 |
| `glossary.md` | 术语表 |
| `audits/` | 历史审计报告归档 |

---

*本文件是 V24 双语版本；根目录 `ARCHITECTURE_OVERVIEW.md` 是英文主版。两者保持同步。*
