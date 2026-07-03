# src/fzq_ai/agents/aop_blackboard.py
# V24 — Agent AOP Blackboard Sync
# 不修改现有 BaseAgent 内部逻辑，只在外层增加自动同步能力。

from __future__ import annotations
import time
from typing import Any, Callable, Awaitable, Dict

# 这里假设你已有 Blackboard，如果在其他模块，请按实际路径导入
from fzq_ai.orchestrator.blackboard import Blackboard


def auto_blackboard_sync(agent_method: Callable[..., Awaitable[Any]]):
    """
    装饰器：自动将 Agent 的输入输出同步到 Blackboard。
    不侵入业务逻辑，只在方法外层记录数据。
    """

    async def wrapper(self, *args, **kwargs):
        agent_name = getattr(self, "name", self.__class__.__name__)

        # 约定：第一个参数是 AgentContext 或 AgentTask
        input_payload: Any = args[0] if args else None

        input_key = f"agents.{agent_name}.input"
        output_key = f"agents.{agent_name}.output"

        # 1. 自动记录输入
        Blackboard.write(input_key, {
            "payload": repr(input_payload),
            "ts": time.time(),
        })

        # 2. 执行原方法
        result = await agent_method(self, *args, **kwargs)

        # 3. 自动记录输出
        Blackboard.write(output_key, {
            "result": result,
            "ts": time.time(),
        })

        # 4. 记录时序关系（用于前端 / APP 画协作链）
        timeline: list[Dict[str, Any]] = Blackboard.read("sys.timeline", [])
        timeline.append({
            "agent": agent_name,
            "from": input_key,
            "to": output_key,
            "ts": time.time(),
        })
        Blackboard.write("sys.timeline", timeline)

        return result

    return wrapper
