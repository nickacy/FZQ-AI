# FZQ‑AI V24 旗舰版

跨文明个人情报官系统 · Cross-Civilization Personal Intelligence Officer

---

## 🏗️ Architecture

```
                            ╔══════════════════════╗
        Frontend ──────────▶║   FastAPI Entry Layer ║──▶ POST /entry /multi /autonomy
        (React + TS)        ╚══════════╤═══════════╝
                                       │
                            ╔══════════▼═══════════╗
                            ║   V24 Orchestrator   ║
                            ║   AgentSelector      ║──▶ classify → route → pipeline
                            ║   ExecutionBuilder   ║
                            ╚══════════╤═══════════╝
                                       │
              ┌────────────────────────┼────────────────────────┐
              │                        │                        │
    ╔═════════▼═════════╗   ╔══════════▼══════════╗   ╔═════════▼═════════╗
    ║   Agent Loop      ║   ║  LLM Router V24     ║   ║  Civilization    ║
    ║   StateMachine    ║   ║  choose_model()     ║   ║  Parliament      ║
    ║   Planning        ║   ║  call_llm()         ║   ║  Consensus       ║
    ║   Reflection      ║   ║  Failover (3-tier)  ║   ║  KnowledgeGraph  ║
    ║   Healing         ║   ║  PromptEngine (13)  ║   ║  Evolution       ║
    ║   Memory          ║   ╚══════════╤══════════╝   ╚═════════╤═════════╝
    ║   Personality     ║              │                        │
    ║   Goals           ║   ╔══════════▼══════════╗             │
    ╚═══════════════════╝   ║  Providers          ║             │
                            ║  DeepSeek GLM Qwen  ║             │
                            ║  OpenAI  Gemini Kimi║             │
                            ╚═════════════════════╝             │
                                       │                        │
                            ╔══════════▼════════════════════════▼══╗
                            ║   Observability                     ║
                            ║   Structlog JSON · Tracing          ║
                            ║   Prometheus Metrics · /metrics     ║
                            ╚═════════════════════════════════════╝
```

---

## 🚀 Quick Start

```bash
git clone https://github.com/nickacy/FZQ-AI
cd FZQ-AI
pip install -r requirements.txt
cp .env.example .env       # edit with your API keys
python main.py              # starts FastAPI on :8000
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/entry` | POST | Single-agent execution (`{"input": "..."}`) |
| `/multi` | POST | Multi-agent collaboration |
| `/autonomy` | POST | Autonomous agent loop |
| `/api/zh/risk_scan` | POST | Chinese risk scan pipeline |
| `/api/zh/policy_brief` | POST | Chinese policy brief pipeline |
| `/api/zh/opinion_landscape` | POST | Chinese opinion landscape |
| `/api/zh/multisource_merge` | POST | Chinese multi-source merge |
| `/v23/entry` | POST | V23 backward-compatible entry |
| `/metrics` | GET | Prometheus metrics |
| `/health` | GET | Health check |

### Example

```bash
curl -X POST http://127.0.0.1:8000/entry \
  -H "Content-Type: application/json" \
  -d '{"input":"分析金融风险","languages":["zh"]}'
```

Response (V24 contract):
```json
{
  "execution": {
    "intent": {}, "route": {"task_type":"zh_risk_scan"},
    "pipeline": "zh_risk_scan", "model": "deepseek-chat", "agent": "deepseek-risk",
    "timeline": [], "state_machine": {"current":"COMPLETED","history":["INIT","PLANNING","EXECUTING","REFLECTING","HEALING","COMPLETED"]},
    "trace_id": "...", "fallback_used": null
  },
  "ui_schema": {"blocks": [...]},
  "output": null
}
```

## 🧪 Testing

```bash
python -m pytest tests/ -v
# 182 passed, 1 warning
```

## 📊 Key Metrics

| Metric | Value |
|--------|-------|
| Backend tests | 182/182 |
| TypeScript errors | 0 |
| Python files | 352 |
| Classes | 432 |
| Functions | 1,173 |
| Supported LLMs | 7 (DeepSeek, GLM, Qwen, OpenAI, Gemini, Kimi, Moonshot) |
| Agent dimensions | 8 (Memory, Personality, Goals, Planning, Reflection, Healing, StateMachine, Loop) |
| Civilization modules | 54 (Parliament, Consensus, KnowledgeGraph, Evolution, etc.) |
| Prompt templates | 13 |

---

## 📂 Module Map

```
src/fzq_ai/
├── api/             FastAPI entry layer (V23 + V24 routes)
├── core/            IntentEngine + TaskRouter + LLMExecutor
├── llm/             Router, Failover, PromptEngine, Providers
├── agents/          BaseAgent + MultiAgent + V24 agents
├── orchestrator/    TaskOrchestrator + AgentSelector + ExecutionBuilder
├── pipelines/       zh_risk_scan, zh_policy_brief, news, etc.
├── civilization/    Parliament, Consensus, KnowledgeGraph, Evolution, Federation
├── schemas/         Pydantic v2 DTOs (core_models, route, validator)
├── registry/        Unified Agent Registry (7 agents)
├── utils/           Memory, Personality, Goals, Planning, Reflection, Healing,
│                    StateMachine, Loop, Tracing, Monitoring, Logger, AsyncManager
├── config/          ModernConfig + GlobalSettings (YAML + env)
├── metrics/         EnhancedMetrics (Prometheus-compatible)
├── quality/         DeepSeek struct optimizer + Minimax validator
├── prompts/         Prompt templates (zh + en)
├── tools/           Translator, NewsFetcher, Embedding, etc.
└── ui/              UISchema definitions
```
