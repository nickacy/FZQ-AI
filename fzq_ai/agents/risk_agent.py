from typing import List


class RiskAgent:
    def __init__(self, llm_router):
        self.llm_router = llm_router

    def _build_prompt(self, items: List[str]) -> str:
        lines = "\n".join(f"- {x}" for x in items)
        return (
            "你是一名风险分析师，请从以下新闻中识别：\n"
            "1）主要风险点（按严重程度排序）\n"
            "2）每个风险的触发条件\n"
            "3）可能影响的领域（经济 / 政策 / 市场 / 社会等）\n"
            "4）风险缓释建议\n\n"
            "【新闻列表】\n"
            f"{lines}\n\n"
            "请用结构化 JSON 风格文本输出，包含字段：\n"
            "risks: [ {name, severity, triggers, impact, suggestions} ]"
        )

    def scan(self, items: List[str]) -> str:
        prompt = self._build_prompt(items)
        return self.llm_router.ask(prompt, task="risk_scan")
