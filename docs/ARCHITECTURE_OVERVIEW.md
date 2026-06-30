# FZQ-AI 系统架构总览

> 版本：V19 · 状态：生产就绪
> 最后更新：2026年
> 范围：覆盖 v6（基础架构）、v7（JSON鲁棒性+并发）、v8（全球搜索+intake）全部功能

---

## 1. 顶层架构（12个模块）

```
fzq_ai/
├── schemas/           ← 数据契约层
│   ├── real/          ← Real System（生产使用）
│   └── test_adapter/  ← Test Adapter Layer（pytest 测试用）
├── llm/               ← LLM 路由与多提供商管理
│   ├── real/          ← 真实 LLM 客户端（OpenAI/DeepSeek/Gemini）
│   └── test_adapter/  ← Mock 适配器
├── pipelines/         ← 业务管道层
│   ├── real/          ← 真实管道（NewsPipeline v8）
│   └── test_adapter/  ← Mock 管道适配器
├── orchestrator/      ← 任务编排调度
│   ├── real/          ← 真实编排器
│   └── test_adapter/  ← Mock 编排器适配器
├── task_registry/     ← 任务注册与发现
│   ├── real/          ← 真实注册中心
│   └── test_adapter/  ← Mock 注册中心
├── tools/             ← 工具层（新闻抓取、翻译等）
├── utils/             ← 通用工具（helpers、formatter）
├── core/              ← 核心系统（prompts、config）
├── agents/            ← 智能体层（预留）
├── ui/                ← 用户界面（预留）
└── dashboard/         ← 仪表盘（预留）
```

---

## 2. 模块职责一句话

| 模块 | Real System | Test Adapter Layer | 一句话职责 |
|------|-------------|-------------------|-----------|
| `schemas` | `real/__init__.py` | `test_adapter/__init__.py` | 定义所有 Pydantic 数据模型（20+ 模型，统一数据契约） |
| `llm` | `llm_router.py` + `openai_client.py` / `deepseek_client.py` / `gemini_client.py` | `llm_router.py` | 多提供商 LLM 路由，带熔断器、负载均衡、fallback 链 |
| `pipelines` | `news_pipeline.py` | `news_pipeline.py` | 新闻管道：翻译 → 多维度分析（叙事/风险/情感/情景） |
| `orchestrator` | `task_orchestrator.py` | `task_orchestrator.py` | 任务编排：调度、生命周期管理、定时执行 |
| `task_registry` | `registry.py` | `registry.py` | 任务注册中心：发现、注册、元数据管理 |
| `tools` | `news_fetcher.py` / `translator.py` | — | 新闻抓取器（v8 全球多源）+ 翻译器（v8 多语言） |
| `utils` | `helpers.py` / `formatter.py` | — | 通用工具：ID生成、格式化输出 |
| `core` | `prompts.py` / `config.py` | — | Prompt 模板系统（v8 共9个模板）+ 配置管理 |
| `agents` | — | — | **预留**：智能体协调层（v10 扩展） |
| `ui` | — | — | **预留**：前端界面（v10 扩展） |
| `dashboard` | — | — | **预留**：数据仪表盘（v10 扩展） |

---

## 3. 版本增强路线图

### v6（基础架构）
- 创建完整的双层次架构（Real + Test Adapter）
- 实现 20+ Pydantic Schema 模型
- 实现 LLMRouter 多提供商路由（OpenAI → DeepSeek → Gemini fallback）
- 实现基础 NewsPipeline（翻译 + 4 维度分析）
- 88 个测试全部通过

### v7（JSON 鲁棒性 + 并发）
- **`_safe_json_parse_v2()`** — 增强 JSON 解析：
  - 提取多 JSON 块，选择字段最多的
  - 修复单引号、尾逗号、BOM、HTML 实体
  - 处理混入自然语言的输出
- **字段类型安全提取** — `_safe_str()`, `_safe_float()`, `_safe_str_list()`, `_safe_enum()`
- **翻译模块增强** — 错误记录、fallback_error 标记、完整元数据
- **并发执行增强** — `asyncio.Semaphore` + `asyncio.gather`，异常隔离
- **Prompt 模板增强** — 添加严格 JSON 输出指令（4 条强制指令）
- **LLM 调用增强** — fallback 链 + latency 记录 + provider_used 字段

