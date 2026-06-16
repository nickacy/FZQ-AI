"""v6.0 Scenario tests."""
from fzq_ai.scenarios.political_intel import PoliticalIntelScenario


class TestScenarios:
    def test_political_intel_interface(self):
        """Scenario exposes name, description, and execute()."""
        s = PoliticalIntelScenario()
        assert s.name == "Political Intelligence"
        assert len(s.description) > 10
        assert callable(s.execute)

    def test_political_intel_execute(self):
        """execute() returns ServiceResult for a valid topic."""
        s = PoliticalIntelScenario()
        result = s.execute(topic="US politics")
        assert hasattr(result, "success")
        assert hasattr(result, "data")
        assert hasattr(result, "error")
