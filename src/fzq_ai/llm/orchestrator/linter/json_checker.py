# src/fzq_ai/llm/orchestrator/linter/json_checker.py

import json
import re

class JsonChecker:
    """
    检查 Prompt 中的 JSON 示例是否合法。
    """

    def check(self, prompt: str):
        issues = []

        # 提取 JSON 示例
        match = re.search(r"\{[\s\S]*\}", prompt)
        if not match:
            issues.append("未找到 JSON 示例")
            return issues

        json_text = match.group(0)

        try:
            json.loads(json_text)
        except Exception:
            issues.append("JSON 示例不可解析")

        return issues
