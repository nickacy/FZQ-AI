# src/fzq_ai/agents/orchestrator.py
class AgentOrchestrator:
    """
    Legacy placeholder orchestrator for backward compatibility.
    Old agents import this file. It prevents ModuleNotFoundError.
    """

    def __init__(self):
        pass

    def run(self, *args, **kwargs):
        return {
            "status": "ok",
            "message": "legacy orchestrator placeholder"
        }
