# src/fzq_ai/utils/goals.py
# V24-Final — Agent Goal System
"""
Hierarchical goal system for FZQ-AI agents.

  Short-term goals: per-request (task_type, intent, priority, deadline)
  Long-term goals:  persistent (role, mission, constraints, quality_target)

Integrated with: PromptEngine, Router, MemoryEngine, Orchestrator, Tracing.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

# ── Pre-defined long-term goals per agent role ────────────────

ROLE_GOALS: Dict[str, Dict[str, Any]] = {
    "deepseek-risk": {
        "role": "风险分析专家",
        "mission": "识别并评估金融风险，提供可执行的建议",
        "constraints": ["基于数据", "避免猜测", "标注置信度"],
        "quality_target": {"accuracy": 0.9, "completeness": 0.85},
    },
    "deepseek-policy": {
        "role": "政策分析师",
        "mission": "解读政策影响，提供前瞻性分析",
        "constraints": ["引用原文", "区分事实与观点", "标注时间线"],
        "quality_target": {"accuracy": 0.85, "completeness": 0.9},
    },
    "deepseek-news": {
        "role": "新闻情报官",
        "mission": "快速提炼新闻要点，生成情报摘要",
        "constraints": ["速度优先", "多源验证", "简洁输出"],
        "quality_target": {"speed": "fast", "coverage": 0.8},
    },
    "glm-opinion": {
        "role": "舆情分析师",
        "mission": "分析舆论趋势，识别话题走向",
        "constraints": ["覆盖多方观点", "区分事实与情绪", "标注样本来源"],
        "quality_target": {"diversity": 0.9, "accuracy": 0.75},
    },
    "autonomy-agent": {
        "role": "自治智能体",
        "mission": "自主规划并执行复杂任务链",
        "constraints": ["保持可追溯", "允许失败重试", "记录决策过程"],
        "quality_target": {"autonomy": 0.95, "completion": 0.8},
    },
}


# ── Goal Engine ───────────────────────────────────────────────

class GoalEngine:
    """Central goal store for all agents."""

    def __init__(self):
        self.short_term: Dict[str, Dict[str, Any]] = {}   # agent → {key: val}
        self.long_term: Dict[str, Dict[str, Any]] = {}    # agent → {key: val}
        self._history: List[Dict[str, Any]] = []

        # Pre-load role-based long-term goals
        for agent, data in ROLE_GOALS.items():
            for k, v in data.items():
                self.set_long_term(agent, k, v)

    # ── Short-term ──────────────────────────────────────────

    def set(self, agent: str, key: str, value: Any) -> None:
        self.short_term.setdefault(agent, {})[key] = value
        self._log("set_short", agent, key, value)

    def get(self, agent: str, key: str, default: Any = None) -> Any:
        return self.short_term.get(agent, {}).get(key, default)

    def clear_short(self, agent: Optional[str] = None) -> None:
        if agent:
            self.short_term.pop(agent, None)
        else:
            self.short_term.clear()

    # ── Long-term ────────────────────────────────────────────

    def set_long_term(self, agent: str, key: str, value: Any) -> None:
        self.long_term.setdefault(agent, {})[key] = value

    def get_long_term(self, agent: str, key: str, default: Any = None) -> Any:
        return self.long_term.get(agent, {}).get(key, default)

    # ── Priority helpers ─────────────────────────────────────

    def priority(self, agent: str) -> str:
        """Get agent execution priority."""
        return self.get(agent, "priority", "balanced")

    def goal_intent(self, agent: str) -> str:
        """Build intent string from agent's current goals."""
        task = self.get(agent, "task_type", "")
        intent = self.get(agent, "intent", "")
        mission = self.get_long_term(agent, "mission", "")
        parts = []
        if mission:
            parts.append(f"使命：{mission}")
        if task:
            parts.append(f"当前任务：{task}")
        if intent:
            parts.append(f"意图：{intent}")
        return "\n".join(parts) if parts else ""

    # ── Snapshot ─────────────────────────────────────────────

    def snapshot(self, agent: str) -> Dict[str, Any]:
        return {
            "short_term": dict(self.short_term.get(agent, {})),
            "long_term": dict(self.long_term.get(agent, {})),
            "priority": self.priority(agent),
        }

    # ── Logging ──────────────────────────────────────────────

    def _log(self, action: str, agent: str, key: str, value: Any) -> None:
        import time
        self._history.append({
            "ts": time.time(),
            "action": action,
            "agent": agent,
            "key": key,
            "val": repr(value)[:100],
        })
        if len(self._history) > 500:
            self._history = self._history[-250:]


# ── Global instance ──────────────────────────────────────────

global_goals = GoalEngine()
