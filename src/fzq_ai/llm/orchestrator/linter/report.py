# src/fzq_ai/llm/orchestrator/linter/report.py

class LintReport:
    def __init__(self, prompt):
        self.prompt = prompt
        self.sections = {}

    def add(self, name, issues):
        self.sections[name] = issues

    def to_dict(self):
        return {
            "prompt": self.prompt,
            "issues": self.sections,
        }
