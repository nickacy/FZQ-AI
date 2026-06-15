"""
fzq_ai.tools.attractions_tool

景点查询工具：
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


async def get_attractions_by_suburb(suburb: str) -> ToolResult[List[Dict[str, Any]]]:
    """
    根据 suburb 返回景点列表。
    你可以将内部逻辑替换为实际数据源（JSON / API / DB）。
    """
    try:
        # TODO: 替换为你的实际 attractions 数据加载逻辑
        # 示例占位数据：
        attractions = [
            {
                "name": "Sample Park",
                "category": "Park",
                "lat": -33.123,
                "lon": 151.123,
                "description": "A beautiful local park.",
                "suburb": suburb,
            },
            {
                "name": "Sample Museum",
                "category": "Museum",
                "lat": -33.456,
                "lon": 151.456,
                "description": "A small but interesting museum.",
                "suburb": suburb,
            },
        ]

        return ToolResult(
            success=True,
            data=attractions,
            metadata={"tool": "get_attractions_by_suburb", "suburb": suburb},
        )

    except Exception as e:
        logger.error("get_attractions_by_suburb failed: %s", e, exc_info=True)
        return ToolResult(
            success=False,
            error=str(e),
            metadata={"tool": "get_attractions_by_suburb", "suburb": suburb},
        )
