# FZQ-AI 数据流与管道详解

> 版本：v9 · 状态：审计准备版
> 重点：NewsPipeline 完整数据流（v6/v7/v8 增强版）

---

## 1. NewsPipeline 主数据流（v8 完整版）

```
┌──────────────────────────────────────────────────────────────────────┐
│                           数据流总览                                  │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  方式 A：基于 topic 的自动 intake（v8 新增）                            │
│  ┌──────────────────┐                                                │
│  │ topic (str)      │                                                │
│  └────────┬─────────┘                                                │
│           ▼                                                          │
│  ┌──────────────────┐     ┌──────────────┐    ┌──────────────────┐  │
│  │ NewsFetcher v8   │ ──▶ │ 过滤/去重    │ ──▶│ PipelineInput    │  │
│  │ · RSS 多源        │     │ · 非新闻过滤  │    │ · items[]        │  │
│  │ · Google News     │     │ · 相关性过滤  │    │ · target_language│  │
│  │ · Bing News       │     │ · 去重       │    │ · dimensions[]   │  │
│  │ · NewsAPI         │     │ · 平衡报告   │    │ · options{}      │  │
│  │ · GDELT           │     └──────────────┘    └────────┬─────────┘  │
│  └──────────────────┘                                    │             │
│                                                          │             │
│  方式 B：直接传入 PipelineInput（v6/v7 原始方式）                        │
│  ┌──────────────────┐                                  │             │
│  │ PipelineInput      │ ────────────────────────────────▶│             │
│  │ · items[]          │                                  │             │
│  │ · target_language  │                                  │             │
│  │ · dimensions[]     │                                  │             │
│  └──────────────────┘                                  │             │
│                                                        │             │
│                                                        ▼             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ NewsPipeline.run(PipelineInput) → PipelineOutput            │  │
│  │                                                                │  │
│  │  1. 并发处理 items（asyncio.Semaphore + gather）              │  │
│  │     ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐              │  │
│  │     │ item 0 │ │ item 1 │ │ item 2 │ │ item N │              │  │
│  │     └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘              │  │
│  │         │          │          │          │                   │  │
│  │         ▼          ▼          ▼          ▼                   │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │  │
│  │  │ 翻译模块      │ │ 翻译模块      │ │ 翻译模块      │ ...    │  │
│  │  │ _translate_   │ │ _translate_   │ │ _translate_   │        │  │
│  │  │  if_needed()  │ │  if_needed()  │ │  if_needed()  │        │  │
│  │  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘        │  │
│  │         │                │                │                 │  │
│  │         ▼                ▼                ▼                 │  │
│  │  TranslatedNewsItem  TranslatedNewsItem  TranslatedNewsItem   │  │
│  │         │                │                │                 │  │
│  │         ▼                ▼                ▼                 │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │  │
│  │  │ 多维度分析    │ │ 多维度分析    │ │ 多维度分析    │ ...    │  │
│  │  │ _analyze_    │ │ _analyze_    │ │ _analyze_    │        │  │
│  │  │ item()       │ │ item()       │ │ item()       │        │  │
│  │  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘        │  │
│  │         │                │                │                 │  │
│  │         ▼                ▼                ▼                 │  │
│  │  MultiDimensionAnalysis  MultiDimensionAnalysis  ...        │  │
│  │                                                                │  │
│  │  2. 合并结果 → PipelineOutput                                 │  │
│  │     ┌──────────────────────────────────────────────────┐     │  │
│  │     │ PipelineOutput                                   │     │  │
│  │     │   · input_summary          (PipelineInput)       │     │  │
│  │     │   · analyzed_items[]       (MultiDimensionAnalysis)│   │  │
│  │     │   · failed_items[]         ({id, error, error_type})│  │  │
│  │     │   · metrics                (PipelineMetrics)     │     │  │
│  │     │   · daily_report           (optional)            │     │  │
│  │     │   · intake_balance_report  (v8, in options)    │     │  │
│  │     └──────────────────────────────────────────────────┘     │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 2. 逐层数据流详解

### 2.1 Step 1: 翻译（_translate_if_needed）

| 输入 | `RawNewsItem` |
|------|---------------|
| 输出 | `TranslatedNewsItem` |
| 逻辑 | 1. 检查是否已有翻译（缓存命中 → 直接返回）<br>2. 检查是否有外部 `translator`（命中 → 使用）<br>3. LLM 翻译（`TRANSLATION_V1` prompt + JSON 解析）<br>4. 失败 → `provider="fallback_error"`，返回原文 |
| 并发 | 每个 item 独立翻译，并发受 `max_concurrency` 限制 |
| LLM 调用 | 每个需要翻译的 item 调用 1 次 LLM（高成本点） |
| 关键字段 | `translated_title`, `translated_content`, `translation_confidence`, `translation_provider`, `translation_latency_ms` |

### 2.2 Step 2: 多维度分析（_analyze_item）

| 输入 | `TranslatedNewsItem` + `dimensions: List[AnalysisDimension]` |
|------|---------------------------------------------------------------|
| 输出 | `MultiDimensionAnalysis` |
| 逻辑 | 按 `dimensions` 列表逐一调用分析模块（每个维度独立） |
| 并发 | 各维度在单个 item 内串行；items 之间并行 |

#### 2.2.1 叙事分析（_run_narrative）

| 输入 | 拼接文本 `title + "\n" + content`（前 3000 字） |
|------|-------------------------------------------------|
| 输出 | `NarrativeAnalysis` |
| Prompt | `NARRATIVE_ANALYSIS_V1` |
| JSON 解析 | `_safe_json_parse_v2()` → 字段完整性检查 → 默认值填充 |
| 关键字段 | `primary_narrative`, `secondary_narratives`, `narrative_strength`, `key_actors`, `key_themes`, `confidence`, `model_used` |
| 失败 Fallback | 使用 LLM 原始文本作为 `primary_narrative`，confidence=0.3 |

#### 2.2.2 风险分析（_run_risk）

| 输入 | 拼接文本 `title + "\n" + content`（前 3000 字） |
|------|-------------------------------------------------|
| 输出 | `RiskAnalysis` |
| Prompt | `RISK_ANALYSIS_V1` |
| JSON 解析 | 解析 `overall_risk_level` → `RiskLevel` 枚举<br>解析 `risk_factors` → `List[RiskFactor]`（逐项字段验证）<br>解析 `systemic_risk_indicators` → `List[str]` |
| 关键字段 | `overall_risk_level`, `composite_risk_score`, `risk_factors`, `systemic_risk_indicators`, `confidence` |
| 失败 Fallback | 生成一个通用 `RiskFactor`，使用 LLM 原始文本作为 description |

#### 2.2.3 情感分析（_run_sentiment）

| 输入 | 拼接文本 `title + "\n" + content`（前 3000 字） |
|------|-------------------------------------------------|
| 输出 | `SentimentAnalysis` |
| Prompt | `SENTIMENT_ANALYSIS_V1` |
| JSON 解析 | 解析 `overall_sentiment` / `headline_sentiment` / `content_sentiment` → `SentimentLabel` 枚举<br>解析 `sentiment_score` / `headline_score` / `content_score` → float<br>解析 `entity_sentiments` → `Dict[str, float]` |
| 关键字段 | `overall_sentiment`, `sentiment_score`, `headline_sentiment`, `headline_score`, `content_sentiment`, `content_score`, `entity_sentiments` |
| 失败 Fallback | 全部 `NEUTRAL`，score=0.0，confidence=0.3 |

#### 2.2.4 情景分析（_run_scenario）

| 输入 | 拼接文本 `title + "\n" + content`（前 3000 字） |
|------|-------------------------------------------------|
| 输出 | `ScenarioAnalysis` |
| Prompt | `SCENARIO_ANALYSIS_V1` |
| JSON 解析 | 解析 `base_case` / `optimistic_case` / `pessimistic_case` → `Optional[ScenarioProjection]`<br>解析 `alternative_scenarios` → `List[ScenarioProjection]` |
| 关键字段 | `base_case`, `optimistic_case`, `pessimistic_case`, `alternative_scenarios` |
| 失败 Fallback | 使用 LLM 原始文本作为 `base_case.description` |

### 2.3 Step 3: 合并 → PipelineOutput

| 字段 | 来源 | 说明 |
|------|------|------|
| `input_summary` | 原样传入 `PipelineInput` | 保留原始输入配置 |
| `analyzed_items` | 成功的 `MultiDimensionAnalysis` 列表 | 按原始 items 顺序 |
| `failed_items` | 失败记录：`{id, error, error_type}` | v7 增强：包含 `error_type` |
| `metrics` | 实时计算 | `PipelineMetrics`（items_processed, items_failed, total_latency_ms, avg_latency_ms） |
| `daily_report` | 可选（由 orchestrator 填充） | v8 未直接生成，预留 |
| `intake_balance_report` | `PipelineInput.options`（v8 新增） | `compute_balance_report()` 结果 |

---

## 3. v8 新增：Intake 数据流（intake_from_topic）

```
topic (str)
    │
    ▼
