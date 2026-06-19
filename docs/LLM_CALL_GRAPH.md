# FZQ-AI LLM 调用图谱

> 版本：v9 · 状态：审计准备版
> 重点：标记所有 LLM 调用入口、成本敏感点、prompt 模板关联

---

## 1. LLM 调用全景图

```
┌────────────────────────────────────────────────────────────────────┐
│                        LLM 调用全景图                               │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                     LLMRouter (入口层)                       │  │
│  │  generate(request: LLMRequest) → LLMResponse              │  │
│  │  ├─ 选择 Provider（priority / round_robin / least_latency）  │  │
│  │  ├─ 尝试 fallback 链（OPENAI → DEEPSEEK → GEMINI）          │  │
│  │  └─ 返回 resp.content + resp.latency_ms + resp.provider    │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              │                                     │
│           ┌──────────────────┼──────────────────┐                 │
│           ▼                  ▼                  ▼                 │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐         │
│  │ OpenAIClient│   │DeepSeekClient│   │ GeminiClient│         │
│  │  · generate │   │  · generate  │   │  · generate │         │
│  │  · health   │   │  · health    │   │  · health   │         │
│  └─────────────┘   └─────────────┘   └─────────────┘         │
│                                                                    │
│  调用方（从入口到 LLMRouter 的调用链）：                            │
│                                                                    │
│  A. NewsPipeline（翻译 + 4 维度分析）                                │
│     ├─ _translate_if_needed() → TRANSLATION_V1                   │
│     ├─ _run_narrative() → NARRATIVE_ANALYSIS_V1                    │
│     ├─ _run_risk() → RISK_ANALYSIS_V1                            │
│     ├─ _run_sentiment() → SENTIMENT_ANALYSIS_V1                  │
│     └─ _run_scenario() → SCENARIO_ANALYSIS_V1                    │
│                                                                    │
│  B. NewsFetcher（搜索 + 过滤）                                     │
│     ├─ expand_topic_keywords() → TOPIC_EXPANSION_V1               │
│     └─ filter_by_relevance() → NEWS_RELEVANCE_FILTER_V1           │
│                                                                    │
│  C. Translator（质量评分）                                          │
│     └─ _score_translation_quality() → 内联 prompt                  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## 2. 逐调用点详解

### 2.1 NewsPipeline 调用点

| 函数 | Prompt 模板 | 调用频率 | 成本敏感 | 说明 |
|------|------------|----------|----------|------|
| `_translate_if_needed()` | `TRANSLATION_V1` | 1 次/需要翻译的 item | 🔴 高 | 每个非目标语言 item 调用 1 次 |
| `_run_narrative()` | `NARRATIVE_ANALYSIS_V1` | 1 次/开启 narrative | 🔴 高 | 前 3000 字 |
| `_run_risk()` | `RISK_ANALYSIS_V1` | 1 次/开启 risk | 🔴 高 | 前 3000 字 |
| `_run_sentiment()` | `SENTIMENT_ANALYSIS_V1` | 1 次/开启 sentiment | 🔴 高 | 前 3000 字 |
| `_run_scenario()` | `SCENARIO_ANALYSIS_V1` | 1 次/开启 scenario | 🔴 高 | 前 3000 字 |
| `_call_llm_with_fallback()` | 间接（通过上述模板） | 代理函数 | — | 统一调用 LLMRouter |

**单 item 总调用数（4 维度全开）**：4-5 次 LLM 调用

**成本估算（以 100 条新闻为例）**：
- 翻译：假设 50% 需要翻译 → 50 次
- 4 维度分析：100 × 4 = 400 次
- **总计约 450 次 LLM 调用**
- 按 DeepSeek 价格估算：~$2-5 / 批次（100 条）
- 按 OpenAI GPT-4 估算：~$10-30 / 批次（100 条）

### 2.2 NewsFetcher 调用点

| 函数 | Prompt 模板 | 调用频率 | 成本敏感 | 说明 |
|------|------------|----------|----------|------|
| `expand_topic_keywords()` | `TOPIC_EXPANSION_V1` | 1 次/topic | 🟡 中 | 每个 topic 只调用 1 次 |
| `filter_by_relevance()` | `NEWS_RELEVANCE_FILTER_V1` | batch/10 次 | 🟡 中 | 每批 10 条新闻，每批 1 次 |

**成本估算（以 100 条新闻为例）**：
- topic 扩展：1 次
- 相关性过滤：100 / 10 = 10 次
- **总计约 11 次 LLM 调用**
- 按 DeepSeek 价格估算：~$0.05 / 批次

### 2.3 Translator 调用点

| 函数 | Prompt 模板 | 调用频率 | 成本敏感 | 说明 |
|------|------------|----------|----------|------|
| `translate()` | `TRANSLATION_V1` | 1 次/需要翻译的文本 | 🔴 高 | 与 NewsPipeline 翻译重复，但 Translator 可独立使用 |
| `_score_translation_quality()` | 内联 prompt | 1 次/翻译完成 | 🟡 中 | 质量评分，max_tokens=10，成本低 |

---

## 3. Fallback 链机制

```
LLMRequest.provider = ModelProvider.OPENAI
          │
          ▼
    ┌───────────┐
    │  OPENAI   │ ← 首选提供商
    └─────┬─────┘
          │ 失败/熔断
          ▼
    ┌───────────┐
    │ DEEPSEEK  │ ← 第一次 fallback
    └─────┬─────┘
          │ 失败/熔断
          ▼
    ┌───────────┐
    │  GEMINI   │ ← 第二次 fallback
    └─────┬─────┘
          │ 失败
          ▼
    ┌───────────┐
    │  全部失败  │ → 返回空响应（error="All providers failed"）
    └───────────┘
