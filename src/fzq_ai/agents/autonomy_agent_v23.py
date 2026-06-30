# src/fzq_ai/agents/autonomy_agent_v23.py
# V23-Final — Autonomous Agent with Safety Guards
# Author: Nick
# Version: V23.3.0

from __future__ import annotations
import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from fzq_ai.agents.blackboard import Blackboard
from fzq_ai.schemas.route import RouteResult


CHECKPOINT_DIR = Path("agent_checkpoints")
CHECKPOINT_DIR.mkdir(exist_ok=True)


class AutonomyAgentV23:
    """
    V23 Autonomous Agent
    - Plan → Act → Observe → Reflect loop
    - Safety guards: timeout, max cycles, sandbox tools
    - Checkpointing for crash recovery
    - Blackboard integration for multi-agent context sharing
    """

    def __init__(
        self,
        max_cycles: int = 5,
        max_duration_sec: int = 30,
        allowed_tools: Optional[list[str]] = None,
    ) -> None:
        self.max_cycles = max_cycles
        self.max_duration_sec = max_duration_sec
        self.allowed_tools = allowed_tools or ["search", "summarize"]

        self.cycle = 0
        self.trace_id = str(uuid.uuid4())
        self.status: Dict[str, Any] = {
            "trace_id": self.trace_id,
            "cycles_completed": 0,
            "last_action": None,
            "last_observation": None,
            "last_reflection": None,
            "blackboard": {},
        }

    # ------------------------------------------------------------
    # Checkpointing
    # ------------------------------------------------------------
    def save_checkpoint(self) -> None:
        ck = CHECKPOINT_DIR / f"{self.trace_id}_cycle_{self.cycle}.json"
        with ck.open("w", encoding="utf-8") as f:
            json.dump(self.status, f, ensure_ascii=False, indent=2)

    def load_latest_checkpoint(self) -> None:
        files = sorted(CHECKPOINT_DIR.glob(f"{self.trace_id}_cycle_*.json"))
        if not files:
            return
        with files[-1].open("r", encoding="utf-8") as f:
            self.status = json.load(f)
            self.cycle = self.status.get("cycles_completed", 0)

    # ------------------------------------------------------------
    # Sandbox tool check
    # ------------------------------------------------------------
    def check_tool_permission(self, tool_name: str) -> bool:
        return tool_name in self.allowed_tools

    # ------------------------------------------------------------
    # Autonomous loop
    # ------------------------------------------------------------
    def loop(self) -> RouteResult:
        start_time = time.time()

        # Load checkpoint if exists
        self.load_latest_checkpoint()

        while self.cycle < self.max_cycles:
            # Timeout guard
            if time.time() - start_time > self.max_duration_sec:
                return RouteResult.error(
                    code="AUTONOMY_TIMEOUT",
                    message="AutonomyAgent exceeded max_duration_sec",
                    debug_info={"trace_id": self.trace_id},
                )

            # ------------------------------
            # 1. PLAN
            # ------------------------------
            plan = f"Cycle {self.cycle}: plan next action"
            self.status["last_action"] = plan

            # ------------------------------
            # 2. ACT (sandbox)
            # ------------------------------
            tool = "search"
            if not self.check_tool_permission(tool):
                return RouteResult.error(
                    code="SANDBOX_VIOLATION",
                    message=f"Tool '{tool}' not allowed",
                    debug_info={"allowed_tools": self.allowed_tools},
                )

            action_result = f"Executed tool: {tool}"
            self.status["last_observation"] = action_result

            # ------------------------------
            # 3. OBSERVE
            # ------------------------------
            Blackboard.write(f"cycle_{self.cycle}_observation", action_result)

            # ------------------------------
            # 4. REFLECT
            # ------------------------------
            reflection = f"Reflection on cycle {self.cycle}"
            self.status["last_reflection"] = reflection

            # Update blackboard snapshot
            self.status["blackboard"] = Blackboard.read_all()

            # Save checkpoint
            self.save_checkpoint()

            # Increment cycle
            self.cycle += 1
            self.status["cycles_completed"] = self.cycle

        return RouteResult.ok(data=self.status)
