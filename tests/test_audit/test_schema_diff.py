# tests/test_audit/test_schema_diff.py

from fzq_ai.llm.orchestrator.diff.schema_diff import SchemaDiffEngine
from tests.utils.mock_schema import MockSchema

def test_schema_diff_basic():
    engine = SchemaDiffEngine()
    diff = engine.diff({"a": 1}, schema=MockSchema)

    assert "issues" in diff
