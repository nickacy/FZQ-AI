"""
fzq_ai.utils.logger

统一日志配置入口：
- setup_logging() 在应用入口调用一次
- 各模块使用 logging.getLogger(__name__)
"""

from __future__ import annotations

import logging
import sys

from fzq_ai.config.settings import settings


def setup_logging(level: int | None = None) -> None:
    """
    初始化全局日志配置。
    如果未显式传入 level，则使用 settings.log_level。
    """

    # 解析日志等级
    if level is None:
        level_name = settings.log_level.upper()
        level = getattr(logging, level_name, logging.INFO)

    # 日志格式
    format_str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    logging.basicConfig(
        stream=sys.stdout,
        level=level,
        format=format_str,
    )

    # 降低第三方库日志等级（避免噪音）
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    # 你可以在这里添加更多第三方库降噪
    # logging.getLogger("some_library").setLevel(logging.WARNING)
