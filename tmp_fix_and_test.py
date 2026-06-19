import sys
from pathlib import Path

sys.path.insert(0, r'C:\Users\nicka\FZQ-AI-WORKSPACE\FZQ-AI')

BASE = Path(r'C:\Users\nicka\FZQ-AI-WORKSPACE\FZQ-AI')

# 1. Restore old schemas
schema_init = BASE / 'fzq_ai' / 'schemas' / 'test_adapter' / '__init__.py'
schema_init.write_text('''"""FZQ-AI Schemas — Test Adapter Layer"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Literal, Union
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

class LanguageCode(str, Enum):
    EN = "en"; ZH = "zh"; ES = "es"; FR = "fr"; DE = "de"; JA = "ja"; KO = "ko"; AR = "ar"; RU = "ru"; PT = "pt"; IT = "it"; NL = "nl"; TR = "tr"; PL = "pl"; VI = "vi"; TH = "th"; ID = "id"

class RegionCode(str, Enum):
    GLOBAL = "global"; US = "us"; CN = "cn"; EU = "eu"; UK = "uk"; JP = "jp"; KR = "kr"; IN = "in"; BR = "br"; RU = "ru"; AE = "ae"; SA = "sa"; AU = "au"; CA = "ca"; MX = "mx"; ID = "id"; TH = "th"; VN = "vn"; TW = "tw"; HK = "hk"; SG = "sg"; MY = "my"; PH = "ph"; DE = "de"; FR = "fr"; IT = "it"; ES = "es"; NL = "nl"

class AnalysisDimension(str, Enum):
    NARRATIVE = "narrative"; RISK = "risk"; SENTIMENT = "sentiment"; SCENARIO = "scenario"

class RiskLevel(str, Enum):
    CRITICAL = "critical"; HIGH = "high"; MEDIUM = "medium"; LOW = "low"; MINIMAL = "minimal"

class SentimentLabel(str, Enum):
    VERY_POSITIVE = "very_positive"; POSITIVE = "positive"; NEUTRAL = "neutral"; NEGATIVE = "negative"; VERY_NEGATIVE = "very_negative"

class ModelProvider(str, Enum):
    OPENAI = "openai"; DEEPSEEK = "deepseek"; GEMINI = "gemini"; AZURE = "azure"; ANTHROPIC = "anthropic"

class NewsSource(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())
    name: str
    url: Optional[str] = None
    region: RegionCode = RegionCode.GLOBAL
    language: LanguageCode = LanguageCode.EN
    reliability_score: float = 0.8
    source_type: Literal["rss", "api", "scraped", "webhook", "manual"] = "api"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RawNewsItem(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())
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
    tags: List[str] = Field(default_factory=list)
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)
    translated_title: Optional[str] = None
    translated_content: Optional[str] = None
    translation_confidence: float = 0.0

class TranslatedNewsItem(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())
    original: RawNewsItem
    translated_title: str
    translated_content: str
    target_language: LanguageCode = LanguageCode.EN
    translation_provider: str = "mock"
    translation_confidence: float = 1.0
    translation_latency_ms: Optional[int] = 1

class NarrativeAnalysis(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())
    news_id: str
    primary_narrative: str = "Mock narrative"
    secondary_narratives: List[str] = Field(default_factory=list)
    narrative_strength: float = 0.5
    key_actors: List[str] = Field(default_factory=lambda: ["Actor A"])
    key_themes: List[str] = Field(default_factory=lambda: ["Theme A"])
    timeline_indicators: List[str] = Field(default_factory=list)
    related_events: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    analysis_metadata: Dict[str, Any] = Field(default_factory=dict)
    model_used: ModelProvider = ModelProvider.OPENAI
    processed_at: datetime = Field(default_factory=datetime.utcnow)

class RiskFactor(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())
    risk_type: str = "mock_risk"
    description: str = "Mock risk factor"
    level: RiskLevel = RiskLevel.LOW
    probability: float = 0.1
    impact_score: float = 0.1
    affected_regions: List[RegionCode] = Field(default_factory=list)
    affected_sectors: List[str] = Field(default_factory=list)
    time_horizon: Literal["immediate", "short_term", "medium_term", "long_term"] = "short_term"
    evidence: List[str] = Field(default_factory=list)

class RiskAnalysis(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())
    news_id: str
    overall_risk_level: RiskLevel = RiskLevel.LOW
    composite_risk_score: float = 0.1
    risk_factors: List[RiskFactor] = Field(default_factory=lambda: [RiskFactor()])
    systemic_risk_indicators: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    model_used: ModelProvider = ModelProvider.OPENAI
    processed_at: datetime = Field(default_factory=datetime.utcnow)

class SentimentAnalysis(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())
    news_id: str
    overall_sentiment: SentimentLabel = SentimentLabel.NEUTRAL
    sentiment_score: float = 0.0
    headline_sentiment: SentimentLabel = SentimentLabel.NEUTRAL
    headline_score: float = 0.0
    content_sentiment: SentimentLabel = SentimentLabel.NEUTRAL
    content_score: float = 0.0
    entity_sentiments: Dict[str, float] = Field(default_factory=dict)
    market_indicators: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    model_used: ModelProvider = ModelProvider.OPENAI
    processed_at: datetime = Field(default_factory=datetime.utcnow)

class ScenarioProjection(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())
    scenario_name: str = "Mock Scenario"
    description: str = "Mock scenario description"
    probability: float = 0.5
    key_triggers: List[str] = Field(default_factory=list)
    expected_outcomes: List[str] = Field(default_factory=list)
    time_horizon: str = "short_term"
    affected_regions: List[RegionCode] = Field(default_factory=list)

class ScenarioAnalysis(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())
    news_id: str
    base_case: ScenarioProjection = Field(default_factory=ScenarioProjection)
    optimistic_case: Optional[ScenarioProjection] = None
    pessimistic_case: Optional[ScenarioProjection] = None
    alternative_scenarios: List[ScenarioProjection] = Field(default_factory=list)
    confidence: float = 1.0
    model_used: ModelProvider = ModelProvider.OPENAI
    processed_at: datetime = Field(default_factory=datetime.utcnow)

class MultiDimensionAnalysis(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())
    news_id: str
    narrative: NarrativeAnalysis = Field(default_factory=lambda: NarrativeAnalysis(news_id="mock"))
    risk: RiskAnalysis = Field(default_factory=lambda: RiskAnalysis(news_id="mock"))
    sentiment: SentimentAnalysis = Field(default_factory=lambda: SentimentAnalysis(news_id="mock"))
    scenario: ScenarioAnalysis = Field(default_factory=lambda: ScenarioAnalysis(news_id="mock"))
    cross_dimension_insights: List[str] = Field(default_factory=list)
    aggregated_priority_score: float = 0.5
    recommended_actions: List[str] = Field(default_factory=list)
    processed_at: datetime = Field(default_factory=datetime.utcnow)

class DailyReportSection(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())
    section_title: str = "Mock Section"
    section_type: Literal["overview", "highlight", "regional", "risk_alert", "sentiment_trend", "scenario_watch", "market_impact"] = "overview"
    content: str = "Mock content"
    data_points: List[Dict[str, Any]] = Field(default_factory=list)
    priority: int = 5
    related_news_ids: List[str] = Field(default_factory=list)

class DailyReport(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())
    report_id: str
    report_date: datetime
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    language: LanguageCode = LanguageCode.EN
    region_focus: Optional[RegionCode] = None
    sections: List[DailyReportSection] = Field(default_factory=lambda: [DailyReportSection()])
    top_stories: List[RawNewsItem] = Field(default_factory=list)
    risk_alerts: List[RiskAnalysis] = Field(default_factory=list)
    sentiment_summary: Optional[str] = None
    scenario_highlights: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    model_used: ModelProvider = ModelProvider.OPENAI
    generation_latency_ms: Optional[int] = 1

class LLMRequest(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())
    prompt: str
    model: Optional[str] = None
    provider: ModelProvider = ModelProvider.OPENAI
    temperature: float = 0.3
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    stream: bool = False
    system_message: Optional[str] = None
    messages: Optional[List[Dict[str, str]]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class LLMResponse(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())
    content: str = "Mock LLM response"
    provider: ModelProvider = ModelProvider.OPENAI
    model: str = "mock-model"
    usage: Dict[str, int] = Field(default_factory=dict)
    latency_ms: int = 1
    finish_reason: Optional[str] = "stop"
    raw_response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class FallbackRecord(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())
    original_provider: ModelProvider = ModelProvider.OPENAI
    fallback_provider: ModelProvider = ModelProvider.OPENAI
    reason: str = "mock"
    latency_ms: int = 1
    success: bool = True
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PipelineMetrics(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())
    pipeline_name: str
    items_processed: int = 0
    items_failed: int = 0
    avg_latency_ms: float = 0.0
    total_latency_ms: float = 0.0
    fallback_count: int = 0
    translation_count: int = 0
    model_usage: Dict[str, int] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PipelineInput(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())
    items: List[RawNewsItem] = Field(default_factory=list)
    target_language: LanguageCode = LanguageCode.EN
    dimensions: List[AnalysisDimension] = Field(
        default_factory=lambda: [
            AnalysisDimension.NARRATIVE,
            AnalysisDimension.RISK,
            AnalysisDimension.SENTIMENT,
            AnalysisDimension.SCENARIO,
        ]
    )
    region_filter: Optional[List[RegionCode]] = None
    priority_threshold: float = 0.0
    max_items: int = 100
    options: Dict[str, Any] = Field(default_factory=dict)

class PipelineOutput(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())
    input_summary: PipelineInput
    analyzed_items: List[MultiDimensionAnalysis] = Field(default_factory=list)
    failed_items: List[Dict[str, Any]] = Field(default_factory=list)
    metrics: PipelineMetrics
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    daily_report: Optional[DailyReport] = None

class PromptTemplate(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())
    name: str
    template: str
    version: str = "1.0"
    description: Optional[str] = None
    variables: List[str] = Field(default_factory=list)
    default_values: Dict[str, Any] = Field(default_factory=dict)
    system_message: Optional[str] = None
    model_config_override: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

class ProviderConfig(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())
    provider: ModelProvider
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    default_model: str = "mock-model"
    backup_models: List[str] = Field(default_factory=list)
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_backoff_base: float = 2.0
    rate_limit_rpm: int = 60
    priority: int = 1
    enabled: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RouterConfig(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())
    default_provider: ModelProvider = ModelProvider.OPENAI
    fallback_chain: List[ModelProvider] = Field(
        default_factory=lambda: [
            ModelProvider.OPENAI,
            ModelProvider.DEEPSEEK,
            ModelProvider.GEMINI,
        ]
    )
    providers: List[ProviderConfig] = Field(default_factory=list)
    health_check_interval_seconds: int = 60
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout_seconds: int = 300
    load_balancing_strategy: Literal["round_robin", "priority", "least_latency"] = "priority"
    metrics_enabled: bool = True
''', encoding='utf-8')

