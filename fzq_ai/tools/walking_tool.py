"""
fzq_ai.tools.walking_tool

步行时间计算工具：
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


async def estimate_walking_time(distance_meters: float) -> ToolResult[Dict[str, Any]]:
    """
    根据距离估算步行时间（分钟）。
    默认步行速度：4.5 km/h（= 75 m/min）
    """
    try:
        if distance_meters < 0:
            raise ValueError("distance_meters must be >= 0")

        # 步行速度：75 米/分钟
        walking_speed_m_per_min = 75
        minutes = round(distance_meters / walking_speed_m_per_min, 1)

        result = {
            "distance_meters": distance_meters,
            "estimated_minutes": minutes,
            "walking_speed_m_per_min": walking_speed_m_per_min,
        }

        return ToolResult(
            success=True,
            data=result,
            metadata={"tool": "estimate_walking_time"}
        )

    except Exception as e:
        logger.error("estimate_walking_time failed: %s", e, exc_info=True)
        return ToolResult(
            success=False,
            error=str(e),
            metadata={"tool": "estimate_walking_time"}
        )
