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
) -> ToolResult[Dict[str, Any]]:
    """
    """
    try:
        if distance_km < 0:
            raise ValueError("distance_km must be >= 0")

        result = {
            "distance_km": distance_km,
            "cost_per_km": cost_per_km,
            "base_fee": base_fee,
            "total_cost": total_cost,

        return ToolResult(
            success=True, data=result, metadata={"tool": "estimate_trip_cost"}

    except Exception as e:
        return ToolResult(
            success=False, error=str(e), metadata={"tool": "estimate_trip_cost"}
        )
