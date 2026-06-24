# tests/utils/mock_provider.py

class MockProvider:
    def __init__(self, name="mock"):
        self.name = name

    async def run(self, task):
        return '{"summary": "ok", "clusters": []}'

    def run_sync(self, text):
        return "mock output"
