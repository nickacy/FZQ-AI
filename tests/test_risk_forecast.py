import pytest
from unittest.mock import MagicMock

from fzq_ai.store.trend_engine import TrendEngine


def test_risk_forecast():
    store = MagicMock()
    engine = TrendEngine(store)

    # mock 历史风险数据
    engine._load_risk_series = MagicMock(
        return_value=[1, 2, 3, 4, 5]
    )

    forecast = engine.forecast_risk("global_macro")

    assert isinstance(forecast, dict)
    assert "prediction" in forecast
    assert forecast["prediction"] >= 5
