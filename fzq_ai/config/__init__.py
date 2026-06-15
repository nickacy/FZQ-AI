# fzq_ai/config/__init__.py
"""
配置入口：多源加载（环境变量 > .env > 配置文件默认值）

加载顺序：
1. 首先尝试加载 config.yaml（默认值）
2. 然后加载 .env（覆盖）
3. 最后读取环境变量（最高优先级）

当缺少关键 API Key 时：不崩溃，返回空字符串并提供明确提示。
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from dotenv import load_dotenv
    _DOTENV_LOADED = False

    def _ensure_dotenv() -> None:
        global _DOTENV_LOADED
        if not _DOTENV_LOADED:
            load_dotenv(override=True)
            _DOTENV_LOADED = True
except ImportError:
    def _ensure_dotenv() -> None:
        pass


# ── 配置文件路径 ──────────────────────────────────────────────
_CONFIG_DIR = Path(__file__).parent
_PROJECT_ROOT = _CONFIG_DIR.parent.parent  # FZQ-AI 项目根目录


def _load_config_yaml() -> Dict[str, Any]:
    """加载 config.yaml / config.json，返回 dict。"""
    config: Dict[str, Any] = {}

    # 尝试 config.yaml（实际是 JSON 格式）
    yaml_path = _CONFIG_DIR / "config.yaml"
    if yaml_path.exists():
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                config.update(json.load(f))
        except (json.JSONDecodeError, OSError):
            pass

    # 尝试 config.json（项目根目录）
    json_path = _PROJECT_ROOT / "config.json"
    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                config.update(json.load(f))
        except (json.JSONDecodeError, OSError):
            pass

    return config


def _check_missing_keys() -> list[str]:
    """检查缺少的关键 API Key，返回缺失列表。"""
    missing: list[str] = []
    keys_to_check = {
        "DEEPSEEK_API_KEY": "DeepSeek LLM API Key",
        "OPENAI_API_KEY": "OpenAI API Key",
        "GEMINI_API_KEY": "Google Gemini API Key",
        "NEWSAPI_KEY": "NewsAPI Key (新闻抓取)",
    }
    for env_var, desc in keys_to_check.items():
        val = os.getenv(env_var, "")
        if not val or val.startswith("your-") or val.startswith("sk-your-"):
            missing.append(f"{env_var} ({desc})")
    return missing


# ── 初始化 ────────────────────────────────────────────────────
_ensure_dotenv()

# API Keys
DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

NEWSAPI_KEY: str = os.getenv("NEWSAPI_KEY", "")

# 日志级别
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# 版本信息
VERSION: str = "2.5.0"
BUILD_TIME: str = "2026-06-15"


def get_config() -> Dict[str, Any]:
    """
    获取完整配置（合并所有来源）。

    Returns:
        包含所有配置项的 dict
    """
    config: Dict[str, Any] = _load_config_yaml()

    # RSS 源配置
    if "rss_sources" not in config:
        config["rss_sources"] = _get_default_rss_sources()

    # API Keys（环境变量优先级最高）
    config["api_keys"] = {
        "deepseek": DEEPSEEK_API_KEY,
        "openai": OPENAI_API_KEY,
        "gemini": GEMINI_API_KEY,
        "newsapi": NEWSAPI_KEY,
    }

    config["version"] = VERSION
    config["log_level"] = LOG_LEVEL

    # 检查缺失的 Key
    missing = _check_missing_keys()
    if missing:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"缺少以下 API Key: {', '.join(missing)}")
        logger.warning("请在 .env 文件或环境变量中配置相应的 API Key")
        config["missing_keys"] = missing

    return config


def _get_default_rss_sources() -> list[Dict[str, Any]]:
    """默认 RSS 源列表（如果配置文件未提供）。"""
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
