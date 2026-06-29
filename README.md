# FZQ-AI

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**FZQ-AI** 是一款多模型中文情报分析系统，支持政策简报、风险扫描、舆情版图、多源合并四大中文情报任务，同时涵盖新闻、叙事、情感、情景、日报等通用分析维度。

> 版本：V15.0.0 | 状态：持续迭代

---

## 功能特性

- **中文情报四件套**：政策简报、风险扫描、舆情版图、多源合并
- **通用分析维度**：新闻、叙事、情感、情景、日报
- **多模型路由**：支持 OpenAI、DeepSeek、Gemini、GLM、Kimi、Qwen 等 6 个提供商，自动 fallback
- **Agent 编排**：多角色 Agent（政策、风险、舆情、报告、调度等）+ AgentHub 统一调度
- **可观测性**：内置指标采集（延迟、Token、Fallback 率）+ 结构化日志
- **双语支持**：UI 与 API 支持中文/英文切换

---

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入至少一个 LLM API 密钥
```

### 启动 API 服务

```bash
python main.py
# 或
uvicorn src.fzq_ai.api.app:app --reload --port 8000
```

API 文档：http://localhost:8000/docs

### 启动 Web UI（Streamlit）

```bash
streamlit run src/fzq_ai/ui/web_app.py --server.port=8501
```

---

## 架构概览

```
FZQ-AI V15.0.0
├── src/fzq_ai/
│   ├── api/              # FastAPI 入口（/api/zh/*, /health, /metrics）
│   ├── agents/           # 多角色 Agent + AgentHub
│   ├── core/             # 意图引擎、任务路由、LLM 执行器
│   ├── llm/              # LLMRouter + 6 个 Provider + Orchestrator
│   ├── pipelines/        # 8+ Pipeline（新闻、叙事、风险、情感、情景、日报 + 4 个中文）
│   ├── schemas/          # Pydantic 模型（核心模型 + 中文任务模型）
│   ├── prompts/          # 提示模板系统
│   ├── tools/            # 新闻获取、翻译、RSS 等工具
│   ├── dashboard/        # 监控仪表盘组件
│   └── ui/               # Streamlit Web UI（主题 + i18n + 组件）
├── configs/              # 配置文件（zh_tasks.yaml 等）
├── docs/                 # 架构文档、审计报告
├── tests/                # 测试套件
└── main.py               # 统一入口
```

---

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | `your_key_here` |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | `your_key_here` |
| `GEMINI_API_KEY` | Google Gemini API 密钥 | `your_key_here` |
| `GLM_API_KEY` | 智谱 GLM API 密钥 | `your_key_here` |
| `KIMI_API_KEY` | Moonshot Kimi API 密钥 | `your_key_here` |
| `QWEN_API_KEY` | 阿里通义千问 API 密钥 | `your_key_here` |
| `ALLOWED_ORIGINS` | CORS 白名单 | `http://localhost:3000,http://localhost:8501` |

---

## 文档

- [架构总览](docs/ARCHITECTURE_OVERVIEW.md)
- [数据流与 Pipeline](docs/DATA_FLOW_PIPELINES.md)
- [Schema 映射](docs/SCHEMAS_MAP.md)
- [Prompt 系统](docs/PROMPT_SYSTEM.md)
- [LLM 调用图](docs/LLM_CALL_GRAPH.md)
- [指标与可观测性](docs/METRICS_AND_OBSERVABILITY.md)
- [模块依赖](docs/MODULE_DEPENDENCIES.md)

---

## 许可证

MIT License — 详见 [LICENSE](LICENSE)。
