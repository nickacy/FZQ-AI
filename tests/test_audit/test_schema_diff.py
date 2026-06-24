from pydantic import BaseModel

class MockSchema(BaseModel):
    a: int


from fzq_ai.llm.orchestrator.diff.schema_diff import SchemaDiffEngine

def test_schema_diff_basic():
    engine = SchemaDiffEngine()
    diff = engine.diff({"a": 1}, schema=MockSchema)
    assert "issues" in diff
