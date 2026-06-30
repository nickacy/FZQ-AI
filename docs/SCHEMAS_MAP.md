# FZQ-AI 关键 Schema 模型地图

> 版本：V19 · 状态：生产就绪
> 范围：覆盖 Real System 中所有核心 Pydantic 模型

---

## 1. 模型总览（按模块分类）

| 模块 | 模型数 | 核心模型 |
|------|--------|---------|
| 新闻基础 | 3 | `NewsSource`, `RawNewsItem`, `TranslatedNewsItem` |
| 分析结果 | 5 | `NarrativeAnalysis`, `RiskAnalysis`, `SentimentAnalysis`, `ScenarioAnalysis`, `MultiDimensionAnalysis` |
| 管道 I/O | 3 | `PipelineInput`, `PipelineOutput`, `PipelineMetrics` |
| LLM 系统 | 4 | `LLMRequest`, `LLMResponse`, `FallbackRecord`, `PromptTemplate` |
| 配置 | 2 | `ProviderConfig`, `RouterConfig` |
| 日报 | 2 | `DailyReportSection`, `DailyReport` |
| 枚举 | 6 | `LanguageCode`, `RegionCode`, `AnalysisDimension`, `RiskLevel`, `SentimentLabel`, `ModelProvider` |

**总计：25 个模型 + 6 个枚举**

---

## 2. 核心模型字段详解

### 2.1 PipelineInput（管道输入）

```python
class PipelineInput(BaseModel):
    items: List[RawNewsItem]                    # 输入新闻列表
    target_language: LanguageCode = LanguageCode.EN
    dimensions: List[AnalysisDimension] = [NARRATIVE, RISK, SENTIMENT, SCENARIO]
    region_filter: Optional[List[RegionCode]] = None
    priority_threshold: float = 0.0
    max_items: int = 100
    options: Dict[str, Any] = {}              # v8 新增：intake_balance_report 等扩展数据
```

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `items` | `List[RawNewsItem]` | ✅ | — | 输入新闻列表，最大长度受 `max_items` 限制 |
| `target_language` | `LanguageCode` | — | `EN` | 目标翻译语言 |
| `dimensions` | `List[AnalysisDimension]` | — | 4 维度 | 要执行的分析维度 |
| `region_filter` | `Optional[List[RegionCode]]` | — | `None` | 区域过滤，只处理指定区域的新闻 |
| `priority_threshold` | `float` | — | `0.0` | 优先级阈值（当前未使用） |
| `max_items` | `int` | — | `100` | 最大处理条数，超过部分截断 |
| `options` | `Dict[str, Any]` | — | `{}` | **v8 新增**：扩展配置，如 `max_concurrency`, `intake_balance_report` |

**v8 新增使用方式**：
```python
options = {
    "max_concurrency": 5,                    # 并发控制
    "max_fetch_concurrency": 10,             # 抓取并发控制
    "intake_topic": "AI regulation",         # 原始议题
    "intake_balance_report": {...},          # 平衡报告
    "enable_relevance_filter": True,           # 是否启用相关性过滤
    "min_relevance_score": 0.5,               # 最低相关性评分
}
```

### 2.2 PipelineOutput（管道输出）

```python
class PipelineOutput(BaseModel):
    input_summary: PipelineInput
    analyzed_items: List[MultiDimensionAnalysis] = []
    failed_items: List[Dict[str, Any]] = []
    metrics: PipelineMetrics
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    daily_report: Optional[DailyReport] = None
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `input_summary` | `PipelineInput` | ✅ | 原样返回输入配置（含 v8 的 `options`） |
| `analyzed_items` | `List[MultiDimensionAnalysis]` | — | 成功分析的新闻列表 |
| `failed_items` | `List[Dict[str, Any]]` | — | **v7 增强**：`{id, error, error_type}` |
| `metrics` | `PipelineMetrics` | ✅ | 处理统计 |
| `generated_at` | `datetime` | — | 输出生成时间 |
| `daily_report` | `Optional[DailyReport]` | — | 日报（由 orchestrator 填充） |

### 2.3 PipelineMetrics（处理指标）

```python
class PipelineMetrics(BaseModel):
    pipeline_name: str
    items_processed: int = 0
    items_failed: int = 0
    avg_latency_ms: float = 0.0
    total_latency_ms: float = 0.0
    fallback_count: int = 0
    translation_count: int = 0
    model_usage: Dict[str, int] = {}
    errors: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `pipeline_name` | `str` | 管道标识（如 `"news_pipeline"`） |
