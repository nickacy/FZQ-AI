from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ModelProvider(str, Enum):
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"


class DailyReportSection(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(default="mock-section-123", description="Unique identifier")
    title: str = Field(default="Mock Section Title", description="Section title")
    content: str = Field(default="Mock section content.", description="Section content")
    order: int = Field(default=1, description="Section order")
    summary: Optional[str] = Field(default="Mock summary", description="Section summary")


class DailyReport(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(default="mock-report-123", description="Unique identifier")
    date: str = Field(default="2024-01-01", description="Report date")
    sections: List[DailyReportSection] = Field(default_factory=list, description="Report sections")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Report metadata")
    generated_at: Optional[datetime] = Field(default=datetime(2024, 1, 1, 0, 0, 0), description="Generation timestamp")


class PipelineInput(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(default="mock-input-123", description="Unique identifier")
    data: Dict[str, Any] = Field(default_factory=dict, description="Input data")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Pipeline parameters")
    timestamp: Optional[datetime] = Field(default=datetime(2024, 1, 1, 0, 0, 0), description="Input timestamp")


class PipelineOutput(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(default="mock-output-123", description="Unique identifier")
    input_id: str = Field(default="mock-input-123", description="Reference to input")
    results: Dict[str, Any] = Field(default_factory=dict, description="Output results")
    status: str = Field(default="success", description="Pipeline status")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    timestamp: Optional[datetime] = Field(default=datetime(2024, 1, 1, 0, 0, 0), description="Output timestamp")


class PipelineMetrics(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(default="mock-metrics-123", description="Unique identifier")
    pipeline_id: str = Field(default="mock-pipeline-123", description="Pipeline reference")
    latency_ms: Optional[float] = Field(default=1.0, description="Latency in milliseconds")
    tokens_used: Optional[int] = Field(default=1, description="Tokens consumed")
    cost: Optional[float] = Field(default=0.001, description="Estimated cost")
    success: bool = Field(default=True, description="Success flag")


class LLMRequest(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(default="mock-request-123", description="Unique identifier")
    model: str = Field(default="mock-model", description="Model name")
    messages: List[Dict[str, str]] = Field(default_factory=list, description="Message list")
    temperature: Optional[float] = Field(default=1.0, ge=0, le=2, description="Temperature")
    max_tokens: Optional[int] = Field(default=1, gt=0, description="Max tokens")
    timeout: Optional[float] = Field(default=1.0, description="Timeout in seconds")


class LLMResponse(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(default="mock-response-123", description="Unique identifier")
    request_id: str = Field(default="mock-request-123", description="Reference to request")
    content: str = Field(default="Mock response content.", description="Response content")
    finish_reason: Optional[str] = Field(default="stop", description="Finish reason")
    usage: Dict[str, Any] = Field(default_factory=dict, description="Token usage")
    latency_ms: Optional[float] = Field(default=1.0, description="Latency in milliseconds")


class ProviderConfig(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    provider: ModelProvider = Field(default=ModelProvider.DEEPSEEK, description="Model provider")
    api_key: Optional[str] = Field(default="mock-api-key", description="API key")
    base_url: Optional[str] = Field(default="https://mock.example.com", description="Base URL")
    timeout: Optional[float] = Field(default=1.0, description="Timeout in seconds")
    retries: int = Field(default=1, description="Retry count")


class RouterConfig(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    default_provider: ModelProvider = Field(default=ModelProvider.DEEPSEEK, description="Default provider")
    provider_configs: List[ProviderConfig] = Field(default_factory=list, description="Provider configs")
    fallback_providers: List[ModelProvider] = Field(default_factory=list, description="Fallback providers")
    timeout: Optional[float] = Field(default=1.0, description="Timeout in seconds")


class FallbackRecord(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(default="mock-fallback-123", description="Unique identifier")
    original_provider: ModelProvider = Field(default=ModelProvider.DEEPSEEK, description="Original provider")
    fallback_provider: ModelProvider = Field(default=ModelProvider.OPENAI, description="Fallback provider")
    reason: str = Field(default="Mock fallback reason.", description="Fallback reason")
    timestamp: Optional[datetime] = Field(default=datetime(2024, 1, 1, 0, 0, 0), description="Fallback timestamp")


class PromptTemplate(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(default="mock-template-123", description="Unique identifier")
    name: str = Field(default="Mock Template", description="Template name")
    template: str = Field(default="Mock prompt template: {{ variable }}.", description="Prompt template")
    variables: List[str] = Field(default_factory=list, description="Template variables")
    description: Optional[str] = Field(default="Mock template description.", description="Template description")
