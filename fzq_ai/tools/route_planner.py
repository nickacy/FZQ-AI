"""
fzq_ai.tools.route_planner

路线规划工具（示范）：
- 使用 ToolResult 作为统一返回结构
- 内置日志
- 内置错误处理
- 完全兼容未来的 ServiceResult / Pipeline 架构
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from fzq_ai.domain.models import ToolResult
from fzq_ai.domain.errors import ToolExecutionError

logger = logging.getLogger(__name__)


async def plan_route(start: str, end: str) -> ToolResult[Dict[str, Any]]:
    """
    示例工具：规划从 start 到 end 的路线。

    你可以将内部逻辑替换为实际路线规划算法或 API。
    """
    try:
        # TODO: 替换为你的实际路线规划逻辑
        # 示例：
        # route = await route_api.get_route(start, end)
        route = {
            "start": start,
            "end": end,
            "steps": [
                f"Walk from {start} station to platform 2",
                "Take Line T1 towards Central",
                f"Arrive at {end} station",
            ],
            "estimated_minutes": 32,
        }  # 占位

        return ToolResult(
            success=True,
            data=route,
            metadata={"tool": "plan_route", "start": start, "end": end}
        )

    except Exception as e:
        logger.error("plan_route failed: %s", e, exc_info=True)
        return ToolResult(
            success=False,
            error=str(e),
            metadata={"tool": "plan_route", "start": start, "end": end}
        )
