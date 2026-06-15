import pytest
from unittest.mock import MagicMock

from fzq_ai.agent.watchlist_agent import WatchlistAgent


def test_narrative_shift_detection():
    store = MagicMock()
    agent = WatchlistAgent(store)

    # mock embedding 对比
    agent._get_last_two_runs = MagicMock(
        return_value=[
            {"embedding": [0.1, 0.2, 0.3]},
            {"embedding": [0.9, 0.8, 0.7]},
        ]
    )

    shift = agent.detect_narrative_shift("gaza_narrative")

    assert isinstance(shift, dict)
    assert "shift_score" in shift
    assert shift["shift_score"] > 0
