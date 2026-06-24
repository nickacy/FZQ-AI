# src/fzq_ai/llm/orchestrator/diff/report.py

class DiffReport:
    def __init__(self, data):
        self.data = data
        self.sections = {}

    def add(self, name, issues):
        self.sections[name] = issues

    def to_dict(self):
        return {
            "data": self.data,
            "issues": self.sections,
        }
