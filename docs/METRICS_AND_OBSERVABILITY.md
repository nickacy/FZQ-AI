# FZQ-AI 指标与可观测性

> 版本：v9 · 状态：审计准备版
> 重点：当前指标设计、已使用 vs 未充分利用、情报级指标建议

---

## 1. 当前指标设计

### 1.1 PipelineMetrics（管道级）

```python
class PipelineMetrics(BaseModel):
    pipeline_name: str
    items_processed: int = 0           # 成功处理条数
    items_failed: int = 0               # 失败条数
    avg_latency_ms: float = 0.0       # 平均延迟（ms）
    total_latency_ms: float = 0.0     # 总延迟（ms）
    fallback_count: int = 0            # LLM fallback 次数
    translation_count: int = 0         # 翻译次数
    model_usage: Dict[str, int] = {}   # 各模型使用次数
    errors: List[str] = []            # 错误信息列表
    timestamp: datetime = ...         # 记录时间
```

### 1.2 LLMRouter 指标（通过 get_metrics()）

```python
class PipelineMetrics(pipeline_name="llm_router"):
    items_processed: int = 0           # 成功请求数
    items_failed: int = 0               # 失败请求数（包含熔断）
    fallback_count: int = 0            # 发生 fallback 的次数
    model_usage: Dict[str, int] = {}   # 各提供商使用次数
    errors: List[str] = []            # 错误信息
```

### 1.3 FallbackRecord（每次 fallback 记录）

```python
class FallbackRecord(BaseModel):
    original_provider: ModelProvider   # 原始请求提供商
    fallback_provider: ModelProvider    # 实际使用的 fallback 提供商
    reason: str                        # fallback 原因
    latency_ms: int                    # 延迟
    success: bool                      # 是否成功
    timestamp: datetime                # 时间
```

### 1.4 v8 新增：Intake 平衡报告（通过 options 传递）

```json
{
  "region_distribution": {...},
  "language_distribution": {...},
  "source_distribution": {...},
  "total_items": 100,
  "region_balance_score": 0.92,
  "language_balance_score": 0.65,
  "source_balance_score": 0.78
}
```

---

## 2. 指标使用状态矩阵

| 指标 | 类型 | 当前使用 | 未来价值 | 建议 |
|------|------|---------|----------|------|
| `items_processed` | 计数 | ✅ 已使用 | 基础监控 | 保持 |
| `items_failed` | 计数 | ✅ 已使用 | 故障检测 | 保持 |
| `avg_latency_ms` | 延迟 | ✅ 已使用 | 性能监控 | 保持 |
| `total_latency_ms` | 延迟 | ✅ 已使用 | 性能监控 | 保持 |
| `fallback_count` | 计数 | ✅ 已使用 | 提供商健康度 | 保持 |
| `translation_count` | 计数 | ✅ 已使用 | 成本监控 | 保持 |
| `model_usage` | 字典 | ✅ 已使用 | 成本分析 | 保持 |
| `errors` | 列表 | ✅ 已使用 | 故障排查 | 保持 |
| `region_balance_score` | 评分 | ⚠️ 结构存在，未上报 | 情报质量监控 | 建议接入监控 |
| `language_balance_score` | 评分 | ⚠️ 结构存在，未上报 | 情报质量监控 | 建议接入监控 |
| `source_balance_score` | 评分 | ⚠️ 结构存在，未上报 | 情报质量监控 | 建议接入监控 |
| `relevance_score` | 评分 | ⚠️ 写入 raw_metadata，未聚合 | 情报质量监控 | 建议聚合统计 |
| `translation_confidence` | 评分 | ⚠️ 记录但无统计 | 翻译质量监控 | 建议聚合统计 |
| `translation_latency_ms` | 延迟 | ⚠️ 记录但无统计 | 翻译性能监控 | 建议聚合统计 |

---

## 3. 已使用指标详解

### 3.1 items_processed / items_failed

| 指标 | 计算方式 | 使用场景 |
|------|---------|----------|
| `items_processed` | `run()` 中成功分析的 item 数 | 吞吐量监控 |
| `items_failed` | `run()` 中异常的 item 数 + None 返回数 | 故障率监控 |
| 失败率 | `items_failed / (items_processed + items_failed)` | 健康度判断 |

### 3.2 latency 指标

| 指标 | 计算方式 | 使用场景 |
|------|---------|----------|
| `total_latency_ms` | `(end - start) * 1000` | 总耗时 |
| `avg_latency_ms` | `total_latency_ms / items_processed` | 单条平均耗时 |
| 并发效率 | `avg_latency_ms * items_processed / total_latency_ms` | 接近并发数 = 效率高 |

### 3.3 fallback_count / model_usage

| 指标 | 计算方式 | 使用场景 |
|------|---------|----------|
| `fallback_count` | LLMRouter 中发生 fallback 的次数 | 提供商稳定性 |
| `model_usage["openai"]` | 各提供商成功调用次数 | 成本分摊 |
| fallback 率 | `fallback_count / items_processed` | 提供商健康度 |

---

## 4. 结构存在但未充分利用的指标

### 4.1 平衡度指标（v8 新增）

```json
{
  "region_balance_score": 0.92,   // 当前：计算后写入 options，未使用
  "language_balance_score": 0.65,   // 当前：同上
  "source_balance_score": 0.78      // 当前：同上
}
```

**建议利用方式**：
- 当 `region_balance_score < 0.5` 时，触发告警（区域偏差过大）
- 当 `language_balance_score < 0.3` 时，自动扩展语言源
- 当 `source_balance_score < 0.3` 时，自动扩展来源
- 将平衡度指标纳入日报，作为情报质量维度

