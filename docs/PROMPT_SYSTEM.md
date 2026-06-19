# FZQ-AI Prompt 系统详解

> 版本：v9 · 状态：审计准备版
> 范围：v6/v7 原有模板 + v8 新增模板，共 9 个模板

---

## 1. Prompt 模板总览

| 模板名 | 版本 | 所属版本 | 使用模块 | 使用场景 |
|--------|------|---------|---------|---------|
| `TRANSLATION_V1` | v1 | v6 | NewsPipeline, Translator | 新闻翻译 |
| `NARRATIVE_ANALYSIS_V1` | v1 | v7 | NewsPipeline | 叙事分析 |
| `RISK_ANALYSIS_V1` | v1 | v7 | NewsPipeline | 风险分析 |
| `SENTIMENT_ANALYSIS_V1` | v1 | v7 | NewsPipeline | 情感分析 |
| `SCENARIO_ANALYSIS_V1` | v1 | v7 | NewsPipeline | 情景分析 |
| `TOPIC_EXPANSION_V1` | v1 | v8 | NewsFetcher | 议题扩展 |
| `TOPIC_REGION_CLASSIFICATION_V1` | v1 | v8 | NewsFetcher | 区域分类 |
| `TOPIC_LANGUAGE_CLASSIFICATION_V1` | v1 | v8 | NewsFetcher | 语言分类 |
| `NEWS_RELEVANCE_FILTER_V1` | v1 | v8 | NewsFetcher | 相关性过滤 |

此外，还有 v6 旧模板保留（未在新代码中使用）：`NARRATIVE_V1`, `RISK_V1`, `DAILY_REPORT_V1`

---

## 2. v7 模板：分析类（严格 JSON 输出）

### 2.1 TRANSLATION_V1

| 属性 | 值 |
|------|-----|
| **输入变量** | `target_language`, `title`, `content` |
| **期望输出** | `{title: str, content: str, confidence: float, provider: str}` |
| **使用位置** | `news_pipeline._translate_if_needed()`, `translator.translate()` |
| **结果质量影响** | 🔴 高 — 翻译质量直接影响后续所有分析 |
| **成本影响** | 🔴 高 — 每次翻译调用 1 次 LLM |
| **特殊要求** | 只输出 JSON，不输出 Markdown 代码块、不输出解释性文字 |

**审计关注点**：
- 翻译 prompt 要求的是 `"title"` 和 `"content"`，但某些 LLM 可能只输出 `"content"` 而忽略 `"title"`
- `_safe_json_parse_v2()` 会尝试从 `title` 或 `content` 任一存在时提取
- 如果 LLM 返回空 JSON `{}`，fallback 策略是返回原文

### 2.2 NARRATIVE_ANALYSIS_V1

| 属性 | 值 |
|------|-----|
| **输入变量** | `text`（新闻内容前 3000 字） |
| **期望输出** | `{primary_narrative, secondary_narratives, narrative_strength, key_actors, key_themes, timeline_indicators, related_events}` |
| **使用位置** | `news_pipeline._run_narrative()` |
| **结果质量影响** | 🔴 高 — 叙事分析是上层应用的核心输入 |
| **成本影响** | 🔴 高 — 每 item 1 次 |

**审计关注点**：
- `narrative_strength` 期望是 0-1 的 float，但 LLM 有时返回字符串（如 "0.8"）
- `_safe_float()` 已处理字符串转换
- `secondary_narratives` 是列表，但 LLM 有时返回空对象或 null

### 2.3 RISK_ANALYSIS_V1

| 属性 | 值 |
|------|-----|
| **输入变量** | `text`（新闻内容前 3000 字） |
| **期望输出** | `{overall_risk_level, composite_risk_score, risk_factors[], systemic_risk_indicators}` |
| **使用位置** | `news_pipeline._run_risk()` |
| **结果质量影响** | 🔴 高 — 风险分析直接用于安全预警 |
| **成本影响** | 🔴 高 — 每 item 1 次 |

**审计关注点**：
- `overall_risk_level` 期望枚举值："critical", "high", "medium", "low", "minimal"
- LLM 有时返回大写或中文（如 "高"），`_safe_enum()` 通过小写匹配处理
- `risk_factors` 是对象列表，每个对象需包含 8 个字段

