# pipelines/news_pipeline.py

import requests
from bs4 import BeautifulSoup

from pipelines.reuters_fetcher import ReutersFetcher
from pipelines.summarizer import NewsSummarizer
from pipelines.risk_scorer import RiskScorer
from core.cache_manager import CacheManager


class NewsPipeline:
    """
    FZQ‑AI Agent — News Pipeline v1.5
    多源新闻抓取 + Reuters 四层终极抓取器
    + 自动摘要 + 自动风险评分 + 缓存系统
    """

    def __init__(self, config, llm=None):
        self.config = config
        self.sources = config.news_sources
        self.llm = llm

        # 终极抓取器
        self.reuters_fetcher = ReutersFetcher()

        # 摘要生成器
        self.summarizer = NewsSummarizer(llm)

        # 风险评分器
        self.risk_scorer = RiskScorer(llm)

        # 缓存系统
        self.news_cache = CacheManager("data/cache/news_cache.json", expire_hours=6)
        self.summary_cache = CacheManager(
            "data/cache/summary_cache.json", expire_hours=24
        )
        self.risk_cache = CacheManager("data/cache/risk_cache.json", expire_hours=24)

        # 通用浏览器 UA
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }

    # ------------------------------------------------------------
    # 通用 HTML 抓取
    # ------------------------------------------------------------
    def fetch_html(self, url):
        try:
            print(f"[HTML] 抓取: {url}")
            resp = requests.get(url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"[ERROR] 抓取失败: {url} — {e}")
            return ""

    # ------------------------------------------------------------
    # 通用 HTML 解析（简单标题提取）
    # ------------------------------------------------------------
    def parse_news(self, html, source_name):
        soup = BeautifulSoup(html, "html.parser")
        items = []

        for a in soup.find_all("a"):
            title = a.get_text(strip=True)
            href = a.get("href", "")

            if not title or len(title) < 10:
                continue

            if href.startswith("/"):
                href = f"https://{source_name}{href}"

            items.append(
                {"title": title, "url": href, "summary": "", "source": source_name}
            )

        return items

    # ------------------------------------------------------------
    # 主流程（含缓存 + Reuters 终极抓取器）
    # ------------------------------------------------------------
    def run(self):
        print("[NewsPipeline] 开始抓取新闻...")

        all_news = []

        for src in self.sources:
            name = src["name"]
            url = src["url"]

            # ----------------------------------------------------
            # 1) 缓存检查
            # ----------------------------------------------------
            cached = self.news_cache.get(url)
            if cached:
                print(f"[Cache] 命中缓存: {url}")
                all_news.extend(cached)
                continue

            # ----------------------------------------------------
            # 2) Reuters 使用终极抓取器（永不 401）
            # ----------------------------------------------------
            if "reuters.com" in url:
                print(f"[Reuters] 使用终极抓取器: {url}")
                articles = self.reuters_fetcher.fetch(url, self.llm)
                all_news.extend(articles)
                self.news_cache.set(url, articles)
                continue

            # ----------------------------------------------------
            # 3) 其他网站使用普通 HTML 抓取
            # ----------------------------------------------------
            html = self.fetch_html(url)
            if not html:
                continue

            items = self.parse_news(html, name)
            all_news.extend(items)
            self.news_cache.set(url, items)

        print(f"[NewsPipeline] 抓取完成，共 {len(all_news)} 条新闻")
        print("[NewsPipeline] 开始生成摘要与风险评分...")

        # --------------------------------------------------------
        # 4) 为每条新闻生成摘要 + 风险评分（含缓存）
        # --------------------------------------------------------
        for item in all_news:
            title = item["title"]

            # -------------------------
            # 摘要缓存
            # -------------------------
            cached_summary = self.summary_cache.get(title)
            if cached_summary:
                item["summary"] = cached_summary
            else:
                summary = self.summarizer.summarize(
                    title=item["title"], url=item["url"]
                )
                item["summary"] = summary
                self.summary_cache.set(title, summary)

            # -------------------------
            # 风险评分缓存
            # -------------------------
            cached_risk = self.risk_cache.get(title)
            if cached_risk:
                item.update(cached_risk)
            else:
                scores = self.risk_scorer.score(
                    title=item["title"], summary=item["summary"]
                )
                item.update(scores)
                self.risk_cache.set(title, scores)

        print(
            f"[NewsPipeline] 全部处理完成，共 {len(all_news)} 条新闻（含摘要 + 风险评分）"
        )
        return all_news
