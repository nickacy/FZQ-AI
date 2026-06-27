FZQ‑AI Intelligence Dashboard

Multi‑Model Intelligence Analysis System · 新闻 · 舆情 · 风险 · 日报
一个由 DeepSeek / OpenAI / Gemini 三大模型驱动的多模型情报分析系统，
用于 新闻情报分析、舆情分析、风险扫描、每日报告生成、任务编排（Orchestrator）。

Designed for real‑world intelligence workflows, combining LLM reasoning, structured pipelines, and a clean Streamlit UI.

🌐 Features | 功能亮点
📰 新闻情报分析
输入主题 → 自动抓取新闻（可选）

自动摘要、提取事件、结构化输出

支持多模型交叉验证

📣 舆情分析
舆论情绪

叙事结构

关键传播节点

⚠️ 风险扫描
风险矩阵

事件链分析

自动生成风险提示

📅 每日报告生成
自动生成日报

可扩展为 PDF（未来版本）

🧠 多模型任务编排（Orchestrator）
输入一句自然语言

自动选择 Pipeline

自动选择模型（DeepSeek / OpenAI / Gemini）

自动执行任务链

🏗️ System Architecture | 系统架构
使用 Mermaid（GitHub 可直接渲染）：

mermaid
flowchart TD

    User[User / Analyst] --> UI[Streamlit UI]

    UI --> ORCH[Task Orchestrator<br/>任务编排器]

    ORCH --> NEWS[News Pipeline<br/>新闻情报分析]
    ORCH --> NARR[Narrative Pipeline<br/>叙事分析]
    ORCH --> RISK[Risk Pipeline<br/>风险扫描]
    ORCH --> DAILY[Daily Report Pipeline<br/>每日报告]

    NEWS --> LLM[LLM Router]
    NARR --> LLM
    RISK --> LLM
    DAILY --> LLM

    LLM --> DS[DeepSeek API]
    LLM --> OA[OpenAI API]
    LLM --> GM[Gemini API]

🚀 Installation | 安装
1. 克隆仓库
bash
git clone https://github.com/yourname/FZQ-AI.git
cd FZQ-AI
2. 安装依赖（Python 3.10+）
bash
pip install -r requirements.txt
# 或安装开发依赖
pip install -e ".[dev]"
3. 配置环境变量 .env
复制 .env.example 为 .env，并填入你的 API Keys：

Code
DEEPSEEK_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
NEWSAPI_KEY=your_key_here

# CORS 白名单（仅允许这些来源跨域访问）
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8501

