# src/fzq_ai/agents/autonomy_agent.py
# V21 — Autonomous Intelligence Agent（完全适配版）
# Author: Nick
# Version: V21.1.0

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List
import asyncio
import json
import logging
import time

from fzq_ai.store.intel_store import IntelStore
from fzq_ai.agents.base import AgentContext
from fzq_ai.agents.registry import get_agent

logger = logging.getLogger(__name__)


@dataclass
class TaskPlan:
    tasks: List[Dict[str, str]] = field(default_factory=list)
    reasoning: str = ""


class AutonomyAgent:
    """
    V21 Autonomous Intelligence Agent.
    """

    def __init__(self, store: IntelStore, orchestrator: Any = None):
        self._store = store
        self._orchestrator = orchestrator
        self._state: Dict[str, Any] = {
            "last_run": 0.0,
            "cycle_count": 0,
            "alerts_triggered": 0,
        }

    # ------------------------------------------------------------
    # think()
    # ------------------------------------------------------------
    def think(self) -> str:
        trends_summary = self._gather_trends()

        prompt = (
            "You are an autonomous intelligence analyst for FZQ-AI.\n\n"
            f"Current trends and data:\n{trends_summary}\n\n"
            "Based on the above, what tasks should be executed next?\n"
            "Respond in JSON format:\n"
            '{"tasks":[{"type":"scenario|report|watchlist","name":"..."}],'
            '"reasoning":"..."}'
        )

        try:
            from fzq_ai.llm.llm_router import LLMRouter
            router = LLMRouter()
            raw = asyncio.run(router.run(prompt))  # V21 统一接口
            return raw
        except Exception:
            return self._rule_based_think(trends_summary)

    def _rule_based_think(self, summary: str) -> str:
        tasks = [
            {"type": "scenario", "name": "daily_global_risk"},
            {"type": "report", "name": "global_risk"},
        ]
        return json.dumps({"tasks": tasks, "reasoning": "Rule-based"}, ensure_ascii=False)

    # ------------------------------------------------------------
    # plan()
    # ------------------------------------------------------------
    def plan(self, think_output: str) -> TaskPlan:
        plan = TaskPlan()
        try:
            text = think_output.strip()
            if "```" in text:
                start = text.find("{")
                end = text.rfind("}") + 1
                text = text[start:end]
            data = json.loads(text)
            plan.tasks = data.get("tasks", [])
            plan.reasoning = data.get("reasoning", "")
        except Exception:
            plan.tasks = [{"type": "scenario", "name": "daily_global_risk"}]
            plan.reasoning = "Default (JSON parse failed)"
        return plan

    # ------------------------------------------------------------
    # act()
    # ------------------------------------------------------------
    def act(self, plan: TaskPlan) -> Dict[str, Any]:
        results: Dict[str, Any] = {}

        if not self._orchestrator:
            logger.warning("No orchestrator set — act() is no-op")
            return results

        for task in plan.tasks:
            task_type = task.get("type", "")
            task_name = task.get("name", "")

            try:
                ctx = AgentContext(
                    user_id="autonomy",
                    locale="en-US",
                    focus_regions=["Global"],
                    languages=["en"],
                    raw_input=task_name,
                    metadata={"source": "autonomy_agent"}
                )

                # Scenario → orchestrator.run_task()
                if task_type == "scenario":
                    results[task_name] = self._orchestrator.run_task(task_name, ctx)

                # Report → ReportAgent.run(ctx)
                elif task_type == "report":
                    from fzq_ai.agents.report_agent import ReportAgent
                    agent = ReportAgent(store=self._store)
                    results[task_name] = agent.run(ctx)

                # Watchlist → WatchlistAgent.run(ctx)
                elif task_type == "watchlist":
                    from fzq_ai.agents.watchlist_agent import WatchlistAgent
                    agent = WatchlistAgent(orchestrator=self._orchestrator)
                    results["watchlist"] = agent.run(ctx)

            except Exception as e:
                logger.warning(f"Task {task_name} failed: {e}")
                results[task_name] = {"error": str(e)}

        return results

    # ------------------------------------------------------------
    # loop()
    # ------------------------------------------------------------
    def loop(self, interval_seconds: int = 1800, max_cycles: int = 0) -> None:
        cycle = 0
        while max_cycles == 0 or cycle < max_cycles:
            cycle += 1
            self._state["cycle_count"] = cycle
            self._state["last_run"] = time.time()

            think_output = self.think()
            plan = self.plan(think_output)
            results = self.act(plan)

            logger.info(f"Cycle {cycle} results: {list(results.keys())}")

            if max_cycles != 1:
                time.sleep(interval_seconds)

    def start(self) -> None:
        self._state["started"] = time.time()

    def stop(self) -> None:
        self._state["stopped"] = time.time()

    @property
    def status(self) -> Dict[str, Any]:
        return dict(self._state)