### 4.2 相关性评分（v8 新增）

```json
// 写入每条 RawNewsItem.raw_metadata["relevance_score"]
{
  "relevance_score": 0.85
}
```

**建议利用方式**：
- 计算平均相关性：`mean(relevance_score)`
- 计算高相关性比例：`count(score > 0.7) / total`
- 低相关性告警：`count(score < 0.3) / total > 0.2` 时告警

### 4.3 翻译质量指标（v7/v8 新增）

```json
// 写入 TranslatedNewsItem
{
  "translation_confidence": 0.85,
  "translation_latency_ms": 1200,
  "translation_provider": "llm"
}
```

**建议利用方式**：
- 平均翻译置信度：`mean(translation_confidence)`
- 低质量翻译比例：`count(confidence < 0.5) / total`
- 翻译延迟分位值：`p50/p95/p99 translation_latency_ms`
- 翻译失败率：`count(provider == "fallback_error") / total`

---

## 5. 情报级指标建议（DeepSeek 审计方向）

### 5.1 安全情报指标

| 指标 | 计算方式 | 用途 |
|------|---------|------|
| 高风险新闻占比 | `count(risk.overall_risk_level in [CRITICAL, HIGH]) / total` | 安全预警 |
| 风险趋势 | 连续 N 天的高风险新闻占比变化 | 趋势分析 |
| 风险热点区域 | `count(risk.affected_regions)` 按区域聚合 | 热点识别 |
| 风险类型分布 | `count(risk_factors.risk_type)` 按类型聚合 | 威胁画像 |

### 5.2 情感情报指标

| 指标 | 计算方式 | 用途 |
|------|---------|------|
| 整体情感倾向 | `mean(sentiment.sentiment_score)` | 市场情绪 |
| 情感极化度 | `std(sentiment.sentiment_score)` | 分歧程度 |
| 负面情感占比 | `count(sentiment.overall_sentiment in [NEGATIVE, VERY_NEGATIVE]) / total` | 危机预警 |
| 实体情感波动 | `entity_sentiments` 按实体时间序列 | 实体声誉监控 |

### 5.3 叙事情报指标

| 指标 | 计算方式 | 用途 |
|------|---------|------|
| 主导叙事 | `count(narrative.primary_narrative)` 按叙事聚合 | 议题热度 |
| 叙事集中度 | 主导叙事占比 / 总叙事数 | 信息集中度 |
| 关键行为者 | `count(narrative.key_actors)` 按行为者聚合 | 影响力分析 |
| 叙事演变 | 同一议题连续多天的叙事变化 | 舆情演变 |

### 5.4 情景情报指标

| 指标 | 计算方式 | 用途 |
|------|---------|------|
| 基准情景概率 | `mean(scenario.base_case.probability)` | 预测置信度 |
| 乐观/悲观概率比 | `optimistic.probability / pessimistic.probability` | 情绪偏向 |
| 情景一致性 | 同一议题不同新闻的情景一致性 | 预测稳定性 |

### 5.5 系统健康指标

| 指标 | 计算方式 | 用途 |
|------|---------|------|
| LLM 调用成功率 | `1 - items_failed / total_items` | 系统稳定性 |
| 平均并发利用率 | `actual_concurrent / max_concurrency` | 资源利用率 |
| 缓存命中率 | `count(translation_provider == "cached") / total` | 效率优化 |
| 端到端延迟 | 从 intake 到 PipelineOutput 的总延迟 | 用户体验 |

---

## 6. 可观测性建议

### 6.1 日志设计

```python
# 建议在每个关键步骤添加结构化日志

# 1. Intake 阶段
log.info("intake_start", topic=topic, expected_sources=source_count)
log.info("intake_complete", items_fetched=len(items), balance_score=balance_score)

# 2. 分析阶段
log.info("analysis_start", item_id=item.id, dimensions=dimensions)
log.info("analysis_complete", item_id=item.id, latency_ms=latency, provider=provider)

# 3. 错误阶段
log.error("analysis_failed", item_id=item.id, error=error, error_type=error_type)
```

### 6.2 监控告警建议

| 告警条件 | 级别 | 响应 |
|----------|------|------|
| `items_failed / total > 0.2` | 警告 | 检查 LLM 提供商状态 |
| `fallback_count > 5` | 警告 | 检查首选提供商健康度 |
| `region_balance_score < 0.3` | 信息 | 自动扩展区域源 |
| `language_balance_score < 0.2` | 信息 | 自动扩展语言源 |
| `avg_latency_ms > 10000` | 警告 | 检查并发设置或提供商 |
| `high_risk_ratio > 0.3` | 紧急 | 人工介入分析 |
| `negative_sentiment_ratio > 0.5` | 警告 | 舆情监控关注 |

---

## 7. 指标与成本关联

| 指标 | 成本关联 | 优化建议 |
|------|---------|----------|
| `translation_count` | 直接翻译成本 | 添加缓存层，减少重复翻译 |
| `model_usage` | 各提供商费用 | 优先使用低成本提供商（DeepSeek） |
| `fallback_count` | 额外成本 | 优化首选提供商稳定性 |
| `items_processed` | 总分析成本 | 合并分析维度（1 次 LLM 输出全维度） |
| `items_failed` | 浪费成本 | 优化 JSON 解析，减少重试 |

---

*文档结束 — 配合 `NEWS_INTAKE_SYSTEM.md` 和 `REGION_LANGUAGE_LOGIC.md` 阅读*
