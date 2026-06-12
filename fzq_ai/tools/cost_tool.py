"""
fzq_ai.tools.cost_tool

费用计算工具：
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


async def estimate_trip_cost(
    distance_km: float,
    cost_per_km: float = 0.25,
    base_fee: float = 1.0,
) -> ToolResult[Dict[str, Any]]:
    """
    根据距离估算出行费用。
    默认参数：
    - cost_per_km: 每公里费用
    - base_fee: 基础费用
    """
    try:
        if distance_km < 0:
            raise ValueError("distance_km must be >= 0")

        total_cost = round(base_fee + distance_km * cost_per_km, 2)

        result = {
            "distance_km": distance_km,
            "cost_per_km": cost_per_km,
            "base_fee": base_fee,
            "total_cost": total_cost,
        }

        return ToolResult(
            success=True,
            data=result,
            metadata={"tool": "estimate_trip_cost"}
        )

    except Exception as e:
        logger.error("estimate_trip_cost failed: %s", e, exc_info=True)
        return ToolResult(
            success=False,
            error=str(e),
            metadata={"tool": "estimate_trip_cost"}
        )