### 2.4 SENTIMENT_ANALYSIS_V1

| 属性 | 值 |
|------|-----|
| **输入变量** | `text`（新闻内容前 3000 字） |
| **期望输出** | `{overall_sentiment, sentiment_score, headline_sentiment, headline_score, content_sentiment, content_score, entity_sentiments, market_indicators}` |
| **使用位置** | `news_pipeline._run_sentiment()` |
| **结果质量影响** | 🟡 中 — 情感分析用于趋势判断，但精度要求相对宽松 |
| **成本影响** | 🔴 高 — 每 item 1 次 |

### 2.5 SCENARIO_ANALYSIS_V1

| 属性 | 值 |
|------|-----|
| **输入变量** | `text`（新闻内容前 3000 字） |
| **期望输出** | `{base_case, optimistic_case, pessimistic_case, alternative_scenarios}`，每个 case 是 ScenarioProjection 对象 |
| **使用位置** | `news_pipeline._run_scenario()` |
| **结果质量影响** | 🟡 中 — 情景分析是预测性质，容忍误差 |
| **成本影响** | 🔴 高 — 每 item 1 次（通常输出最长，成本最高） |

**审计关注点**：
- 这是 9 个模板中输出结构最复杂的，JSON 解析失败率最高
- `alternative_scenarios` 是空列表的情况很常见，需要处理
- 4 个 case 中的任何一个都可能是 null 或缺失

---

## 3. v8 模板：搜索与过滤类

### 3.1 TOPIC_EXPANSION_V1

| 属性 | 值 |
|------|-----|
| **输入变量** | `topic`（原始议题） |
| **期望输出** | `{keywords: [str]}`（5-10 个关键词） |
| **使用位置** | `news_fetcher.expand_topic_keywords()` |
| **结果质量影响** | 🟡 中 — 扩展质量影响搜索覆盖度，但规则 fallback 已兜底 |
| **成本影响** | 🟢 低 — 每 topic 仅 1 次 |
| **特殊要求** | 关键词应包含中英文双语、不同区域变体 |

**审计关注点**：
- 当前实现中，规则扩展（TOPIC_REGION_MAP）优先于 LLM 扩展
- 如果 LLM 扩展失败，至少还有规则扩展的结果
- LLM 可能返回非列表格式的 keywords，需要防御性处理

### 3.2 TOPIC_REGION_CLASSIFICATION_V1

| 属性 | 值 |
|------|-----|
| **输入变量** | `topic`（原始议题） |
| **期望输出** | `{regions: [str], primary_region: str, confidence: float}` |
| **使用位置** | 预留（当前使用规则推断） |
| **结果质量影响** | 🟡 中 — 区域推断影响 RSS 源选择 |
| **成本影响** | 🟢 低 — 每 topic 1 次 |

**当前状态**：
- 模板已定义，但 `infer_regions()` 当前使用规则（TOPIC_REGION_MAP）
- 模板作为 LLM 增强选项，可在未来启用

### 3.3 TOPIC_LANGUAGE_CLASSIFICATION_V1

| 属性 | 值 |
|------|-----|
| **输入变量** | `topic`（原始议题） |
| **期望输出** | `{original_language: str, search_languages: [str], confidence: float}` |
| **使用位置** | 预留（当前使用 Unicode 检测） |
| **结果质量影响** | 🟡 中 — 语言推断影响搜索覆盖度 |
| **成本影响** | 🟢 低 — 每 topic 1 次 |

**当前状态**：
- 模板已定义，但 `infer_languages()` 当前使用 Unicode 范围检测
- 模板作为 LLM 增强选项，可在未来启用

### 3.4 NEWS_RELEVANCE_FILTER_V1

| 属性 | 值 |
|------|-----|
| **输入变量** | `topic`, `news_batch`（最多 10 条新闻） |
| **期望输出** | `{scores: [float]}`（0-1 的相关性评分，每个 item 1 个） |
| **使用位置** | `news_fetcher.filter_by_relevance()` |
| **结果质量影响** | 🔴 高 — 过滤质量直接影响 intake 质量 |
| **成本影响** | 🟡 中 — 每 10 条 1 次，100 条约 10 次 |
| **特殊要求** | 评分标准：主题匹配度、内容深度、时效性、来源可信度 |