| `items_processed` | `int` | 成功处理条数 |
| `items_failed` | `int` | 失败条数 |
| `avg_latency_ms` | `float` | 平均每条处理延迟 |
| `total_latency_ms` | `float` | 总处理延迟 |
| `fallback_count` | `int` | LLM fallback 次数 |
| `translation_count` | `int` | 翻译次数 |
| `model_usage` | `Dict[str, int]` | 各模型使用次数统计 |
| `errors` | `List[str]` | 错误信息列表 |
| `timestamp` | `datetime` | 记录时间 |

### 2.4 RawNewsItem（原始新闻）

```python
class RawNewsItem(BaseModel):
    id: str
    title: str
    content: str
    summary: Optional[str] = None
    source: NewsSource
    published_at: datetime
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    language: LanguageCode
    region: RegionCode
    url: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = []
    raw_metadata: Dict[str, Any] = {}          # v8 新增：relevance_score 等扩展数据
    translated_title: Optional[str] = None
    translated_content: Optional[str] = None
    translation_confidence: float = 0.0
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | `str` | ✅ | 唯一标识 |
| `title` | `str` | ✅ | 新闻标题 |
| `content` | `str` | ✅ | 新闻内容 |
| `source` | `NewsSource` | ✅ | 来源信息 |
| `published_at` | `datetime` | ✅ | 发布时间 |
| `language` | `LanguageCode` | ✅ | 原始语言 |
| `region` | `RegionCode` | ✅ | 所属区域 |
| `raw_metadata` | `Dict[str, Any]` | — | **v8 新增**：存储 `relevance_score` 等临时数据 |
| `translated_title` | `Optional[str]` | — | 翻译后的标题（缓存） |
| `translated_content` | `Optional[str]` | — | 翻译后的内容（缓存） |
| `translation_confidence` | `float` | — | 翻译置信度 |

### 2.5 NewsSource（新闻来源）

```python
class NewsSource(BaseModel):
    name: str
    url: Optional[str] = None
    region: RegionCode = RegionCode.GLOBAL
    language: LanguageCode = LanguageCode.EN
    reliability_score: float = 0.8
    source_type: Literal["rss", "api", "scraped", "webhook", "manual"] = "api"
    metadata: Dict[str, Any] = {}
```

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | `str` | — | 来源名称（如 "BBC World", "Reuters"） |
| `url` | `Optional[str]` | `None` | 来源 URL |
| `region` | `RegionCode` | `GLOBAL` | 来源区域 |
| `language` | `LanguageCode` | `EN` | 来源语言 |
| `reliability_score` | `float` | `0.8` | 可信度评分（0-1） |
| `source_type` | `Literal` | `"api"` | 来源类型 |
| `metadata` | `Dict[str, Any]` | `{}` | 扩展元数据 |

### 2.6 TranslatedNewsItem（翻译后新闻）

```python
class TranslatedNewsItem(BaseModel):
    original: RawNewsItem
    translated_title: str
    translated_content: str
    target_language: LanguageCode = LanguageCode.EN
    translation_provider: str = "llm"           # v8: 可为 "cached", "fallback_error", "simple_fallback"
    translation_confidence: float = 1.0
    translation_latency_ms: Optional[int] = None  # v8 新增：翻译延迟
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `original` | `RawNewsItem` | 原始新闻 |
| `translated_title` | `str` | 翻译后标题 |
| `translated_content` | `str` | 翻译后内容 |
| `target_language` | `LanguageCode` | 目标语言 |
| `translation_provider` | `str` | **v7/v8 新增**：`"llm"`, `"cached"`, `"fallback_error"`, `"simple_fallback"` |
| `translation_confidence` | `float` | 翻译置信度 |
| `translation_latency_ms` | `Optional[int]` | **v8 新增**：翻译延迟（毫秒） |

### 2.7 MultiDimensionAnalysis（多维度分析）

