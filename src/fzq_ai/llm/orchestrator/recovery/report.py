# src/fzq_ai/llm/orchestrator/recovery/report.py

class RecoveryReport:
    def __init__(self, provider, raw_output, error):
        self.provider = provider
        self.raw_output = raw_output
        self.error = error
        self.steps = []

    def add_step(self, name, data):
        self.steps.append({"step": name, "data": data})

    def to_dict(self):
        return {
            "provider": self.provider,
            "raw_output": self.raw_output,
            "error": self.error,
            "steps": self.steps,
        }