### v8（全球搜索 + 跨区域跨语言 Intake）
- **NewsFetcher v8** — 全球情报级多源抓取：
  - 5 类来源：RSS（30+ 源）、Google News RSS、Bing News RSS、NewsAPI、GDELT
  - 多语言：17 种语言自动检测 + 按语言选择源
  - 多区域：16 个 topic-region 映射
  - 议题扩展：`expand_topic_keywords()` — 规则 + LLM
  - 相关性过滤：`filter_by_relevance()` — LLM 批量评分
  - 去重：SHA-256 hash
  - 平衡报告：`compute_balance_report()` — 区域/语言/来源分布 + 平衡度评分
- **Translator v8** — 多语言翻译器：
  - 17 种语言自动检测（Unicode 范围）
  - 中英核心 + 阿/法/西/俄/日/韩 fallback
  - LLM 翻译质量评分
- **NewsPipeline v8** — Intake 增强：
  - `intake_from_topic()` — topic → 多源抓取 → 过滤 → 平衡报告 → PipelineInput
  - `compute_balance_report()` — 基于现有 items 计算平衡
  - `expand_topic_keywords()` / `infer_regions()` / `infer_languages()`
- **Prompt 模板新增** — 4 个 v8 模板（TOPIC_EXPANSION、REGION_CLASSIFICATION、LANGUAGE_CLASSIFICATION、NEWS_RELEVANCE_FILTER）

---

## 4. 关键设计决策

### 双层次架构（Dual-Layer）
- **Real System**：生产代码，直接调用真实 LLM 和外部 API
- **Test Adapter Layer**：Mock 实现，所有返回值带默认值，无需外部依赖即可运行测试
- **设计意图**：测试可以在 CI 环境中运行，无需真实 API key；Real System 在部署环境中运行

### 为什么 v8 的 NewsFetcher 不依赖外部 ORM/DB
- 所有新闻数据通过内存 Pipeline 流转，不持久化
- 意图是：新闻作为"情报流"，实时处理、实时分析、实时报告，不存储
- 如果需要持久化，可以在 v10 中扩展 `core/storage.py`

### 为什么使用 `aiohttp` 而不是 `requests`
- 全栈异步设计（async/await）
- 并发抓取和并发 LLM 调用是核心性能瓶颈
- `requests` 会阻塞事件循环

---

## 5. 文件树（核心文件）

```
fzq_ai/
├── schemas/
│   ├── real/__init__.py              ← 20+ Pydantic 模型（v6 修复字段后）
│   ├── test_adapter/__init__.py      ← 与 real 同结构，带 mock 默认值
│   ├── __init__.py
│   └── test_adapter/__init__.py
├── llm/
│   ├── real/
│   │   ├── llm_router.py             ← 多提供商路由 + 熔断器 + 负载均衡
│   │   ├── openai_client.py
│   │   ├── deepseek_client.py
│   │   └── gemini_client.py
│   └── test_adapter/
│       └── llm_router.py             ← Mock 路由
├── pipelines/
│   ├── real/
│   │   └── news_pipeline.py          ← v8 完整版（723 行）
│   └── test_adapter/
│       └── news_pipeline.py          ← Mock 管道
├── orchestrator/
│   ├── real/task_orchestrator.py
│   └── test_adapter/task_orchestrator.py
├── task_registry/
│   ├── real/registry.py
│   └── test_adapter/registry.py
├── tools/
│   ├── news_fetcher.py               ← v8 全球情报级（768 行）
│   └── translator.py                 ← v8 多语言（~280 行）
├── utils/
│   ├── helpers.py
│   └── formatter.py
├── core/
│   ├── prompts.py                    ← v8 共 9 个模板（~300 行）
│   └── config.py
├── agents/
│   ├── __init__.py
│   └── news_agent.py
├── ui/
│   └── __init__.py
└── dashboard/
    └── __init__.py
```

---

## 6. 测试覆盖

- **6 个测试文件**：`test_api.py`, `test_formatter.py`, `test_llm_router.py`, `test_orchestrator.py`, `test_pipelines.py`, `test_schemas.py`
- **88 个测试**：全部通过，覆盖 schemas、API、格式化、LLM 路由、管道、编排器
- **测试策略**：测试使用 Test Adapter Layer，无需真实 API key

---

*文档结束 — 配合 `MODULE_DEPENDENCIES.md` 和 `DATA_FLOW_PIPELINES.md` 阅读*
