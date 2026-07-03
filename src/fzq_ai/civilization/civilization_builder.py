# src/fzq_ai/civilization/civilization_builder.py
# V24-Final — Civilization Builder
"""Pre-built civilization configurations for FZQ-AI."""
from .civilization_engine import CivilizationEngine


def build_default_civilization() -> CivilizationEngine:
    """Build the default FZQ-AI civilization with risk/policy/core agents."""
    civ = CivilizationEngine("fzq-default")

    civ.add_agent("deepseek-risk", role="risk_analyst", priority=3)
    civ.add_agent("deepseek-policy", role="policy_analyst", priority=2)
    civ.add_agent("deepseek-news", role="intelligence_officer", priority=1)

    civ.link("deepseek-risk", "deepseek-policy")
    civ.link("deepseek-policy", "deepseek-news")
    civ.link("deepseek-risk", "deepseek-news")

    civ.remember("mission", "Cross-civilization intelligence analysis")
    civ.remember("version", "v24")

    return civ


def build_parliament() -> CivilizationEngine:
    """Build a parliamentary civilization with voting weights."""
    civ = CivilizationEngine("parliament")

    civ.add_agent("deepseek-risk", role="opposition", priority=1)
    civ.add_agent("deepseek-policy", role="governing_party", priority=2)
    civ.add_agent("glm-opinion", role="public_voice", priority=1)
    civ.add_agent("deepseek-news", role="speaker", priority=3)

    # Full connectivity
    for a in civ.agents:
        for b in civ.agents:
            if a != b:
                civ.link(a, b)

    return civ
