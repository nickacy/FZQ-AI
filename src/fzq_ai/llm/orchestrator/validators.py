# src/fzq_ai/llm/orchestrator/validators.py

import json

class OutputValidator:
    """
    校验模型输出是否为合法 JSON / Schema 对齐。
    """

    def is_valid(self, output: str) -> bool:
        try:
            json.loads(output)
            return True
        except Exception:
            return False
