# tests/test_self_healing/test_json_repairer.py

from fzq_ai.llm.orchestrator.repair.json_repairer import JsonRepairer
from tests.utils.mock_schema import MockSchema

def test_json_repairer_fixes_broken_json():
    repairer = JsonRepairer()
    broken = '{"a": 1,}'
    result = repairer.repair(broken, MockSchema)

    assert "fixed" in result
    assert isinstance(result["fixed"], dict)