┌──────────────────────────────────────────────────┐
│ 1. NewsFetcher.expand_topic_keywords(topic)      │
│    ├─ 规则扩展：TOPIC_REGION_MAP 匹配 → 区域变体    │
│    └─ LLM 扩展：TOPIC_EXPANSION_V1 prompt → 关键词列表│
│       输出：List[str]（最多 20 个）                │
└──────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────┐
│ 2. NewsFetcher.infer_regions(topic)              │
│    └─ TOPIC_REGION_MAP 匹配 → RegionCode 列表      │
│    2b. NewsFetcher.infer_languages(topic)         │
│    └─ Unicode 范围检测 → LanguageCode 列表         │
└──────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────┐
│ 3. 并行抓取（asyncio.gather + Semaphore）          │
│    ├─ RSS 源（按区域）：RSS_SOURCES_BY_REGION     │
│    ├─ Google News RSS（按语言）                    │
│    ├─ Bing News RSS（按语言）                      │
│    ├─ NewsAPI（如果配置了 key）                   │
│    └─ GDELT                                       │
│    输出：List[RawNewsItem]（最多 max_total 条）   │
└──────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────┐
│ 4. 过滤                                           │
│    ├─ filter_non_news()：广告/PR/非新闻过滤        │
│    ├─ filter_by_relevance()：LLM 批量评分（batch=10）│
│    │   └─ NEWS_RELEVANCE_FILTER_V1 prompt         │
│    └─ 去重：SHA-256 hash（title + content[:200]）  │
└──────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────┐
│ 5. 平衡报告 compute_balance_report()              │
│    ├─ region_distribution：区域分布               │
│    ├─ language_distribution：语言分布             │
│    ├─ source_distribution：来源分布               │
│    ├─ region_balance_score：区域平衡度（0-1）       │
│    ├─ language_balance_score：语言平衡度（0-1）     │
│    └─ source_balance_score：来源平衡度（0-1）       │
└──────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────┐
│ 6. 构建 PipelineInput                             │
│    ├─ items = 过滤后的新闻列表                    │
│    ├─ target_language = options.target_language   │
│    ├─ dimensions = options.dimensions               │
│    ├─ max_items = options.max_items                 │
│    ├─ region_filter = regions                       │
│    └─ options.intake_balance_report = 平衡报告      │
└──────────────────────────────────────────────────┘
```

---

## 4. 并发模型

```
NewsPipeline.run()
    ├── max_concurrency = options.get("max_concurrency", 5)
    ├── Semaphore(max_concurrency)
    │
    └── asyncio.gather(
            _process(item0),    ← Semaphore 内：翻译 → 分析
            _process(item1),    ← Semaphore 内：翻译 → 分析
            _process(item2),    ← Semaphore 内：翻译 → 分析
            ...
            _process(itemN),    ← Semaphore 内：翻译 → 分析
            return_exceptions=True
        )

