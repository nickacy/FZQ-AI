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
) -> None:
    """

    """
    if level is None:

    # 格式

    # 控制台 handler

    # 文件 handler
    if log_dir is None:

    # 降低第三方库日志噪音

def get_logger(name: str) -> logging.Logger:
    """

    """
    return logging.getLogger(name)

def log_time(func: Callable[..., Any]) -> Callable[..., Any]:
    """

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
            raise

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return wrapper

# 模块导入时自动初始化日志
setup_logging()
