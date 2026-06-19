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

    id: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")
    order: int = Field(default=0, description="Section order")
    summary: Optional[str] = Field(default=None, description="Section summary")


class DailyReport(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(..., description="Unique identifier")
    date: str = Field(..., description="Report date")
    sections: List[DailyReportSection] = Field(default_factory=list, description="Report sections")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Report metadata")
    generated_at: Optional[datetime] = Field(default=None, description="Generation timestamp")


class PipelineInput(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(..., description="Unique identifier")
    data: Dict[str, Any] = Field(default_factory=dict, description="Input data")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Pipeline parameters")
    timestamp: Optional[datetime] = Field(default=None, description="Input timestamp")


class PipelineOutput(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(..., description="Unique identifier")
    input_id: str = Field(..., description="Reference to input")
    results: Dict[str, Any] = Field(default_factory=dict, description="Output results")
    status: str = Field(default="pending", description="Pipeline status")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    timestamp: Optional[datetime] = Field(default=None, description="Output timestamp")


class PipelineMetrics(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(..., description="Unique identifier")
    pipeline_id: str = Field(..., description="Pipeline reference")
    latency_ms: Optional[float] = Field(default=None, description="Latency in milliseconds")
    tokens_used: Optional[int] = Field(default=None, description="Tokens consumed")
    cost: Optional[float] = Field(default=None, description="Estimated cost")
    success: bool = Field(default=True, description="Success flag")


class LLMRequest(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(..., description="Unique identifier")
    model: str = Field(..., description="Model name")
    messages: List[Dict[str, str]] = Field(default_factory=list, description="Message list")
    temperature: Optional[float] = Field(default=0.7, ge=0, le=2, description="Temperature")
    max_tokens: Optional[int] = Field(default=1024, gt=0, description="Max tokens")
    timeout: Optional[float] = Field(default=30.0, description="Timeout in seconds")


class LLMResponse(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(..., description="Unique identifier")
    request_id: str = Field(..., description="Reference to request")
    content: str = Field(..., description="Response content")
    finish_reason: Optional[str] = Field(default=None, description="Finish reason")
    usage: Dict[str, Any] = Field(default_factory=dict, description="Token usage")
    latency_ms: Optional[float] = Field(default=None, description="Latency in milliseconds")


class ProviderConfig(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    provider: ModelProvider = Field(..., description="Model provider")
    api_key: Optional[str] = Field(default=None, description="API key")
    base_url: Optional[str] = Field(default=None, description="Base URL")
    timeout: Optional[float] = Field(default=30.0, description="Timeout in seconds")
    retries: int = Field(default=3, description="Retry count")


class RouterConfig(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    default_provider: ModelProvider = Field(..., description="Default provider")
    provider_configs: List[ProviderConfig] = Field(default_factory=list, description="Provider configs")
    fallback_providers: List[ModelProvider] = Field(default_factory=list, description="Fallback providers")
    timeout: Optional[float] = Field(default=30.0, description="Timeout in seconds")


class FallbackRecord(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(..., description="Unique identifier")
    original_provider: ModelProvider = Field(..., description="Original provider")
    fallback_provider: ModelProvider = Field(..., description="Fallback provider")
    reason: str = Field(..., description="Fallback reason")
    timestamp: Optional[datetime] = Field(default=None, description="Fallback timestamp")


class PromptTemplate(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Template name")
    template: str = Field(..., description="Prompt template")
    variables: List[str] = Field(default_factory=list, description="Template variables")
    description: Optional[str] = Field(default=None, description="Template description")