NewsFetcher.fetch_multi_source()
    ├── max_concurrency = options.get("max_fetch_concurrency", 10)
    ├── Semaphore(max_concurrency)
    │
    └── asyncio.gather(
            _fetch_rss(source0),        ← RSS 抓取
            _fetch_rss(source1),        ← RSS 抓取
            _fetch_newsapi(query0),     ← NewsAPI 调用
            _fetch_gdelt(query0),       ← GDELT 调用
            ...
            return_exceptions=True
        )
```

| 并发层 | 并发数 | 作用 | 隔离策略 |
|--------|--------|------|----------|
| Pipeline 层 | 默认 5 | items 并行处理 | 每个 item 独立，失败不影响其他 |
| Fetch 层 | 默认 10 | 多源并行抓取 | 每个源独立，失败返回空列表 |

---

## 5. 数据流关键指标（每条 item）

| 阶段 | 平均调用次数 | 是否调用 LLM | 平均延迟（估算） |
|------|-------------|-------------|-----------------|
| 翻译 | 1 次/需要翻译的 item | ✅（如非缓存） | 500-3000 ms |
| 叙事分析 | 1 次/开启 narrative | ✅ | 1000-5000 ms |
| 风险分析 | 1 次/开启 risk | ✅ | 1000-5000 ms |
| 情感分析 | 1 次/开启 sentiment | ✅ | 500-3000 ms |
| 情景分析 | 1 次/开启 scenario | ✅ | 1500-6000 ms |
| **总计**（4 维度全开） | **4-5 次/item** | ✅ | **4000-17000 ms** |

**v8 优化**：
- 并发将单 item 总延迟从串行的 ~17s 降到并行的 ~5-8s（5 并发时）
- 批量处理 10 个 items 的总延迟约 15-30s（取决于 LLM 提供商响应）

---

*文档结束 — 配合 `ARCHITECTURE_OVERVIEW.md` 和 `LLM_CALL_GRAPH.md` 阅读*
