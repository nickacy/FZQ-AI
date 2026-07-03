"""
FZQ‑AI 全局配置中心 (V24)

职责：
1. 加载 config.yaml / config.json（声明性配置）
2. 提供 API Keys / RSS / 日志级别 / 版本号
3. 提供统一 get_config() 接口
4. 与 fzq_ai.config.global_settings（模型优先级 + 任务覆盖）并存，不冲突

注意：.env 加载已统一移至应用入口（main.py / app.py），
      本模块不再调用 load_dotenv()，避免重复加载和不可预测的覆盖。
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

import yaml

# Re-export dataclass-style config types so callers can use either:
#   - dict-style:  from fzq_ai.config import get_config           # -> dict
#   - dataclass:   from fzq_ai.config import AppConfig, ConfigManager
# The dataclass API is intended for typed config access (e.g. tests,
# future plugins) — both styles load from the same env / yaml sources.
from fzq_ai.config.modern_config import (  # noqa: F401
    AppConfig,
    ProviderConfig,
    CacheConfig,
    LoggingConfig,
    PipelineConfig,
    ConfigManager,
    init_config,
    get_config as get_typed_config,  # alias to avoid shadowing the dict-style get_config below
)

# ------------------------------------------------------------
# 1. 配置文件路径
# ------------------------------------------------------------
_CONFIG_DIR = Path(__file__).parent
_PROJECT_ROOT = _CONFIG_DIR.parent.parent


def _read_version() -> str:
    """Read VERSION from VERSION.txt, falling back to a hard-coded default."""
    version_file = _PROJECT_ROOT / "VERSION.txt"
    if version_file.exists():
        try:
            return version_file.read_text(encoding="utf-8").strip()
        except Exception:
            pass
    return "24.0.0"


# ------------------------------------------------------------
# 2. 加载 config.yaml / config.json
# ------------------------------------------------------------
def _load_config_yaml() -> Dict[str, Any]:
    config: Dict[str, Any] = {}

    yaml_path = _CONFIG_DIR / "config.yaml"
    if yaml_path.exists():
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                config.update(yaml.safe_load(f))
        except Exception:
            pass

    json_path = _PROJECT_ROOT / "config.json"
    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                config.update(json.load(f))
        except Exception:
            pass

    return config


# ------------------------------------------------------------
# 3. 检查缺失 API Keys
# ------------------------------------------------------------
def _check_missing_keys() -> list[str]:
    missing: list[str] = []
    keys_to_check = {
        "DEEPSEEK_API_KEY": "DeepSeek API Key",
        "OPENAI_API_KEY": "OpenAI API Key",
        "GEMINI_API_KEY": "Gemini API Key",
        "NEWSAPI_KEY": "NewsAPI Key",
    }
    for env_var, desc in keys_to_check.items():
        val = os.getenv(env_var, "")
        if not val or val.startswith("your-") or val.startswith("sk-your-"):
            missing.append(f"{env_var} ({desc})")
    return missing


# ------------------------------------------------------------
# 4. API Keys（从已加载的环境变量读取）
# ------------------------------------------------------------
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Source of truth: VERSION.txt (single source for version string)
VERSION = _read_version()
BUILD_TIME = "2026-07-03"


# ------------------------------------------------------------
# 5. get_config()：统一配置入口
# ------------------------------------------------------------
def get_config() -> Dict[str, Any]:
    config: Dict[str, Any] = _load_config_yaml()

    # RSS 默认源
    if "rss_sources" not in config:
        config["rss_sources"] = _get_default_rss_sources()

    # API Keys
    config["api_keys"] = {
        "deepseek": DEEPSEEK_API_KEY,
        "openai": OPENAI_API_KEY,
        "gemini": GEMINI_API_KEY,
        "newsapi": NEWSAPI_KEY,
    }

    config["version"] = VERSION
    config["log_level"] = LOG_LEVEL

    # 缺失 Key 警告
    missing = _check_missing_keys()
    if missing:
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"缺少以下 API Key: {', '.join(missing)}")
        config["missing_keys"] = missing

    return config


# ------------------------------------------------------------
# 6. 默认 RSS 源
# ------------------------------------------------------------
def _get_default_rss_sources() -> list[Dict[str, Any]]:
    return [
        {
            "id": "bbc",
            "name": "BBC World",
            "region": "western",
            "language": "en",
            "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
        },
        {
            "id": "reuters",
            "name": "Reuters World",
            "region": "western",
            "language": "en",
            "url": "https://feeds.reuters.com/Reuters/worldNews",
        },
        {
            "id": "aljazeera",
            "name": "Al Jazeera",
            "region": "middle_east",
            "language": "en",
            "url": "https://www.aljazeera.com/xml/rss/all.xml",
        },
        {
            "id": "nhk",
            "name": "NHK Japan",
            "region": "east_asia",
            "language": "ja",
            "url": "https://www3.nhk.or.jp/rss/news/cat0.xml",
        },
    ]
