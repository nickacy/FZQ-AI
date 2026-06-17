# fzq_ai/llm/task_registry.py
# v6.0 鈥?Unified task registry (all pipeline task types registered)

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TaskConfig:
    name: str
    default_provider: str
    fallback_chain: List[str]
    json_mode: bool = False
    require_reasoning: bool = False
    require_long_context: bool = False


class TaskRegistry:
    \"\"\"Unified task registration 鈥?drives LLMRouter provider selection.\"\"\"

    def __init__(self):
        self.tasks = {}
        self._register_all()

    def _register_all(self):
        # === Intelligence (JSON structured output) ===
        _intel = lambda n: TaskConfig(
            name=n, default_provider=\"openai\",
            fallback_chain=[\"openai\", \"deepseek\", \"minimax\"], json_mode=True)
        self.register(_intel(\"news_intel\"))
        self.register(_intel(\"event_extraction\"))
        self.register(_intel(\"structured_extraction\"))

        # === Risk (reasoning-heavy) ===
        _risk = lambda n: TaskConfig(
            name=n, default_provider=\"deepseek\",
            fallback_chain=[\"deepseek\", \"openai\", \"minimax\"],
            json_mode=False, require_reasoning=True)
        self.register(_risk(\"risk_intel\"))
        self.register(_risk(\"risk_summary\"))
        self.register(_risk(\"risk_factors\"))
        self.register(_risk(\"risk_forecast\"))

        # === Sentiment ===
        _sent = lambda n: TaskConfig(
            name=n, default_provider=\"openai\",
            fallback_chain=[\"openai\", \"deepseek\", \"minimax\"], json_mode=False)
        self.register(_sent(\"sentiment\"))
        self.register(_sent(\"sentiment_score\"))
        self.register(_sent(\"sentiment_summary\"))

        # === Narrative (deep reasoning) ===
        _narr = lambda n: TaskConfig(
            name=n, default_provider=\"deepseek\",
            fallback_chain=[\"deepseek\", \"openai\", \"minimax\"],
            json_mode=False, require_reasoning=True)
        self.register(_narr(\"narrative_summary\"))
        self.register(_narr(\"narrative_keypoints\"))
        self.register(_narr(\"narrative_storyline\"))
        self.register(_narr(\"narrative_implications\"))

        # === Scenario (long context + deep reasoning) ===
        self.register(TaskConfig(
            name=\"scenario\", default_provider=\"deepseek\",
            fallback_chain=[\"deepseek\", \"openai\", \"minimax\"],
            json_mode=False, require_reasoning=True, require_long_context=True))

        # === Multilingual ===
        self.register(TaskConfig(
            name=\"multilingual_summary\", default_provider=\"gemini\",
            fallback_chain=[\"gemini\", \"openai\", \"deepseek\"], json_mode=False))

        # === Deep reasoning ===
        self.register(TaskConfig(
            name=\"deep_reasoning\", default_provider=\"deepseek\",
            fallback_chain=[\"deepseek\", \"openai\", \"minimax\"],
            json_mode=False, require_reasoning=True, require_long_context=True))

    def register(self, config: TaskConfig) -> None:
        self.tasks[config.name] = config

    def get(self, task: str) -> TaskConfig:
        return self.tasks.get(task, self.tasks[\"sentiment\"])

    def list_tasks(self) -> list:
        return sorted(self.tasks.keys())
