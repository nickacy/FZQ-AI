# src/fzq_ai/llm/orchestrator/repair/report.py

class RepairReport:
    def __init__(self, raw):
        self.raw = raw
        self.steps = []

    def add_step(self, name, data):
        self.steps.append({"step": name, "data": data})

    def to_dict(self):
        return {
            "raw": self.raw,
            "steps": self.steps,
        }
