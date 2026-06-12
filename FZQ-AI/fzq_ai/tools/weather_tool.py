"""
fzq_ai.tools.weather_tool

天气查询工具（示范）：
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


async def get_weather(location: str) -> ToolResult[Dict[str, Any]]:
    """
    示例工具：查询天气信息。

    你可以将内部逻辑替换为实际 API 调用。
    """
    try:
        # TODO: 替换为你的实际天气 API 调用
        # 示例：
        # weather = await weather_api.get_weather(location)
        weather = {
            "location": location,
            "temperature": 22,
            "condition": "Sunny",
            "humidity": 55,
        }  # 占位

        return ToolResult(
            success=True,
            data=weather,
            metadata={"tool": "get_weather", "location": location}
        )

    except Exception as e:
        logger.error("get_weather failed: %s", e, exc_info=True)
        return ToolResult(
            success=False,
            error=str(e),
            metadata={"tool": "get_weather", "location": location}
        )
