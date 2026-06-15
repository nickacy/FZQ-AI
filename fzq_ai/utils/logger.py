"""
fzq_ai.utils.logger

统一日志配置入口 (v2.5)：
- setup_logging() 在应用入口调用一次
- 各模块使用 logging.getLogger(__name__)
- 支持控制台 + 文件输出
- 提供 @log_time 装饰器记录函数耗时
"""

from __future__ import annotations

import functools
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

from fzq_ai.config.settings import settings


def setup_logging(
    level: Optional[int] = None,
    log_dir: Optional[str] = None,
) -> None:
    """
    初始化全局日志配置。

    Args:
        level: 日志等级（None 时使用 settings.log_level）
        log_dir: 日志文件目录（None 时使用项目根目录下的 logs/）
    """
    if level is None:
        level_name: str = settings.log_level.upper()
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

    today: str = datetime.now().strftime("%Y%m%d")
    log_file: str = os.path.join(log_dir, f"fzq_ai_{today}.log")

    file_handler: logging.FileHandler = logging.FileHandler(
        log_file, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    # 降低第三方库日志噪音
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    获取模块日志器。

    Args:
        name: 通常传入 __name__

    Returns:
        logging.Logger 实例
    """
    return logging.getLogger(name)


def log_time(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    装饰器：记录被装饰函数的执行耗时。

    用于关键函数（Pipeline、Orchestrator、LLM 调用）的耗时统计。

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
            logger.info(f"{func.__qualname__} 完成, 耗时 {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start
            logger.error(
                f"{func.__qualname__} 失败, 耗时 {elapsed:.3f}s, 错误: {e}"
            )
            raise

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = logging.getLogger(func.__module__)
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            elapsed = time.time() - start
            logger.info(f"{func.__qualname__} 完成, 耗时 {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start
            logger.error(
                f"{func.__qualname__} 失败, 耗时 {elapsed:.3f}s, 错误: {e}"
            )
            raise

    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return wrapper


# 模块导入时自动初始化日志
setup_logging()
