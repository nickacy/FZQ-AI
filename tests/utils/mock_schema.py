# tests/utils/mock_schema.py
from pydantic import BaseModel

class MockSchema(BaseModel):
    a: int = 0
    b: str = ""
    c: list = []
