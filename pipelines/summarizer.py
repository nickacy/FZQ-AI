# pipelines/summarizer.py

class NewsSummarizer:
    """
    """

    def __init__(self, llm):
        self.llm = llm

    def summarize(self, title, url, content=""):
        prompt = f"""
你是一名新闻摘要助手。请为以下新闻生成 1–2 句简短摘要。

标题：{title}
URL：{url}

如果没有正文，请根据标题和 URL 推断新闻大意。
摘要必须简短、客观、信息密度高。
"""

        try:
            summary = self.llm.ask(prompt)
            return summary.strip()
        except:
            return ""
