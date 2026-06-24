# src/fzq_ai/llm/orchestrator/recovery/error_classifier.py

import json

class ErrorClassifier:
    """
    分类错误类型。
    """

    def classify(self, output, error):
        if error:
            if "timeout" in str(error).lower():
                return "TimeoutError"
            if "api" in str(error).lower():
                return "APIError"

        try:
            json.loads(output)
        except Exception:
            return "JSONDecodeError"

        return "UnknownError"
