# src/fzq_ai/llm/orchestrator/recovery/retry_policy.py

class RetryPolicy:
    """
    根据错误类型决定是否重试。
    """

    RETRYABLE = {"JSONDecodeError", "TimeoutError", "APIError"}

    def should_retry(self, error_type):
        return error_type in self.RETRYABLE
