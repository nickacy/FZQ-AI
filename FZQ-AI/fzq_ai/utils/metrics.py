import time
from typing import Dict, Any


class Metrics:
    def __init__(self):
        # 每次调用记录
        self.records = []

    def start(self, model: str, task: str) -> Dict[str, Any]:
        record = {
            "model": model,
            "task": task,
            "start_time": time.time(),
            "end_time": None,
            "latency": None,
            "input_tokens": 0,
            "output_tokens": 0,
        }
        self.records.append(record)
        return record

    def end(self, record: Dict[str, Any], input_tokens: int, output_tokens: int):
        record["end_time"] = time.time()
        record["latency"] = record["end_time"] - record["start_time"]
        record["input_tokens"] = input_tokens
        record["output_tokens"] = output_tokens

    def dump(self):
        """返回所有调用的统计信息"""
        return self.records
