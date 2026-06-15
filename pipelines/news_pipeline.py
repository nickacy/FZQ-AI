import feedparser
from fzq_ai.domain.models import Article, IntelBundle, IntelMeta
from fzq_ai.tools.service_result import ServiceResult
from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.utils.logger import get_logger
from fzq_ai.config import get_config
from datetime import datetime

logger = get_logger(__name__)


class NewsPipeline:
    """
    FZQ‑AI v2.5 — News Intelligence Pipeline
    RSS 多源新闻抓取 + 自动摘要 + 风险评分
    """

    def __init__(self, llm: LLMRouter = None):
        self.config = get_config()
        self.sources = self.config.get("rss_sources", [])
        self.llm = llm or LLMRouter()

    def _fetch_rss(self, url: str):
        try:
            feed = feedparser.parse(url)
            return feed.entries
        except Exception as e:
            logger.error(f"[RSS] 抓取失败: {url} — {e}")
            return []

    def _summarize(self, title: str, content: str):
        prompt = f"""
你是一名新闻分析助手，请总结以下新闻内容：

标题：{title}
内容：{content}

请输出简短摘要。
"""
        return self.llm.run(prompt)

    def _risk_score(self, title: str, summary: str):
        prompt = f"""
请对以下新闻进行风险评分（1-5），并给出风险类型：

标题：{title}
摘要：{summary}

输出 JSON：
{{
  "risk_level": 1-5,
  "risk_type": "政治/经济/社会/科技/其他"
}}
"""
        return self.llm.run_json(prompt)

    def run(self, topic: str):
        logger.info(f"[NewsPipeline] 开始分析主题: {topic}")

        articles = []

        # --------------------------------------------------------
        # 1. 遍历所有 RSS 源
        # --------------------------------------------------------
        for src in self.sources:
            url = src.get("url")
            name = src.get("name")

            entries = self._fetch_rss(url)
            for e in entries:
                title = e.get("title", "")
                summary = e.get("summary", "")
                link = e.get("link", "")

                if topic not in title and topic not in summary:
                    continue

                # LLM 摘要
                llm_summary = self._summarize(title, summary)

                # 风险评分
                risk = self._risk_score(title, llm_summary)

                articles.append(
                    Article(
                        title=title,
                        url=link,
                        summary=llm_summary,
                        source=name,
                        published_at=e.get("published", ""),
                        risk_level=risk.get("risk_level", 1),
                        risk_type=risk.get("risk_type", "其他"),
                    )
                )

        # --------------------------------------------------------
        # 2. 构建 intel_bundle
        # --------------------------------------------------------
        bundle = IntelBundle(
            meta=IntelMeta(
                topics=[topic],
                regions=[],
                depth="normal",
                timestamp=datetime.utcnow().isoformat(),
            ),
            articles=articles,
            events=[],
        )

        return ServiceResult.success(bundle)
