# src/fzq_ai/agents/autonomy_agent.py
# v4.6 — Autonomous Intelligence Agent（兼容现有接口修正版）
# Author: Nick

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import asyncio
import json
import logging
import time

from fzq_ai.store.intel_store import IntelStore

logger = logging.getLogger(__name__)


@dataclass
class TaskPlan:
    tasks: List[Dict[str, str]] = field(default_factory=list)
    reasoning: str = ""


class AutonomyAgent:
    """
    Autonomous Intelligence Agent (v4.6)
    Compatible with your current project interfaces.
    """

    def __init__(self, store: IntelStore, orchestrator: Any = None):  # type: ignore[no-any-explicit]
        self._store = store
        self._orchestrator = orchestrator
        self._state: Dict[str, Any] = {
            "last_run": 0.0,
            "cycle_count": 0,
            "alerts_triggered": 0,
        }

    # ── think() ──

    def think(self) -> str:
        trends_summary = self._gather_trends()

        prompt = (
            "You are an autonomous intelligence analyst for FZQ-AI.\n\n"
            f"Current trends and data:\n{trends_summary}\n\n"
            "Based on the above, what tasks should be executed next?\n"
            "Respond in JSON format:\n"
            '{"tasks": [{"type": "scenario|report|watchlist", "name": "..."}], '
            '"reasoning": "..."}'
        )

        try:
            from fzq_ai.llm.llm_router import LLMRouter
            router = LLMRouter()

            # LLMRouter.call(provider, prompt, model, api_key)
            import os
            raw = asyncio.run(
                router.call(
                    provider="deepseek",
                    prompt=prompt,
                    model="default",
                    api_key=os.getenv("DEEPSEEK_API_KEY", ""),
                )
            )
            return raw

        except RuntimeError as e:
            if "cannot be called from a running event loop" in str(e):
                logger.warning("asyncio.run() failed, falling back to rule-based")
            return self._rule_based_think(trends_summary)

        except Exception:
            return self._rule_based_think(trends_summary)

    def _rule_based_think(self, summary: str) -> str:
        tasks = [
            {"type": "scenario", "name": "daily_global_risk"},
            {"type": "report", "name": "global risk"},
        ]
        return json.dumps({"tasks": tasks, "reasoning": "Rule-based"}, ensure_ascii=False)

    def _gather_trends(self) -> str:
        lines = ["- Cycle: " + str(self._state["cycle_count"])]
        try:
            topics = ["global conflict", "US election", "energy market"]
            for t in topics:
                records = self._store.load_latest(t, limit=1)
                count = len(records[0].bundle.articles) if records else 0
                lines.append(f"- {t}: {count} articles (latest)")
        except Exception:
            pass
        return "\n".join(lines)

    # ── plan() ──

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

    # ── act() ──

    def act(self, plan: TaskPlan) -> Dict[str, Any]:
        results: Dict[str, Any] = {}

        if not self._orchestrator:
            logger.warning("No orchestrator set — act() is no-op")
            return results

        for task in plan.tasks:
            task_type = task.get("type", "")
            task_name = task.get("name", "")

            try:
                # Scenario → use your existing run_scenario / run_nl
                if task_type == "scenario":
                    if hasattr(self._orchestrator, "run_scenario"):
                        results[task_name] = self._orchestrator.run_scenario(task_name)
                    else:
                        results[task_name] = self._orchestrator.run_nl(
                            task_name.replace("_", " ")
                        )

                # Report → use your existing generate_markdown_report
                elif task_type == "report":
                    from fzq_ai.agents.report_agent import ReportAgent
                    agent = ReportAgent(store=self._store)
                    results[task_name] = agent.generate_markdown_report(task_name)

                # Watchlist → use your existing run_once
                elif task_type == "watchlist":
                    from fzq_ai.agents.watchlist_agent import WatchlistAgent
                    agent = WatchlistAgent(orchestrator=self._orchestrator)
                    results["watchlist"] = agent.detect_narrative_shift(topic=task_name)

            except Exception as e:
                logger.warning(f"Task {task_name} failed: {e}")
                results[task_name] = {"error": str(e)}

        return results

    # ── loop() ──

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