```python
class MultiDimensionAnalysis(BaseModel):
    news_id: str
    narrative: NarrativeAnalysis
    risk: RiskAnalysis
    sentiment: SentimentAnalysis
    scenario: ScenarioAnalysis
    cross_dimension_insights: List[str] = []
    aggregated_priority_score: float = 0.5
    recommended_actions: List[str] = []
    processed_at: datetime = Field(default_factory=datetime.utcnow)
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `news_id` | `str` | 关联新闻 ID |
| `narrative` | `NarrativeAnalysis` | 叙事分析结果 |
| `risk` | `RiskAnalysis` | 风险分析结果 |
| `sentiment` | `SentimentAnalysis` | 情感分析结果 |
| `scenario` | `ScenarioAnalysis` | 情景分析结果 |
| `cross_dimension_insights` | `List[str]` | 跨维度洞察 |
| `aggregated_priority_score` | `float` | 综合优先级评分 |
| `recommended_actions` | `List[str]` | 推荐行动 |
| `processed_at` | `datetime` | 处理时间 |

### 2.8 NarrativeAnalysis（叙事分析）

```python
class NarrativeAnalysis(BaseModel):
    news_id: str
    primary_narrative: str = ""
    secondary_narratives: List[str] = []
    narrative_strength: float = 0.0
    key_actors: List[str] = []
    key_themes: List[str] = []
    timeline_indicators: List[str] = []
    related_events: List[str] = []
    confidence: float = 0.0
    model_used: ModelProvider = ModelProvider.OPENAI
    processed_at: datetime = Field(default_factory=datetime.utcnow)
```

**v7 之前**：`primary_narrative` 默认值为 `"Mock narrative"`（测试适配器）
**v7 之后**：`primary_narrative` 默认值为 `""`（Real System），解析失败时填充

### 2.9 RiskAnalysis（风险分析）

```python
class RiskAnalysis(BaseModel):
    news_id: str
    overall_risk_level: RiskLevel = RiskLevel.LOW
    composite_risk_score: float = 0.0
    risk_factors: List[RiskFactor] = []
    systemic_risk_indicators: List[str] = []
    confidence: float = 0.0
    model_used: ModelProvider = ModelProvider.OPENAI
    processed_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2.10 RiskFactor（风险因子）

```python
class RiskFactor(BaseModel):
    risk_type: str = ""
    description: str = ""
    level: RiskLevel = RiskLevel.LOW
    probability: float = 0.0
    impact_score: float = 0.0
    affected_regions: List[RegionCode] = []
    affected_sectors: List[str] = []
    time_horizon: Literal["immediate", "short_term", "medium_term", "long_term"] = "short_term"
    evidence: List[str] = []
```

**v7 之前**：字段有 mock 默认值（如 `risk_type="mock_risk"`）
**v7 之后**：字段默认值为空字符串/0.0（Real System），解析失败时填充

### 2.11 SentimentAnalysis（情感分析）

```python
class SentimentAnalysis(BaseModel):
    news_id: str
    overall_sentiment: SentimentLabel = SentimentLabel.NEUTRAL
    sentiment_score: float = 0.0
    headline_sentiment: SentimentLabel = SentimentLabel.NEUTRAL
    headline_score: float = 0.0
    content_sentiment: SentimentLabel = SentimentLabel.NEUTRAL
    content_score: float = 0.0
    entity_sentiments: Dict[str, float] = {}
    market_indicators: List[str] = []
    confidence: float = 0.0
    model_used: ModelProvider = ModelProvider.OPENAI
    processed_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2.12 ScenarioAnalysis（情景分析）

```python
class ScenarioAnalysis(BaseModel):
    news_id: str
    base_case: ScenarioProjection
    optimistic_case: Optional[ScenarioProjection] = None
    pessimistic_case: Optional[ScenarioProjection] = None
    alternative_scenarios: List[ScenarioProjection] = []
    confidence: float = 0.0
    model_used: ModelProvider = ModelProvider.OPENAI
    processed_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2.13 ScenarioProjection（情景投影）

```python
class ScenarioProjection(BaseModel):
    scenario_name: str = ""
    description: str = ""
    probability: float = 0.0
    key_triggers: List[str] = []
    expected_outcomes: List[str] = []
    time_horizon: str = "short_term"
    affected_regions: List[RegionCode] = []
```

### 2.14 LLMRequest（LLM 请求）