# 2. Fix pipelines __init__.py
(BASE / 'fzq_ai' / 'pipelines' / 'test_adapter' / '__init__.py').write_text('''from fzq_ai.pipelines.test_adapter.news_pipeline import MockNewsPipeline
from fzq_ai.pipelines.test_adapter.narrative_pipeline import MockNarrativePipeline
from fzq_ai.pipelines.test_adapter.risk_pipeline import MockRiskPipeline
from fzq_ai.pipelines.test_adapter.sentiment_pipeline import MockSentimentPipeline
from fzq_ai.pipelines.test_adapter.scenario_pipeline import MockScenarioPipeline
from fzq_ai.pipelines.test_adapter.daily_report_pipeline import MockDailyReportPipeline

__all__ = [
    "MockNewsPipeline",
    "MockNarrativePipeline",
    "MockRiskPipeline",
    "MockSentimentPipeline",
    "MockScenarioPipeline",
    "MockDailyReportPipeline",
]
''', encoding='utf-8')

# 3. Fix LLM __init__.py
(BASE / 'fzq_ai' / 'llm' / 'test_adapter' / '__init__.py').write_text('''from fzq_ai.llm.test_adapter.llm_router import MockLLMRouter
from fzq_ai.llm.test_adapter.mock_providers import MockOpenAIClient, MockDeepSeekClient, MockGeminiClient

__all__ = [
    "MockLLMRouter",
    "MockOpenAIClient",
    "MockDeepSeekClient",
    "MockGeminiClient",
]
''', encoding='utf-8')