```

**关键配置（RouterConfig）**：
- `fallback_chain`: [OPENAI, DEEPSEEK, GEMINI]
- `circuit_breaker_threshold`: 5 次失败 → 熔断
- `circuit_breaker_timeout_seconds`: 300 秒 → 熔断后冷却时间
- `load_balancing_strategy`: "priority"（默认）/ "round_robin" / "least_latency"

---

## 4. Prompt 模板 → 调用点映射

| Prompt 模板 | 使用模块 | 使用函数 | 每次调用输入量 | 期望输出 |
|-----------|---------|---------|-------------|---------|
| `TRANSLATION_V1` | NewsPipeline | `_translate_if_needed()` | title + content[:2000] | `{title, content, confidence, provider}` |
| `NARRATIVE_ANALYSIS_V1` | NewsPipeline | `_run_narrative()` | text[:3000] | `{primary_narrative, secondary_narratives, narrative_strength, key_actors, key_themes, timeline_indicators, related_events}` |
| `RISK_ANALYSIS_V1` | NewsPipeline | `_run_risk()` | text[:3000] | `{overall_risk_level, composite_risk_score, risk_factors[], systemic_risk_indicators}` |
| `SENTIMENT_ANALYSIS_V1` | NewsPipeline | `_run_sentiment()` | text[:3000] | `{overall_sentiment, sentiment_score, headline_sentiment, headline_score, content_sentiment, content_score, entity_sentiments, market_indicators}` |
| `SCENARIO_ANALYSIS_V1` | NewsPipeline | `_run_scenario()` | text[:3000] | `{base_case, optimistic_case, pessimistic_case, alternative_scenarios}` |
| `TOPIC_EXPANSION_V1` | NewsFetcher | `expand_topic_keywords()` | topic (str) | `{keywords[]}` |
| `TOPIC_REGION_CLASSIFICATION_V1` | NewsFetcher | `infer_regions()` (可选) | topic (str) | `{regions[], primary_region, confidence}` |
| `TOPIC_LANGUAGE_CLASSIFICATION_V1` | NewsFetcher | `infer_languages()` (可选) | topic (str) | `{original_language, search_languages[], confidence}` |
| `NEWS_RELEVANCE_FILTER_V1` | NewsFetcher | `filter_by_relevance()` | batch of 10 news items | `{scores[]}` |

---

## 5. 成本敏感点（审计重点）

| 排名 | 敏感点 | 单次成本 | 调用频率 | 优化建议 |
|------|--------|----------|----------|----------|
| 🔴 1 | NewsPipeline 4 维度分析 | 中-高 | 400 次/100条 | 考虑维度合并 prompt（1 次 LLM 输出全维度） |
| 🔴 2 | NewsPipeline 翻译 | 中 | 50 次/100条 | 考虑批量翻译、缓存层 |
| 🟡 3 | NewsFetcher 相关性过滤 | 低 | 10 次/100条 | 可考虑规则过滤替代 LLM（节省 80%） |
| 🟡 4 | NewsFetcher topic 扩展 | 低 | 1 次/topic | 可缓存扩展结果 |
| 🟢 5 | Translator 质量评分 | 极低 | 50 次/100条 | max_tokens=10，可忽略 |

**总成本优化潜力**：
- 如果合并 4 维度分析为 1 个 prompt：节省 75% 分析成本（300 次 → 100 次）
- 如果用规则过滤替代 LLM 相关性过滤：节省 10 次/批次
- 如果添加缓存层：节省 50% 翻译成本

---

## 6. 错误处理与降级策略

| 调用点 | 失败策略 | 降级结果 |
|--------|----------|----------|
| `_translate_if_needed()` | 返回原文 | `provider="fallback_error"`, `confidence=0.0` |
| `_run_narrative()` | 使用原始文本 | `primary_narrative=resp.content`, `confidence=0.3` |
| `_run_risk()` | 生成通用 RiskFactor | `level=LOW`, `description=原始文本` |
| `_run_sentiment()` | 全部 NEUTRAL | `score=0.0`, `confidence=0.3` |
| `_run_scenario()` | 使用原始文本 | `base_case.description=原始文本` |
| `expand_topic_keywords()` | 规则扩展 | 仅返回 TOPIC_REGION_MAP 匹配结果 |
| `filter_by_relevance()` | 不过滤 | 全部保留 |

---

*文档结束 — 配合 `DATA_FLOW_PIPELINES.md` 和 `PROMPT_SYSTEM.md` 阅读*
