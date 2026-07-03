# src/fzq_ai/orchestrator/execution_builder.py
# V24-Final — Execution Builder
"""Build unified execution objects for frontend rendering."""
from __future__ import annotations
import uuid
import time
from typing import Any, Dict, List, Optional


def build_execution(
    *,
    agent_name: str = "unknown",
    task_type: str = "default",
    intent: str = "",
    output: Any = None,
    reflection: Optional[Dict[str, Any]] = None,
    healing: Optional[Dict[str, Any]] = None,
    loop_cycles: Optional[List[Dict[str, Any]]] = None,
    model_used: str = "unknown",
    fallback_used: Optional[str] = None,
    timeline: Optional[List[Dict[str, Any]]] = None,
    trace_id: Optional[str] = None,
    duration_ms: float = 0,
    success: bool = True,
    error: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a complete V24 execution payload for the frontend."""
    from fzq_ai.utils.state_machine import get_state_machine
    from fzq_ai.utils.memory import global_memory
    from fzq_ai.utils.goals import global_goals
    from fzq_ai.utils.personality import global_personality

    sm = get_state_machine(agent_name)

    return {
        # Core
        "agent": agent_name,
        "task_type": task_type,
        "intent": intent,
        "output": output,
        "timestamp": time.time(),
        "trace_id": trace_id or str(uuid.uuid4()),
        "duration_ms": duration_ms,
        "success": success,
        "error": error,

        # Model & failover
        "model_used": model_used,
        "fallback_used": fallback_used,

        # State machine
        "state_machine": sm.snapshot(),

        # Agent subsystems
        "memory": global_memory.snapshot(agent_name),
        "goals": global_goals.snapshot(agent_name),
        "personality": global_personality.get(agent_name),
        "reflection": reflection,
        "healing": healing,

        # Loop
        "loop": {
            "cycles": loop_cycles or [],
            "total_cycles": len(loop_cycles) if loop_cycles else 0,
        },

        # Timeline
        "timeline": timeline or [],
    }
