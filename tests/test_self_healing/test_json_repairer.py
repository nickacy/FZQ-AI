from fzq_ai.llm.orchestrator.repair.json_repairer import JsonRepairer

def test_json_repairer_basic():
    repairer = JsonRepairer()
    broken = '{"a": 1,}'
    fixed = repairer.repair(broken, schema=None)
    assert "fixed" in fixed