# 运行环境：development / production / staging
# production 下错误信息不会暴露给客户端
ENV=development
▶️ Run UI | 启动界面
bash
streamlit run ui_app.py
▶️ Run API Server | 启动 API 服务
bash
uvicorn app:app --reload --port 8000
# 访问文档：http://localhost:8000/docs
# 健康检查：http://localhost:8000/health
# 版本信息：http://localhost:8000/version
📦 Project Structure | 项目结构
Code
FZQ-AI/
│
├── app.py                        # FastAPI 后端服务入口（v4.0.0，使用 lifespan）
├── main.py                       # 启动器（调用 Streamlit UI）
├── ui_app.py                     # Streamlit UI 主界面
│
├── requirements.txt              # Python 依赖
├── setup.py                      # 包安装配置
├── pyproject.toml                # 统一工具配置（Black/Ruff/mypy/pytest）
├── README.md                     # 项目说明文档（双语）
├── LICENSE                       # MIT License
├── .gitignore                    # 忽略文件
├── .env.example                  # 环境变量模板
│
├── tests/                        # 测试目录
│   ├── test_api.py               # API 测试
│   ├── test_news_pipeline.py     # 新闻 Pipeline 测试
│   ├── test_narrative.py         # 叙事分析测试
│   ├── test_risk.py              # 风险扫描测试
│   ├── test_daily_report.py      # 日报测试
│   ├── test_llm_router.py        # LLM 路由测试
│   ├── test_schemas.py           # Schema 测试
│   └── test_adapter/             # 测试适配器（mock 依赖）
│
├── src/fzq_ai/                   # 主代码包
│   ├── api/                      # API 端点
│   │   ├── __init__.py
│   │   ├── zh_endpoints.py       # 中文情报 API
│   │   └── metrics_endpoints.py  # 系统指标 API
│   │
│   ├── agents/                   # 智能体系统
│   │   ├── base.py
│   │   ├── registry.py
│   │   ├── orchestrator.py
│   │   ├── news_center_agent.py
│   │   ├── autonomy_agent.py
│   │   ├── alert_agent.py
│   │   ├── report_agent.py
│   │   ├── watchlist_agent.py
│   │   └── tasks/
│   │       └── policy_brief_agent.py
│   │
│   ├── cli/                      # 命令行工具
│   │   └── agent.py
│   │
│   ├── config/                   # 配置管理
│   │   ├── __init__.py           # 统一配置入口（加载 config.yaml）
│   │   ├── global_settings.py    # 全局设置（支持嵌套属性访问）
│   │   └── settings.yaml
│   │
│   ├── core/                     # 核心组件
│   │   ├── __init__.py
│   │   ├── config.py             # 全局配置模型
│   │   ├── llm_executor.py       # 统一 LLM 执行器
│   │   └── prompts.py            # Prompt 模板系统
│   │
│   ├── dashboard/                # Dashboard 组件
│   │   ├── dashboard.py
│   │   └── components/
│   │
│   ├── domain/                   # 领域模型
│   │   └── models.py
│   │
│   ├── intel/                    # 情报引擎
│   │   ├── news_intel_engine.py
│   │   ├── news_intel_service.py
│   │   ├── narrative_engine.py
│   │   ├── event_clustering.py
│   │   ├── translation_manager.py
│   │   ├── denoising_and_scoring.py
│   │   └── schemas.py
│   │
│   ├── llm/                      # LLM 层
│   │   ├── llm_router.py         # 多模型路由（fallback + 熔断）
│   │   ├── router.py             # 底层模型路由
│   │   ├── model_selector.py
│   │   ├── cache_redis.py
│   │   ├── providers/            # 各 Provider 实现
│   │   │   ├── deepseek_provider.py
│   │   │   ├── openai_provider.py
│   │   │   ├── gemini_provider.py
│   │   │   ├── qwen_provider.py
│   │   │   └── kimi_provider.py
│   │   └── test_adapter/         # 测试适配器（mock）
│   │       ├── __init__.py
│   │       └── llm_router.py
│   │
│   ├── logging/                  # 日志系统
│   │   └── logger.py
│   │
│   ├── metrics/                  # 性能指标
│   │   └── metrics_store.py
│   │
│   ├── orchestrator/             # 任务编排器
│   │   ├── task_orchestrator.py  # 主编排器
│   │   ├── daily_report_orchestrator.py
│   │   └── test_adapter/
│   │       ├── __init__.py
│   │       └── task_orchestrator.py
│   │
│   ├── pipelines/                # Pipeline 层
│   │   ├── news_pipeline.py
│   │   ├── narrative_pipeline.py
│   │   ├── risk_pipeline.py
│   │   ├── sentiment_pipeline.py
│   │   ├── scenario_pipeline.py
│   │   ├── daily_report_pipeline.py
│   │   ├── registry.py
│   │   ├── protocol.py
│   │   ├── base.py
│   │   └── test_adapter/         # 测试适配器（mock）
│   │       ├── __init__.py
│   │       ├── news_pipeline.py
│   │       ├── narrative_pipeline.py
│   │       ├── risk_pipeline.py
│   │       ├── sentiment_pipeline.py
│   │       ├── scenario_pipeline.py
│   │       └── daily_report_pipeline.py
│   │
│   ├── prompts/                  # Prompt 模板
│   │   └── news_intel_prompt.py
│   │
│   ├── quality/                  # 质量优化
│   │   ├── deepseek_struct_opt.py
│   │   ├── minimax.py
│   │   └── schemas.py
│   │
│   ├── schemas/                  # 数据模型
│   │   ├── __init__.py           # 统一导出所有 Schema
│   │   ├── core_models.py        # 核心数据模型（v13）
│   │   ├── base.py
│   │   ├── pipeline_output.py
│   │   └── validator.py
│   │
│   ├── store/                    # 数据存储
│   │   ├── intel_store.py
│   │   └── event_extractor.py
│   │
│   ├── tools/                    # 工具集
│   │   ├── news_fetcher.py
│   │   ├── translator.py
│   │   ├── generic_llm_tool.py
│   │   ├── weather_tool.py
│   │   ├── attractions_tool.py
│   │   ├── metro_checker.py
│   │   ├── route_planner.py
│   │   └── embedding.py
│   │
│   ├── ui/                       # UI 模块
│   │   └── __init__.py
│   │
│   └── utils/                    # 工具函数
│       ├── helpers.py
│       ├── json_formatter.py
│       ├── key_health.py
│       └── translation.py
│
└── .github/workflows/            # CI/CD
    └── python.yml
📡 API Endpoints | API 接口
GET /health
健康检查

GET /version
版本信息

POST /news/analyze
新闻情报分析

POST /narrative
叙事分析

POST /risk
风险扫描

POST /daily/generate
日报生成

POST /task/run
任务编排（自然语言 → 自动执行）

🧭 Roadmap | 路线图
✔️ 已完成
多模型路由器（DeepSeek / OpenAI / Gemini fallback）

Streamlit UI 主界面

FastAPI 后端（v4.0.0，lifespan + CORS 白名单）

Pipelines（新闻 / 舆情 / 风险 / 日报）

任务编排器（Task Orchestrator）

LLM 熔断器 + 负载均衡

配置管理统一（config.yaml + 环境变量）

Schema 验证（Minimax）

异步架构（async/await）

🔜 即将加入
新闻抓取（NewsAPI）

PDF 日报生成

UI 卡片式展示

Orchestrator 可视化

多模型并行推理

Redis 缓存集成

🛠️ Development | 开发
代码质量
使用 pre-commit hooks 自动格式化与检查：

bash
pre-commit install
pre-commit run --all-files
测试
bash
python -m pytest tests/ -v --tb=short
# 带覆盖率
python -m pytest tests/ --cov=src --cov-report=term-missing
🤝 Contributing | 贡献
欢迎提交 PR、Issue 或建议。
你可以：

添加新的 Pipeline

改进 UI

优化 LLM Router

添加新的数据源

📄 License
本项目采用 MIT License。