**审计关注点**：
- 批量评分（batch=10）是为了降低成本，但牺牲了精度（无法深入分析每条新闻）
- 可考虑规则预过滤（关键词匹配）+ LLM 精过滤的两层策略
- 如果 LLM 返回的 scores 长度与 batch 不匹配，当前代码有防御性处理

---

## 4. 模板渲染系统

### 4.1 渲染引擎

```python
class PromptTemplates:
    @staticmethod
    def render(template: str, variables: Dict[str, Any]) -> str:
        output = template
        for key, value in variables.items():
            placeholder = "{{" + key + "}}"
            output = output.replace(placeholder, str(value))
        return output
```

| 属性 | 说明 |
|------|------|
| 依赖 | 无外部依赖（纯字符串替换） |
| 模板引擎 | 自定义简单替换（非 Jinja2） |
| 变量语法 | `{{variable_name}}` |
| 转义 | 无转义（输入值直接 str() 转换） |
| 嵌套 | 不支持嵌套或条件语句 |

### 4.2 设计意图

- **不引入 Jinja2**：避免额外依赖，减少部署复杂度
- **简单替换足够**：所有模板都是"变量注入 + 固定文本"，无需复杂逻辑
- **可扩展**：如果需要，可以在未来替换为 Jinja2 而无需修改模板内容

---

## 5. 结果质量影响排序

| 排名 | 模板 | 对结果质量影响 | 原因 |
|------|------|---------------|------|
| 1 | `RISK_ANALYSIS_V1` | 🔴 最高 | 风险分析用于安全预警，误报/漏报都有严重后果 |
| 2 | `NARRATIVE_ANALYSIS_V1` | 🔴 高 | 叙事分析是上层应用的核心输入，影响情报判断 |
| 3 | `TRANSLATION_V1` | 🔴 高 | 翻译错误会传播到所有后续分析 |
| 4 | `NEWS_RELEVANCE_FILTER_V1` | 🔴 高 | 过滤质量决定 intake 质量，影响下游所有分析 |
| 5 | `SCENARIO_ANALYSIS_V1` | 🟡 中 | 预测性质，容忍一定误差 |
| 6 | `SENTIMENT_ANALYSIS_V1` | 🟡 中 | 情感分析相对成熟，LLM 表现稳定 |
| 7 | `TOPIC_EXPANSION_V1` | 🟢 低 | 有规则 fallback，质量不足时规则兜底 |
| 8 | `TOPIC_REGION_CLASSIFICATION_V1` | 🟢 低 | 当前使用规则推断，模板未启用 |
| 9 | `TOPIC_LANGUAGE_CLASSIFICATION_V1` | 🟢 低 | 当前使用 Unicode 检测，模板未启用 |

---

## 6. 成本影响排序

| 排名 | 模板 | 单次成本 | 调用次数/100条 | 总成本影响 | 优化建议 |
|------|------|---------|---------------|-----------|---------|
| 1 | `SCENARIO_ANALYSIS_V1` | 高 | 100 次 | 🔴 最高 | 输出最长，可考虑缩短 prompt |
| 2 | `RISK_ANALYSIS_V1` | 高 | 100 次 | 🔴 高 | 风险分析不可省略，但可合并维度 |
| 3 | `NARRATIVE_ANALYSIS_V1` | 高 | 100 次 | 🔴 高 | 可尝试合并 prompt |
| 4 | `SENTIMENT_ANALYSIS_V1` | 中 | 100 次 | 🔴 高 | 可尝试合并 prompt |
| 5 | `TRANSLATION_V1` | 中 | 50 次 | 🟡 中 | 可添加缓存层 |
| 6 | `NEWS_RELEVANCE_FILTER_V1` | 低 | 10 次 | 🟡 中 | 可用规则替代 |
| 7 | `TOPIC_EXPANSION_V1` | 低 | 1 次 | 🟢 低 | 可缓存 |
| 8-9 | 分类模板（未启用） | 低 | 0 次 | 🟢 低 | 当前未使用 |

---

*文档结束 — 配合 `LLM_CALL_GRAPH.md` 和 `SCHEMAS_MAP.md` 阅读*
