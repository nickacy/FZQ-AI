from typing import List
from fzq_ai.llm.llm_router import LLMRouter


class NewsAgent:
    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router

    def _build_prompt(self, items: List[str]) -> str:
        lines = "\n".join(f"- {x}" for x in items)
        return (
            "你是一名专业的新闻编辑，请对以下多条新闻进行逐条摘要，"
            "并给出一个整体的简要综述。\n\n"
            "【新闻列表】\n"
            f"{lines}\n\n"
            "请输出结构化结果：\n"
            "1）每条新闻的简要摘要\n"
            "2）整体趋势与关键信息\n"
        )

    def summarize_multi(self, items: List[str]) -> str:
        prompt = self._build_prompt(items)
        return self.llm_router.ask(prompt, task="news_summary")
