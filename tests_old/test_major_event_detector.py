import pytest
from unittest.mock import MagicMock

from fzq_ai.agent.alert_agent import AlertAgent
from fzq_ai.domain.models import IntelBundle, Article


def test_major_event_detector():
    store = MagicMock()
    agent = AlertAgent(store)

    # 构造一个 bundle，包含一个高风险文章
    article = Article(
        title_original="重大事件：以色列与哈马斯达成停火协议",
        content_original="Ceasefire agreement reached...",
        risk_level=5,
        risk_type="military",
    )

    bundle = IntelBundle(
        articles=[article],
        summary="test",
        risk_summary={"military": 5},
        narrative_summary={},
        sentiment_summary={},
    )

    events = agent.detect_major_events(bundle)

    assert isinstance(events, list)
    assert len(events) >= 1
