# src/fzq_ai/llm/orchestrator/recovery/repair_policy.py

from fzq_ai.llm.orchestrator.repair.json_repairer import JsonRepairer

class RepairPolicy:
    """
    使用 JSON 自愈系统修复输出。
    """

    def __init__(self):
        self.repairer = JsonRepairer()

    def repair(self, output, task):
        schema = task.get("schema")
        return self.repairer.repair(output, schema)
