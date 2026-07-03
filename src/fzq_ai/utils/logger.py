"""
fzq_ai.utils.logger

统一日志系统 (v2.5)
- setup_logging() 在主入口调用一次即可
- 各模块通过 get_logger(__name__) 获取 logger
- 支持: 控制台 + 文件双输出
- 装饰器: @log_time 计时装饰器
"""

from __future__ import annotations

import functools
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

from fzq_ai.config.global_settings import settings

_logger_initialized: bool = False


def ensure_logging_initialized() -> None:
    """Idempotently initialise global logging. Safe to call multiple times."""
    global _logger_initialized
    if _logger_initialized:
        return
    _logger_initialized = True
    setup_logging()


def setup_logging(
    level: Optional[int] = None,
    log_dir: Optional[str] = None,
) -> None:
    """
    初始化全局日志系统。

    Args:
        level: 可选日志级别，None 则使用 settings.log_level
        log_dir: 可选日志目录，None 则使用项目根目录下的 logs/
    """
    if level is None:
        level_name: str = getattr(settings, "log_level", "INFO").upper()
        level = getattr(logging, level_name, logging.INFO)

    # 格式
    format_str: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    formatter: logging.Formatter = logging.Formatter(
        fmt=format_str,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root: logging.Logger = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    # 控制台 handler
    console: logging.StreamHandler = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    root.addHandler(console)

    # 文件 handler
    if log_dir is None:
        project_root: Path = Path(__file__).parent.parent
        log_dir = str(project_root / "logs")
    os.makedirs(log_dir, exist_ok=True)

    today: str = datetime.now(timezone.utc).strftime("%Y%m%d")
    log_file: str = os.path.join(log_dir, f"fzq_ai_{today}.log")

    file_handler: logging.FileHandler = logging.FileHandler(
        log_file, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    # 抑制第三方库噪音
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    获取模块级 logger。

    Args:
        name: 通常传入 __name__

    Returns:
        logging.Logger 实例
    """
    ensure_logging_initialized()
    return logging.getLogger(name)


def log_time(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    计时装饰器，用于 pipeline / orchestrator / LLM 调用计时。

    Usage:
        @log_time
        def my_pipeline_run(self, topic: str) -> ServiceResult:
            ...
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger: logging.Logger = logging.getLogger(func.__module__)
        start: float = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed: float = time.time() - start
            logger.info(f"{func.__qualname__} 完成 耗时: {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start
            logger.error(
                f"{func.__qualname__} 失败 耗时: {elapsed:.3f}s, 错误: {e}"
            )
            raise

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = logging.getLogger(func.__module__)
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            elapsed = time.time() - start
            logger.info(f"{func.__qualname__} 完成 耗时: {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start
            logger.error(
                f"{func.__qualname__} 失败 耗时: {elapsed:.3f}s, 错误: {e}"
            )
            raise

    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return wrapper


# 不再在 import 时自动调用 setup_logging()
# 改为在 get_logger() 首次调用时懒初始化