# 4. Fix orchestrator __init__.py
(BASE / 'fzq_ai' / 'orchestrator' / 'test_adapter' / '__init__.py').write_text('''from fzq_ai.orchestrator.test_adapter.task_orchestrator import MockTaskOrchestrator

__all__ = ["MockTaskOrchestrator"]
''', encoding='utf-8')

# 5. Fix task_registry __init__.py
(BASE / 'fzq_ai' / 'task_registry' / 'test_adapter' / '__init__.py').write_text('''from fzq_ai.task_registry.test_adapter.task_registry import (
    Task,
    TaskFilter,
    TaskHistory,
    TaskPriority,
    TaskSchedule,
    TaskStats,
    TaskStatus,
    TaskType,
    MockTaskRegistry,
)

__all__ = [
    "Task",
    "TaskFilter",
    "TaskHistory",
    "TaskPriority",
    "TaskSchedule",
    "TaskStats",
    "TaskStatus",
    "TaskType",
    "MockTaskRegistry",
]
''', encoding='utf-8')

# 6. Add run_daily to MockTaskOrchestrator
task_orch = BASE / 'fzq_ai' / 'orchestrator' / 'test_adapter' / 'task_orchestrator.py'
content = task_orch.read_text(encoding='utf-8')
if 'def run_daily' not in content:
    # insert run_daily before schedule_daily
    content = content.replace(
        '    def schedule_daily(self, callback: Callable) -> None:',
        '''    def run_daily(self, topic: str = '', news_raw_texts: Optional[List[str]] = None) -> DailyReport:
        """Return a fixed DailyReport for daily runs."""
        return self.run(PipelineInput())

    def schedule_daily(self, callback: Callable) -> None:'''
    )
    task_orch.write_text(content, encoding='utf-8')

