# src/fzq_ai/agents/news_center_agent.py
"""V24 — NewsCenterAgent: 个人全球信息新闻中心总控。

- 拉取多源多语言原始信息（占位：ctx.raw_input 视为已获取的多源文本）
- 并行调度 4 个任务子 agent（policy_brief / risk_scan / opinion_landscape / multisource_merge）
- 聚合成"广泛、平衡、尽量无偏"的个人情报视图
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

from fzq_ai.agents.base import AgentContext, AgentResult


# Default 4 sub-agents composing the "news center" view
DEFAULT_SUB_AGENTS: List[str] = [
    "zh_policy_brief",
    "zh_risk_scan",
    "zh_opinion_landscape",
    "zh_multisource_merge",
]


class NewsCenterAgent:
    """Aggregates downstream intelligence agents into a single personal-intel view.

    NOT a BaseAgent subclass — NewsCenterAgent is a *coordinator* that
    invokes other agents rather than implementing the plan-execute-reflect-
    heal loop itself. Keeping it BaseAgent-free avoids the trap of forcing
    9 abstract methods onto what is fundamentally a fan-out/fan-in pattern.
    """

    name = "news_center"

    def __init__(self, sub_agents: Optional[List[str]] = None) -> None:
        self._sub_agents = sub_agents or DEFAULT_SUB_AGENTS

    async def run(self, ctx: AgentContext) -> AgentResult:
        # Lazy import to avoid circular dependency with fzq_ai.registry.agents
        from fzq_ai.registry.agents import get_agent

        trace: list[str] = ["news_center_start"]

        # 1. Pull per-sub-agent results sequentially (deterministic, easy to debug).
        #    Parallelism is left for V25; current sub-agents are LLM-bound and
        #    rate-limited, so sequential keeps things simple and observable.
        merged: Dict[str, Any] = {}
        all_warnings: List[str] = []
        any_failed = False

        for sub_name in self._sub_agents:
            try:
                agent = get_agent(sub_name)
                if agent is None:
                    all_warnings.append(f"{sub_name}: not registered")
                    merged[sub_name] = None
                    any_failed = True
                    trace.append(f"{sub_name}_missing")
                    continue
                result = await agent.run(ctx)
                merged[sub_name] = result.data
                trace.append(f"{sub_name}_done")
                all_warnings.extend(result.warnings)
                if not result.ok:
                    any_failed = True
            except Exception as e:  # noqa: BLE001 — keep all sub-failures isolated
                all_warnings.append(f"{sub_name}: {type(e).__name__}: {e}")
                merged[sub_name] = None
                any_failed = True
                trace.append(f"{sub_name}_error")

        # 2. Civilization: remember and enrich
        civ_trace: list[str] = []
        try:
            civ = ctx.metadata.get("civilization") if hasattr(ctx, "metadata") else None
            if civ and hasattr(civ, "remember"):
                civ.remember("news_query", str(ctx.raw_input))
                civ.remember("news_result_count", str(len(merged)))
                civ_trace.append("civilization.remember")
        except Exception:
            pass

        # 3. Aggregate into a personal-intel view
        return AgentResult(
            ok=not any_failed,
            data={
                "view_type": "personal_intel_center",
                "topic": ctx.raw_input,
                "languages": ctx.languages,
                "focus_regions": ctx.focus_regions,
                "components": merged,
                "civilization_trace": civ_trace,
            },
            warnings=all_warnings,
            trace=trace + civ_trace,
        )
