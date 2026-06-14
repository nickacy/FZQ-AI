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
📸 Screenshots | 系统截图
（你已提供 2 张截图，README 中将这样展示）

1. 系统首页 Dashboard
FZQ‑AI Intelligence Dashboard 主界面

（你稍后上传图片，我会帮你插入 Markdown 图片链接）

2. 新闻情报分析模块
输入主题 → 自动分析 → 结构化输出

（你稍后上传图片，我会帮你插入 Markdown 图片链接）

🚀 Installation | 安装
1. 克隆仓库
bash
git clone https://github.com/yourname/FZQ-AI.git
cd FZQ-AI
2. 安装依赖（Python 3.11）
bash
pip install -r requirements.txt
3. 配置环境变量 .env
Code
DEEPSEEK_API_KEY=
OPENAI_API_KEY=
GEMINI_API_KEY=
DEFAULT_MODEL=deepseek
NEWSAPI_KEY=
▶️ Run UI | 启动界面
bash
streamlit run ui_app.py
▶️ Run API Server | 启动 API 服务
bash
uvicorn api_server:app --reload --port 8000
📦 Project Structure | 项目结构（超详细版）
Code
FZQ-AI/
│
├── api_server.py                # FastAPI 后端服务入口
├── main.py                      # 启动器（调用 Streamlit）
├── ui_app.py                    # Streamlit UI 主界面
│
├── requirements.txt             # Python 依赖
├── README.md                    # 项目说明文档（双语）
├── LICENSE                      # MIT License
├── .gitignore                   # 忽略文件
│
├── tests/
│   └── test_news_pipeline.py    # 新闻 Pipeline 单元测试
│
├── fzq_ai/
│   ├── pipelines/
│   │   ├── news_pipeline.py         # 新闻情报分析
│   │   ├── narrative_pipeline.py    # 叙事分析
│   │   ├── risk_pipeline.py         # 风险扫描
│   │   └── daily_report_pipeline.py # 每日报告
│   │
│   ├── orchestrator/
│   │   └── task_orchestrator.py     # 自然语言任务编排器
│   │
│   ├── llm/
│   │   ├── llm_router.py            # 多模型路由器
│   │   ├── deepseek_client.py
│   │   ├── openai_client.py
│   │   └── gemini_client.py
│   │
│   ├── tools/
│   │   └── utils.py                 # 工具函数
│   │
│   ├── logging/
│   │   └── logger.py                # 日志系统
│   │
│   └── metrics/
│       └── metrics.py               # Pipeline 性能指标
📡 API Endpoints | API 接口
/news/analyze
新闻情报分析

/risk/scan
风险扫描

/daily/generate
日报生成

/task/run
任务编排（自然语言 → 自动执行）

🧭 Roadmap | 路线图
✔ 已完成
多模型路由器

Streamlit UI

FastAPI 后端

Pipelines（新闻 / 舆情 / 风险 / 日报）

任务编排器

GitHub 仓库清理

依赖管理（Python 3.11）

🔜 即将加入
新闻抓取（NewsAPI）

PDF 日报生成

UI 卡片式展示

Orchestrator 可视化

多模型并行推理

🤝 Contributing | 贡献
欢迎提交 PR、Issue 或建议。
你可以：

添加新的 Pipeline

改进 UI

优化 LLM Router

添加新的数据源

📄 License
本项目采用 MIT License。