```python
class LLMRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    provider: ModelProvider = ModelProvider.OPENAI
    temperature: float = 0.3
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    stream: bool = False
    system_message: Optional[str] = None
    messages: Optional[List[Dict[str, str]]] = None
    metadata: Dict[str, Any] = {}
```

### 2.15 LLMResponse（LLM 响应）

```python
class LLMResponse(BaseModel):
    content: str = ""
    provider: ModelProvider = ModelProvider.OPENAI
    model: str = ""
    usage: Dict[str, int] = {}
    latency_ms: int = 0
    finish_reason: Optional[str] = "stop"
    raw_response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
```

**v7 之前**：`content` 默认值为 `"Mock LLM response"`
**v7 之后**：`content` 默认值为 `""`（Real System）

---

## 3. 枚举定义

### 3.1 LanguageCode（语言）

```python
class LanguageCode(str, Enum):
    EN = "en"; ZH = "zh"; ES = "es"; FR = "fr"; DE = "de"
    JA = "ja"; KO = "ko"; AR = "ar"; RU = "ru"; PT = "pt"
    IT = "it"; NL = "nl"; TR = "tr"; PL = "pl"; VI = "vi"
    TH = "th"; ID = "id"
```

### 3.2 RegionCode（区域）

```python
class RegionCode(str, Enum):
    GLOBAL = "global"; US = "us"; CN = "cn"; EU = "eu"; UK = "uk"
    JP = "jp"; KR = "kr"; IN = "in"; BR = "br"; RU = "ru"
    AE = "ae"; SA = "sa"; AU = "au"; CA = "ca"; MX = "mx"
    ID = "id"; TH = "th"; VN = "vn"; TW = "tw"; HK = "hk"
    SG = "sg"; MY = "my"; PH = "ph"; DE = "de"; FR = "fr"
    IT = "it"; ES = "es"; NL = "nl"
```

### 3.3 AnalysisDimension（分析维度）

```python
class AnalysisDimension(str, Enum):
    NARRATIVE = "narrative"
    RISK = "risk"
    SENTIMENT = "sentiment"
    SCENARIO = "scenario"
```

### 3.4 RiskLevel（风险等级）

```python
class RiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"
```

### 3.5 SentimentLabel（情感标签）

```python
class SentimentLabel(str, Enum):
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"
```

### 3.6 ModelProvider（模型提供商）

```python
class ModelProvider(str, Enum):
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    GEMINI = "gemini"
    AZURE = "azure"
    ANTHROPIC = "anthropic"
```

---

## 4. v7/v8 字段变更日志

| 模型 | 变更字段 | 变更类型 | 说明 |
|------|---------|---------|------|
| `PipelineInput` | `options` | v8 新增使用 | 存储 `intake_balance_report`, `intake_topic` 等 |
| `RawNewsItem` | `raw_metadata` | v8 新增使用 | 存储 `relevance_score` 等临时数据 |
| `TranslatedNewsItem` | `translation_provider` | v7 修改值域 | 新增 `"fallback_error"`, `"simple_fallback"` |
| `TranslatedNewsItem` | `translation_latency_ms` | v8 新增 | 记录翻译延迟 |
| `NarrativeAnalysis` | 所有字段 | v7 修改默认值 | 从 mock 值改为空值/0.0 |
| `RiskAnalysis` | 所有字段 | v7 修改默认值 | 从 mock 值改为空值/0.0 |
| `RiskFactor` | 所有字段 | v7 修改默认值 | 从 mock 值改为空值/0.0 |
| `SentimentAnalysis` | 所有字段 | v7 修改默认值 | 从 mock 值改为空值/0.0 |
| `ScenarioAnalysis` | 所有字段 | v7 修改默认值 | 从 mock 值改为空值/0.0 |
| `ScenarioProjection` | 所有字段 | v7 修改默认值 | 从 mock 值改为空值/0.0 |
| `LLMResponse` | `content` | v7 修改默认值 | 从 `"Mock LLM response"` 改为 `""` |
| `LLMResponse` | `model` | v7 修改默认值 | 从 `"mock-model"` 改为 `""` |
| `PipelineMetrics` | 所有字段 | v7 修改默认值 | 从 mock 值改为空值/0.0 |

---

*文档结束 — 配合 `PROMPT_SYSTEM.md` 和 `DATA_FLOW_PIPELINES.md` 阅读*
