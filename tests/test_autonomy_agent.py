import pytest
from unittest.mock import MagicMock

from fzq_ai.agent.autonomy_agent import AutonomyAgent


def test_autonomy_agent_basic_flow():
    store = MagicMock()
    orchestrator = MagicMock()

    agent = AutonomyAgent(store, orchestrator)

    # mock think()
    agent.think = MagicMock(return_value={"tasks": ["daily_global_risk"]})

    # mock plan()
    agent.plan = MagicMock(return_value=[{"type": "scenario", "name": "daily_global_risk"}])

    # mock act()
    agent.act = MagicMock(return_value={"daily_global_risk": "ok"})

    think_output = agent.think()
    plan = agent.plan(think_output)
    results = agent.act(plan)

    assert think_output == {"tasks": ["daily_global_risk"]}
    assert isinstance(plan, list)
    assert results == {"daily_global_risk": "ok"}
