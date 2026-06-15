from typing import List

class NarrativeAgent:
    def __init__(self, llm_router):
        self.llm_router = llm_router

    def _build_prompt(self, merged_news: str, items: List[str]) -> str:
        lines = "\n".join(f"- {x}" for x in items)
        return (
            "你是一名宏观叙事分析师，请从下列新闻中提炼出：\n"
            "1）核心叙事（Narrative）\n"
            "2）驱动因素（Drivers）\n"
            "3）潜在影响（Implications）\n"
            "4）未来可能演化方向（Scenarios）\n\n"
            "【新闻原文汇总】\n"
            "【新闻列表】\n"
            "请用结构化方式输出分析结果。"

    def analyze(self, merged_news: str, items: List[str]) -> str:
        prompt = self._build_prompt(merged_news, items)
        return self.llm_router.ask(prompt, task="narrative")
