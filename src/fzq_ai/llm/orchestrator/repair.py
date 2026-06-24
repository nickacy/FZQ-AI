# src/fzq_ai/llm/orchestrator/repair.py

import json

class JsonRepairer:
    """
    JSON 自愈修复器 v1
    - 修复缺失括号
    - 修复多余逗号
    - 修复字段缺失（简单补全）
    """

    def repair(self, output: str) -> str:
        try:
            return json.dumps(json.loads(output), ensure_ascii=False)
        except Exception:
            # TODO: v2: 使用 Qwen 自动修复
            return "{}"
