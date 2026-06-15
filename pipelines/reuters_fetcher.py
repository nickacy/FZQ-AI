# pipelines/reuters_fetcher.py

import requests
from bs4 import BeautifulSoup
import feedparser

class ReutersFetcher:
    """
    """

    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            "Accept-Language": "en-US,en;q=0.9",

    # ------------------------------------------------------------
    # 1) HTML 抓取
    # ------------------------------------------------------------
    def fetch_html(self, url):
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                return resp.text
            return None
        except:
            return None

    # ------------------------------------------------------------
    # 2) Textise（官方纯文本镜像）
    # ------------------------------------------------------------
    def fetch_textise(self, url):
        try:
            resp = requests.get(textise_url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                return resp.text
            return None
        except:
            return None

    # ------------------------------------------------------------
    # 3) RSS（永不封锁）
    # ------------------------------------------------------------
    def fetch_rss(self):
        rss_url = "https://www.reuters.com/rssFeed/worldNews"
        try:
            for entry in feed.entries:
                        "title": entry.title,
                        "url": entry.link,
                        "summary": entry.summary if hasattr(entry, "summary") else "",
                        "source": "Reuters RSS",
            return items
        except:
            return []

    # ------------------------------------------------------------
    # 4) LLM 自动补全文本（兜底）
    # ------------------------------------------------------------
    def fallback_generate(self, url, llm):
        if llm is None:
            return []

        try:
            return [
                    "title": "Reuters Summary (LLM Fallback)",
                    "url": url,
                    "summary": summary,
                    "source": "DeepSeek Fallback",
        except:
            return []

    # ------------------------------------------------------------
    # 主入口：自动四层 fallback
    # ------------------------------------------------------------
    def fetch(self, url, llm=None):
        # 1) HTML
        html = self.fetch_html(url)
        if html:
            for a in soup.select("a"):
                title = a.get_text(strip=True)
                href = a.get("href", "")
                if title and "/world" in href:
                            "title": title,
                            "url": "https://www.reuters.com" + href,
                            "summary": "",
                            "source": "Reuters HTML",
            if articles:
                return articles

        # 2) Textise
        textise = self.fetch_textise(url)
        if textise:
            for line in lines:
                if "http" in line and len(line) < 200:
                    articles.append(
                        {
                            "title": line.strip()[:120],
                            "url": url,
                            "summary": "",
                            "source": "Reuters Textise",
            if articles:
                return articles

        # 3) RSS
        rss_items = self.fetch_rss()
        if rss_items:
            return rss_items

        # 4) LLM fallback
        return self.fallback_generate(url, llm)
