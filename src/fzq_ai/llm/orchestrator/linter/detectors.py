# src/fzq_ai/llm/orchestrator/linter/detectors.py

class RiskDetector:
    """
    检测 Prompt 中的风险点：
    - 模糊指令
    - 多义指令
    - 容易导致结构化失败的描述
    """

    RISK_PATTERNS = [
        "尽量",
        "大概",
        "可能",
        "随意",
        "自由发挥",
        "尽可能详细",
        "请你判断",
    ]

    def detect(self, prompt: str):
        issues = []
        for pattern in self.RISK_PATTERNS:
            if pattern in prompt:
                issues.append(f"存在模糊指令: {pattern}")
        return issues
