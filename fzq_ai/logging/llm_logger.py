# fzq_ai/logging/llm_logger.py

import time
import json
import os


class LLMLogger:
    """
    统一 LLM 调用日志
    - 记录 provider / fallback / latency / errors
    - prompt 可选（避免泄露敏感信息）
    """

    def __init__(self, base_dir=None, log_prompt=False):
        self.base_dir = base_dir or os.path.join(os.getcwd(), "logs")
        os.makedirs(self.base_dir, exist_ok=True)

        self.log_prompt = log_prompt

    def log(self, task, provider, prompt, response, latency, error=None, fallback=False):
        record = {
            "task": task,
            "provider": provider,
            "fallback": fallback,
            "latency_ms": int(latency * 1000),
            "error": str(error) if error else None,
        }

        if self.log_prompt:
            record["prompt"] = prompt

        path = os.path.join(self.base_dir, "llm_calls.log")

        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
