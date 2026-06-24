"""
fzq_ai.utils.logger

缁熶竴鏃ュ織閰嶇疆鍏ュ彛 (v2.5)锛?
- setup_logging() 鍦ㄥ簲鐢ㄥ叆鍙ｈ皟鐢ㄤ竴娆?
- 鍚勬ā鍧椾娇鐢?logging.getLogger(__name__)
- 鏀?寔鎺у埗鍙?+ 鏂囦欢杈撳嚭
- 鎻愪緵 @log_time 瑁呴グ鍣ㄨ?褰曞嚱鏁拌€楁椂
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


def setup_logging(
    level: Optional[int] = None,
    log_dir: Optional[str] = None,
) -> None:
    """
    鍒濆?鍖栧叏灞€鏃ュ織閰嶇疆銆?

    Args:
        level: 鏃ュ織绛夌骇锛圢one 鏃朵娇鐢?settings.log_level锛?
        log_dir: 鏃ュ織鏂囦欢鐩?綍锛圢one 鏃朵娇鐢ㄩ」鐩?牴鐩?綍涓嬬殑 logs/锛?
    """
    if level is None:
        level_name: str = getattr(settings, "log_level", "INFO").upper()
        level = getattr(logging, level_name, logging.INFO)

    # 鏍煎紡
    format_str: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    formatter: logging.Formatter = logging.Formatter(
        fmt=format_str,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root: logging.Logger = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    # 鎺у埗鍙?handler
    console: logging.StreamHandler = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    root.addHandler(console)

    # 鏂囦欢 handler
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

    # 闄嶄綆绗?笁鏂瑰簱鏃ュ織鍣?煶
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    鑾峰彇妯″潡鏃ュ織鍣ㄣ€?

    Args:
        name: 閫氬父浼犲叆 __name__

    Returns:
        logging.Logger 瀹炰緥
    """
    return logging.getLogger(name)


def log_time(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    瑁呴グ鍣?細璁板綍琚??楗板嚱鏁扮殑鎵ц?鑰楁椂銆?

    鐢ㄤ簬鍏抽敭鍑芥暟锛圥ipeline銆丱rchestrator銆丩LM 璋冪敤锛夌殑鑰楁椂缁熻?銆?

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
            logger.info(f"{func.__qualname__} 瀹屾垚, 鑰楁椂 {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start
            logger.error(
                f"{func.__qualname__} 澶辫触, 鑰楁椂 {elapsed:.3f}s, 閿欒?: {e}"
            )
            raise

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = logging.getLogger(func.__module__)
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            elapsed = time.time() - start
            logger.info(f"{func.__qualname__} 瀹屾垚, 鑰楁椂 {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start
            logger.error(
                f"{func.__qualname__} 澶辫触, 鑰楁椂 {elapsed:.3f}s, 閿欒?: {e}"
            )
            raise

    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return wrapper


# 妯″潡瀵煎叆鏃惰嚜鍔ㄥ垵濮嬪寲鏃ュ織
setup_logging()

