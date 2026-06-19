"""
FZQ-AI Core — 全局状态与配置管理
"""
import os
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class FZQConfig(BaseModel):
    """全局配置"""
    model_config = ConfigDict(frozen=False)

    test_mode: bool = Field(default=False)
    default_language: str = "en"
    default_region: str = "global"
    max_concurrent_llm_requests: int = 10
    translation_timeout_seconds: int = 30
    analysis_timeout_seconds: int = 60
    report_timeout_seconds: int = 120
    metrics_enabled: bool = True
    log_level: str = "INFO"
    cache_dir: Optional[str] = None
    data_dir: Optional[str] = None

    @classmethod
    def from_env(cls) -> "FZQConfig":
        return cls(
            test_mode=os.environ.get("FZQAI_TEST_MODE", "0") == "1",
            default_language=os.environ.get("FZQAI_DEFAULT_LANG", "en"),
            default_region=os.environ.get("FZQAI_DEFAULT_REGION", "global"),
            max_concurrent_llm_requests=int(os.environ.get("FZQAI_MAX_CONCURRENT", "10")),
            translation_timeout_seconds=int(os.environ.get("FZQAI_TRANS_TIMEOUT", "30")),
            analysis_timeout_seconds=int(os.environ.get("FZQAI_ANALYSIS_TIMEOUT", "60")),
            report_timeout_seconds=int(os.environ.get("FZQAI_REPORT_TIMEOUT", "120")),
            metrics_enabled=os.environ.get("FZQAI_METRICS", "1") == "1",
            log_level=os.environ.get("FZQAI_LOG_LEVEL", "INFO"),
            cache_dir=os.environ.get("FZQAI_CACHE_DIR"),
            data_dir=os.environ.get("FZQAI_DATA_DIR"),
        )
