"""
fzq_ai.logging.logger

统一日志系统：
- 所有模块使用相同格式
- 自动输出到控制台
- 可扩展输出到文件 / ELK / Grafana Loki
"""

from __future__ import annotations

import logging
import sys
from typing import Optional

def setup_logging(level: int = logging.INFO) -> None:
    """
    """

# 初始化日志（import 时自动执行）
setup_logging()
