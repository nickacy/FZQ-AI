# FZQ-AI 模块依赖关系

> 版本：v9 · 状态：审计准备版

---

## 1. `pipelines.real.news_pipeline` 依赖链

```
news_pipeline.py
  ├── schemas.real               ← 20+ Pydantic 模型（硬依赖）
  │   ├── PipelineInput
  │   ├── PipelineOutput
  │   ├── PipelineMetrics
  │   ├── RawNewsItem
  │   ├── TranslatedNewsItem
  │   ├── MultiDimensionAnalysis
  │   ├── NarrativeAnalysis, RiskAnalysis, SentimentAnalysis, ScenarioAnalysis
  │   ├── RiskFactor, RiskLevel, SentimentLabel, ScenarioProjection
  │   ├── ModelProvider, LLMRequest, LanguageCode, AnalysisDimension, RegionCode
  │   └── FallbackRecord
  ├── llm.real.llm_router        ← LLM 路由（硬依赖）
  │   └── LLMRouter.generate()   ← 核心调用入口
  ├── core.prompts               ← Prompt 模板（硬依赖）
  │   └── PromptTemplates.render() + 9 个模板常量
  ├── tools.news_fetcher         ← v8 新增（可选依赖）
  │   └── NewsFetcher（intake_from_topic 使用）
  └── tools.translator           ← v8 新增（可选依赖）
      └── Translator（translate 质量评分使用）
```

| 依赖 | 类型 | 说明 |
|------|------|------|
| `schemas.real` | 硬依赖 | 所有数据模型定义，无此无法运行 |
| `llm.real.llm_router` | 硬依赖 | 所有 LLM 调用必须通过此路由 |
| `core.prompts` | 硬依赖 | 所有 prompt 模板集中管理 |
| `tools.news_fetcher` | 可选 | 仅 `intake_from_topic()` 使用，不传则使用已有 items |
| `tools.translator` | 可选 | 仅 `_score_translation_quality()` 使用，不传则使用 simple fallback |

---

## 2. `llm.real.llm_router` 依赖链

```
llm_router.py
  ├── schemas.real               ← LLMRequest, LLMResponse, RouterConfig 等
  ├── llm.real.openai_client      ← OpenAIClient（可选，需 api_key）
  │   └── OpenAIClient.generate()
  ├── llm.real.deepseek_client   ← DeepSeekClient（可选，需 api_key）
  │   └── DeepSeekClient.generate()
  └── llm.real.gemini_client     ← GeminiClient（可选，需 api_key）
      └── GeminiClient.generate()
```

| Provider | 依赖类型 | 说明 |
|----------|----------|------|
| OpenAIClient | 可选 | 需 `api_key`，无 key 则跳过该提供商 |
| DeepSeekClient | 可选 | 需 `api_key`，默认 URL: `https://api.deepseek.com` |
| GeminiClient | 可选 | 需 `api_key`，默认 URL: `https://generativelanguage.googleapis.com/v1beta` |
| **Fallback 链** | 自动 | OPENAI → DEEPSEEK → GEMINI，按 `config.fallback_chain` 顺序 |

**关键设计**：
- 每个提供商独立配置（`ProviderConfig`），可单独启用/禁用
- 熔断器（Circuit Breaker）独立：每个提供商有自己的失败计数和超时
- 负载均衡：支持 `priority` / `round_robin` / `least_latency` 三种策略

---

## 3. `tools.news_fetcher` 依赖链

```
news_fetcher.py
  ├── schemas.real               ← NewsSource, RawNewsItem, LanguageCode, RegionCode, LLMRequest, ModelProvider
  ├── core.prompts               ← TOPIC_EXPANSION_V1, NEWS_RELEVANCE_FILTER_V1
  ├── llm.real.llm_router        ← 可选，仅用于 topic 扩展和相关性过滤
  ├── aiohttp                    ← 外部依赖（硬依赖，HTTP 请求）
  ├── xml.etree.ElementTree     ← 外部依赖（硬依赖，RSS 解析）
  └── fzq_ai.utils.helpers      ← generate_id（硬依赖）
```

| 外部服务 | 依赖类型 | 说明 |
|----------|----------|------|
| RSS 源（30+） | 硬依赖 | 通过 `aiohttp` 抓取，但单个源失败不影响整体 |
| Google News RSS | 可选 | 通过 `aiohttp` 抓取，不需要 API key |
| Bing News RSS | 可选 | 通过 `aiohttp` 抓取，不需要 API key |
| NewsAPI | 可选 | 需 `newsapi_key`（`v2/everything` endpoint），不配置则跳过 |
| GDELT | 可选 | 通过 `aiohttp` 抓取，不需要 API key |
| LLM Router | 可选 | 仅用于 `expand_topic_keywords()` 和 `filter_by_relevance()` |

**容错设计**：
- 每个源独立失败，不影响其他源
- `fetch_multi_source()` 使用 `asyncio.gather(return_exceptions=True)` 隔离失败
- 去重机制（SHA-256）在合并阶段执行，不依赖外部服务

---

## 4. `tools.translator` 依赖链

```
translator.py
  ├── schemas.real               ← LanguageCode, ModelProvider, LLMRequest
  ├── core.prompts               ← TRANSLATION_V1
  ├── llm.real.llm_router        ← 可选，用于 LLM 翻译和质量评分
  └── re                         ← 外部依赖（硬依赖，Unicode 范围检测）
```

| 外部服务 | 依赖类型 | 说明 |
|----------|----------|------|
| LLM Router | 可选 | 有则使用 LLM 翻译 + 质量评分；无则使用 simple fallback |

---

## 5. `core.prompts` 依赖链

```
prompts.py
  └── 无外部依赖（纯字符串模板）
```

| 依赖 | 类型 | 说明 |
|------|------|------|
| 无 | — | 所有模板是 `str` 常量，`render()` 是静态方法，不依赖外部模块 |

---

## 6. `utils.helpers` 和 `utils.formatter` 依赖链

```
helpers.py
  └── 无外部依赖（纯工具函数）

formatter.py
  ├── schemas.real               ← 用于格式化输出
  └── typing                     ← 标准库
```

---

## 7. 依赖矩阵汇总

| 被依赖模块 | 依赖者 |
|-----------|--------|
| `schemas.real` | `news_pipeline`, `llm_router`, `news_fetcher`, `translator`, `formatter`, `task_orchestrator`, `registry` |
| `llm.real.llm_router` | `news_pipeline`, `news_fetcher`, `translator` |
| `core.prompts` | `news_pipeline`, `news_fetcher`, `translator` |
| `tools.news_fetcher` | `news_pipeline`（可选） |
| `tools.translator` | `news_pipeline`（可选） |
| `utils.helpers` | `news_fetcher` |
| `utils.formatter` | 测试 + 预留 UI |

---

## 8. 外部依赖包（requirements.txt）

| 包名 | 版本要求 | 用途 | 是否必需 |
|------|----------|------|----------|
| `pydantic` | ^2.0 | 数据模型验证 | 必需 |
| `aiohttp` | ^3.8 | 异步 HTTP 请求（新闻抓取） | 必需（v8） |
| `pytest` | ^7.0 | 测试框架 | 开发必需 |
| `pytest-asyncio` | ^0.20 | 异步测试支持 | 开发必需 |
| `openai` | 可选 | OpenAI 客户端（如有 api_key） | 可选 |
| 其他 | — | 各提供商 SDK（DeepSeek/Gemini） | 可选 |

---

*文档结束 — 配合 `ARCHITECTURE_OVERVIEW.md` 和 `DATA_FLOW_PIPELINES.md` 阅读*
