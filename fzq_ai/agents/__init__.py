# fzq_ai/agents/__init__.py

from __future__ import annotations

from typing import Dict, Type

from fzq_ai.agents.base_agent import BaseAgent
from fzq_ai.agents.news_intel_agent import NewsIntelAgent

# 如有其他 Agent（code_agent、life_assistant_agent 等），可在此逐步接入
# from fzq_ai.agents.code_agent import CodeAgent
# from fzq_ai.agents.life_assistant_agent import LifeAssistantAgent
# ...


AGENT_REGISTRY: Dict[str, Type[BaseAgent]] = {
    NewsIntelAgent.name: NewsIntelAgent,
    # "code": CodeAgent,
    # "life": LifeAssistantAgent,
}
