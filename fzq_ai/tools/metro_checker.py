"""
fzq_ai.tools.metro_checker

地铁线路查询工具（示范）：
- 使用 ToolResult 作为统一返回结构
- 内置日志
- 内置错误处理
- 完全兼容未来的 ServiceResult / Pipeline 架构
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from fzq_ai.domain.models import ToolResult
from fzq_ai.domain.errors import ToolExecutionError

logger = logging.getLogger(__name__)


async def check_metro_status(line: str) -> ToolResult[Dict[str, Any]]:
    """
    示例工具：查询地铁线路状态。

    你可以将内部逻辑替换为实际 API 调用。
    """
    try:
        # TODO: 替换为你的实际 API 调用
        # 示例：
        # status = await metro_api.get_status(line)
        status = {
            "line": line,
            "status": "operational",
            "delay_minutes": 0,
        }  # 占位

        return ToolResult(
            success=True,
            data=status,
            metadata={"tool": "check_metro_status", "line": line},
        )

    except Exception as e:
        logger.error("check_metro_status failed: %s", e, exc_info=True)
        return ToolResult(
            success=False,
            error=str(e),
            metadata={"tool": "check_metro_status", "line": line},
        )
