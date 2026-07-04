# FZQ‑AI V24 Architecture Overview

> **Version**: V24 · **Status**: Production-Ready · **Tests**: 165/165

---

## 1. Layered Architecture

```
Layer 8 ▐  FRONTEND         React + TypeScript (schemaAdapter, entryService, Zustand)
Layer 7 ▐  ENTRY            FastAPI routes (/entry, /multi, /autonomy, /api/zh/*)
Layer 6 ▐  ORCHESTRATOR     V24 Orchestrator (AgentSelector → ExecutionBuilder)
Layer 5 ▐  AGENT DECA       Loop, StateMachine, Healing, Reflection, Planning,
         ▐  SYSTEM           Goals, Personality, Memory (+ MultiAgent)
Layer 4 ▐  LLM INTELLIGENCE Router (choose_model), Failover (3-tier), PromptEngine (13)
Layer 3 ▐  PROVIDERS        DeepSeek, GLM, Qwen, OpenAI, Gemini, Kimi, Moonshot
Layer 2 ▐  CIVILIZATION     Memory, Graph, Consensus (integrated in Entry→Orchestrator→Agent chain)
Layer 1 ▐  OBSERVABILITY    Structlog JSON, Tracing, Prometheus /metrics
Layer 0 ▐  INFRASTRUCTURE   Pydantic v2, Registry, Config, Schemas
```

---

## 2. Data Flow: Intent → Route → Pipeline → Model

```
User Input
    │
    ▼
[IntentEngine.classify()]          sync, keyword-match, 8 task types
    │ returns IntentResult
    ▼
[TaskRouter.route()]               async, pipeline lookup + fallback
    │
    ▼
[_call_pipeline()]                 sync/async bridge, parameter auto-adapt
    │
    ▼
[LLM Router.choose_model()]        9×2×2 routing table (task×lang×length×priority)
    │
    ▼
[call_llm()]                       failover: primary → same-family → cross-family → ultimate
    │
    ▼
[Provider.chat()]                  DeepSeek / GLM / Qwen / OpenAI / Gemini / Kimi
    │
    ▼
[wrap_response()]                  V24 contract: {execution: {...}, ui_schema: {...}, output: ...}
```

---

## 3. Agent Lifecycle

```
INIT → PLANNING → EXECUTING → REFLECTING → HEALING → COMPLETED
  ↑                    ↓           ↓          ↓         ↓
  └────────────────────┴───────────┴──────────┴─────────┘
                       ↺ ERROR → HEALING

Each state triggers:
  PLANNING    → PlanningEngine.decompose() + GoalEngine
  EXECUTING   → MemoryEngine + LLM Router + Failover
  REFLECTING  → ReflectionEngine (instant + deep)
  HEALING     → HealingEngine (memory, goals, plan, personality)
```

---

## 4. LLM Intelligent Routing

### Model Selection Table (excerpt)

| Task | zh | en | Long (>4000) | Priority |
|------|----|----|--------------|----------|
| `zh_risk_scan` | glm-4 | deepseek-chat | glm-4-flash (128K) | quality |
| `zh_policy_brief` | deepseek-chat | gpt-4o | deepseek-chat (64K) | quality |
| `news` | deepseek-chat | gpt-4o-mini | gpt-4o-mini (128K) | balanced |
| default | deepseek-chat | gpt-4o-mini | deepseek-chat | quality |

### Failover Chain

```
deepseek-chat → deepseek-reasoner (same-family)
              → glm-4-flash       (cross-family)
              → qwen-max          (cross-family)
              → gpt-4o-mini       (ultimate)
```

---

## 5. Civilization Layer

```
CivilizationEngine
├── civilization_builder.py    # build_default_civilization(), build_parliament()
├── civilization_engine.py     # CivilizationEngine — shared state, snapshot, lifecycle
└── __init__.py                # public exports
```

> The civilization layer has been simplified from 28 modules to 3 core modules (P0-3 cleanup).
> The deleted modules (parliament, consensus, evolution, federation, etc.) are archived in git history.

### Integration (P2)

The civilization layer is now **actively integrated** into the main production chain:

```
EntryServiceV24
  └── build_default_civilization()    # 3 agents: risk_analyst, policy_analyst, intelligence_officer
  └── passes civilization to ctx
      └── UnifiedOrchestratorV24.run_single()
            ├── civilization.remember(task, input)    # pre-execution memory
            ├── civilization.snapshot()               # plan awareness
            ├── NewsAgentV24.run()                    # agent execution
            └── civilization.remember(result)         # post-execution memory
            └── civilization._generate_consensus()    # decision consensus
      └── RouteResult.debug_info includes:
            └── civilization_trace[]   # per-stage trace
            └── civilization_consensus # voting result
```

**Imports** (`git grep -l "fzq_ai.civilization" src/`):
- `api/entry_service_v24.py` — initializes & injects CivilizationEngine
- `civilization/civilization_engine.py` — core engine
- `civilization/civilization_builder.py` — factory functions
- `civilization/__init__.py` — public API

**Tests**: `tests/test_civilization.py` (8 tests, covers engine + integration)

---

## 6. V24 API Contract

All endpoints return:

```json
{
  "execution": {
    "intent": {},
    "route": {"task_type": "zh_risk_scan"},
    "pipeline": "zh_risk_scan",
    "model": "deepseek-chat",
    "agent": "deepseek-risk",
    "timeline": [],
    "state_machine": {"current": "COMPLETED", "history": ["INIT","PLANNING","EXECUTING","REFLECTING","HEALING","COMPLETED"]},
    "trace_id": "uuid",
    "fallback_used": null,
    "success": true,
    "error": null
  },
  "ui_schema": {"blocks": [...]},
  "output": null
}
```

---

## 7. Observability Stack

| Component | Implementation | Output |
|-----------|---------------|--------|
| Logging | `utils/logger.py` (JSONFormatter) | `logs/fzq_ai_*.jsonl` |
| Tracing | `utils/tracing.py` (Tracer) | In-memory + optional LangFuse |
| Metrics | `utils/monitoring.py` (11 Prometheus metrics) | `GET /metrics` |
| Health | `GET /health` | `{"status":"ok","version":"24.0.0"}` |

---

## 8. Design Principles

1. **Pydantic v2 only** — 0 `@validator` / `class Config` / `orm_mode` residues
2. **Backward compatible** — V23 `/v23/entry` coexists with V24 `/entry`
3. **Failover by default** — all LLM calls go through 3-tier failover
4. **Personality-driven** — agent tone/style/risk_preference flows through PromptEngine + Router
5. **Stateful agents** — StateMachine tracks full lifecycle per agent
6. **Observable everywhere** — JSON logs + tracing + Prometheus on all critical paths
7. **Civilization-ready** — Federation API for cross-civ governance (V25 target)