# 7. Reload and test
import importlib
import fzq_ai.schemas.test_adapter
importlib.reload(fzq_ai.schemas.test_adapter)

from fzq_ai.pipelines.test_adapter import MockNewsPipeline
print('Pipeline import OK')

from fzq_ai.llm.test_adapter import MockLLMRouter
print('LLM router import OK')

from fzq_ai.orchestrator.test_adapter import MockTaskOrchestrator
print('Orchestrator import OK')

from fzq_ai.task_registry.test_adapter import MockTaskRegistry
print('Task registry import OK')

import asyncio
from datetime import datetime
from fzq_ai.schemas.test_adapter import RawNewsItem, NewsSource, LanguageCode, RegionCode, PipelineInput
item = RawNewsItem(id='1', title='t', content='c', source=NewsSource(name='s'), published_at=datetime.utcnow(), language=LanguageCode.EN, region=RegionCode.GLOBAL)
inp = PipelineInput(items=[item])
out = asyncio.run(MockNewsPipeline().run(inp))
print('Pipeline run OK', out.metrics.pipeline_name)

orch = MockTaskOrchestrator()
report = orch.run(inp)
print('Orchestrator run OK', report.report_id)

report2 = orch.run_daily()
print('Orchestrator run_daily OK', report2.report_id)

router = MockLLMRouter(config=fzq_ai.schemas.test_adapter.RouterConfig())
resp = asyncio.run(router.generate(fzq_ai.schemas.test_adapter.LLMRequest(prompt='hi')))
print('LLM router generate OK', resp.content)

print('ALL CHECKS PASSED')
