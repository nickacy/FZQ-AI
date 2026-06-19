
"""
FZQ-AI Tools — 全球情报级多源新闻抓取器 v8
支持 RSS、NewsAPI、GDELT、Google News RSS、Bing News RSS 等多源
支持多语言、多区域、议题自动扩展、相关性过滤
"""
import hashlib
import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, AsyncIterator
from urllib.parse import quote

import aiohttp
import xml.etree.ElementTree as ET

from fzq_ai.schemas.real import (
    LanguageCode, NewsSource, RawNewsItem, RegionCode,
    ModelProvider, LLMRequest, LLMResponse,
)
from fzq_ai.utils.helpers import generate_id
from fzq_ai.core.prompts import PromptTemplates


# ===========================================================================
# 内置多源 RSS 配置（按区域 + 语言）
# ===========================================================================

RSS_SOURCES_BY_REGION: Dict[RegionCode, List[Dict[str, Any]]] = {
    RegionCode.GLOBAL: [
        {"name": "Reuters", "url": "https://www.reutersagency.com/feed/?taxonomy=markets&post_type=reuters-best", "language": LanguageCode.EN, "reliability_score": 0.9},
        {"name": "BBC World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml", "language": LanguageCode.EN, "reliability_score": 0.9},
        {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml", "language": LanguageCode.EN, "reliability_score": 0.85},
    ],
    RegionCode.US: [
        {"name": "CNN", "url": "http://rss.cnn.com/rss/edition.rss", "language": LanguageCode.EN, "reliability_score": 0.8},
        {"name": "Washington Post", "url": "https://feeds.washingtonpost.com/rss/world", "language": LanguageCode.EN, "reliability_score": 0.85},
        {"name": "NYT", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "language": LanguageCode.EN, "reliability_score": 0.9},
    ],
    RegionCode.CN: [
        {"name": "财联社", "url": "https://www.cls.cn/telegraph", "language": LanguageCode.ZH, "reliability_score": 0.85},
        {"name": "澎湃新闻", "url": "https://www.thepaper.cn/rss", "language": LanguageCode.ZH, "reliability_score": 0.8},
    ],
    RegionCode.EU: [
        {"name": "Politico EU", "url": "https://www.politico.eu/rss", "language": LanguageCode.EN, "reliability_score": 0.85},
        {"name": "Le Monde", "url": "https://www.lemonde.fr/rss/une.xml", "language": LanguageCode.FR, "reliability_score": 0.85},
    ],
    RegionCode.AE: [
        {"name": "Gulf News", "url": "https://gulfnews.com/rss", "language": LanguageCode.EN, "reliability_score": 0.8},
    ],
    RegionCode.SA: [
        {"name": "Arab News", "url": "https://www.arabnews.com/rss", "language": LanguageCode.EN, "reliability_score": 0.8},
    ],
    RegionCode.JP: [
        {"name": "Japan Times", "url": "https://www.japantimes.co.jp/feed/", "language": LanguageCode.EN, "reliability_score": 0.85},
    ],
    RegionCode.BR: [
        {"name": "Globo", "url": "https://oglobo.globo.com/rss.xml", "language": LanguageCode.PT, "reliability_score": 0.8},
    ],
    RegionCode.IN: [
        {"name": "The Hindu", "url": "https://www.thehindu.com/news/?service=rss", "language": LanguageCode.EN, "reliability_score": 0.85},
    ],
    RegionCode.RU: [
        {"name": "TASS", "url": "https://tass.com/rss/v2.xml", "language": LanguageCode.EN, "reliability_score": 0.75},
    ],
}

# Google News RSS 搜索模板（按语言）
GOOGLE_NEWS_RSS_TEMPLATES: Dict[LanguageCode, str] = {
    LanguageCode.EN: "https://news.google.com/rss/search?q={}&hl=en-US&gl=US&ceid=US:en",
    LanguageCode.ZH: "https://news.google.com/rss/search?q={}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
    LanguageCode.ES: "https://news.google.com/rss/search?q={}&hl=es&gl=ES&ceid=ES:es",
    LanguageCode.FR: "https://news.google.com/rss/search?q={}&hl=fr&gl=FR&ceid=FR:fr",
    LanguageCode.DE: "https://news.google.com/rss/search?q={}&hl=de&gl=DE&ceid=DE:de",
    LanguageCode.AR: "https://news.google.com/rss/search?q={}&hl=ar&gl=AE&ceid=AE:ar",
}

# Bing News RSS 搜索模板
BING_NEWS_RSS_TEMPLATES: Dict[LanguageCode, str] = {
    LanguageCode.EN: "https://www.bing.com/news/search?q={}&format=rss",
    LanguageCode.ZH: "https://www.bing.com/news/search?q={}&setmkt=zh-CN&format=rss",
}

# Topic → Region 映射（议题地理关联）
TOPIC_REGION_MAP: Dict[str, List[RegionCode]] = {
    "china": [RegionCode.CN, RegionCode.HK, RegionCode.TW],
    "us": [RegionCode.US, RegionCode.CA],
    "europe": [RegionCode.EU, RegionCode.UK, RegionCode.DE, RegionCode.FR],
    "middle east": [RegionCode.AE, RegionCode.SA],
    "asia": [RegionCode.JP, RegionCode.KR, RegionCode.IN, RegionCode.SG, RegionCode.ID, RegionCode.TH, RegionCode.VN, RegionCode.MY, RegionCode.PH],
    "africa": [RegionCode.AE],
    "latin america": [RegionCode.BR, RegionCode.MX],
    "russia": [RegionCode.RU],
    "ukraine": [RegionCode.EU, RegionCode.RU],
    "taiwan": [RegionCode.TW, RegionCode.CN, RegionCode.US],
    "gaza": [RegionCode.AE, RegionCode.SA],
    "oil": [RegionCode.AE, RegionCode.SA, RegionCode.RU, RegionCode.US],
    "ai": [RegionCode.US, RegionCode.CN, RegionCode.EU, RegionCode.JP],
    "trade": [RegionCode.US, RegionCode.CN, RegionCode.EU, RegionCode.SG, RegionCode.HK],
    "climate": [RegionCode.GLOBAL],
    "election": [RegionCode.US, RegionCode.EU, RegionCode.CN],
}


# ===========================================================================
# NewsFetcher v8
# ===========================================================================
class NewsFetcher:
    """全球情报级多源新闻抓取器 v8。

    支持：
    - 多源 RSS（按区域 + 语言）
    - Google News RSS 搜索
    - Bing News RSS 搜索
    - NewsAPI（需要 API key）
    - GDELT 事件查询
    - 多语言 topic 扩展
    - 区域自动推断
    - 相关性过滤 + 去重
    """

    def __init__(
        self,
        llm_router: Optional[Any] = None,
        newsapi_key: Optional[str] = None,
        http_timeout: int = 30,
    ):
        self.sources: List[NewsSource] = []
        self.llm_router = llm_router
        self.newsapi_key = newsapi_key
        self.http_timeout = http_timeout
        self._session: Optional[aiohttp.ClientSession] = None

    # -----------------------------------------------------------------------
    # 生命周期
    # -----------------------------------------------------------------------
    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.http_timeout),
            )
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    # -----------------------------------------------------------------------
    # 源注册（保留旧接口）
    # -----------------------------------------------------------------------
    def register_source(self, source: NewsSource) -> None:
        self.sources.append(source)

    # -----------------------------------------------------------------------
    # v8: 议题扩展（topic → 相关关键词）
    # -----------------------------------------------------------------------
    async def expand_topic_keywords(self, topic: str) -> List[str]:
        """使用 LLM 扩展议题关键词，生成多语言相关关键词。"""
        keywords = [topic]

        # 1. 简单规则扩展（无需 LLM）
        lower_topic = topic.lower()
        for key, regions in TOPIC_REGION_MAP.items():
            if key in lower_topic or lower_topic in key:
                # 添加区域相关变体
                for region in regions:
                    keywords.append(f"{topic} {region.value}")

        # 2. 如果有 LLM，使用 LLM 扩展
        if self.llm_router:
            try:
                prompt = PromptTemplates.render(
                    PromptTemplates.TOPIC_EXPANSION_V1,
                    {"topic": topic},
                )
                request = LLMRequest(
                    prompt=prompt,
                    provider=ModelProvider.OPENAI,
                    temperature=0.3,
                    max_tokens=512,
                )
                resp = await self.llm_router.generate(request)
                data = _try_parse_json(resp.content)
                if data and "keywords" in data:
                    extra = data["keywords"]
                    if isinstance(extra, list):
                        for kw in extra:
                            if isinstance(kw, str) and kw not in keywords:
                                keywords.append(kw)
            except Exception:
                pass

        return keywords[:20]  # 最多 20 个

    # -----------------------------------------------------------------------
    # v8: 区域自动推断（topic → regions）
    # -----------------------------------------------------------------------
    def infer_regions(self, topic: str) -> List[RegionCode]:
        """根据 topic 自动推断相关区域。"""
        regions: List[RegionCode] = []
        lower_topic = topic.lower()

        for key, mapped_regions in TOPIC_REGION_MAP.items():
            if key in lower_topic or lower_topic in key:
                for r in mapped_regions:
                    if r not in regions:
                        regions.append(r)

        # 如果没有匹配，默认全球
        if not regions:
            regions = [RegionCode.GLOBAL]

        return regions

    # -----------------------------------------------------------------------
    # v8: 语言自动推断（topic → languages）
    # -----------------------------------------------------------------------
    def infer_languages(self, topic: str) -> List[LanguageCode]:
        """根据 topic 语言自动推断搜索语言。"""
        languages = [LanguageCode.EN]

        # 检测中文
        if any('\u4e00' <= ch <= '\u9fff' for ch in topic):
            languages.append(LanguageCode.ZH)

        # 检测阿拉伯语
        if any('\u0600' <= ch <= '\u06ff' for ch in topic):
            languages.append(LanguageCode.AR)

        # 检测俄语/西里尔
        if any('\u0400' <= ch <= '\u04ff' for ch in topic):
            languages.append(LanguageCode.RU)

        # 检测日语
        if any('\u3040' <= ch <= '\u30ff' for ch in topic):
            languages.append(LanguageCode.JA)

        # 检测韩语
        if any('\uac00' <= ch <= '\ud7af' for ch in topic):
            languages.append(LanguageCode.KO)

        # 去重
        seen = set()
        result = []
        for lang in languages:
            if lang not in seen:
                seen.add(lang)
                result.append(lang)
        return result

    # -----------------------------------------------------------------------
    # v8: 多源抓取（核心）
    # -----------------------------------------------------------------------
    async def fetch_multi_source(
        self,
        topic: str,
        regions: Optional[List[RegionCode]] = None,
        languages: Optional[List[LanguageCode]] = None,
        max_per_source: int = 20,
        max_total: int = 100,
        options: Optional[Dict[str, Any]] = None,
    ) -> List[RawNewsItem]:
        """v8 核心入口：多源、多语言、多区域抓取。

        1. 扩展 topic 关键词
        2. 推断 region + language
        3. 并行抓取所有源
        4. 去重 + 过滤
        5. 返回合并列表
        """
        opts = options or {}

        # 1. 扩展关键词
        keywords = await self.expand_topic_keywords(topic)

        # 2. 推断区域和语言
        target_regions = regions or self.infer_regions(topic)
        target_languages = languages or self.infer_languages(topic)

        # 3. 收集所有抓取任务
        tasks: List[Any] = []
        task_labels: List[str] = []

        # 3a. RSS 源（按区域）
        for region in target_regions:
            rss_list = RSS_SOURCES_BY_REGION.get(region, [])
            for rss in rss_list:
                tasks.append(
                    self._fetch_rss(
                        rss["url"], rss["name"], rss.get("language", LanguageCode.EN),
                        rss.get("reliability_score", 0.8), max_per_source
                    )
                )
                task_labels.append(f"rss:{rss['name']}")

        # 3b. Google News RSS（按语言）
        for lang in target_languages:
            template = GOOGLE_NEWS_RSS_TEMPLATES.get(lang)
            if template:
                for kw in keywords[:3]:
                    url = template.format(quote(kw))
                    tasks.append(
                        self._fetch_rss(url, f"GoogleNews-{lang.value}", lang, 0.7, max_per_source)
                    )
                    task_labels.append(f"google_news:{lang.value}:{kw}")

        # 3c. Bing News RSS
        for lang in target_languages:
            template = BING_NEWS_RSS_TEMPLATES.get(lang)
            if template:
                for kw in keywords[:2]:
                    url = template.format(quote(kw))
                    tasks.append(
                        self._fetch_rss(url, f"BingNews-{lang.value}", lang, 0.7, max_per_source)
                    )
                    task_labels.append(f"bing_news:{lang.value}:{kw}")

        # 3d. NewsAPI（如果配置了 key）
        if self.newsapi_key:
            for kw in keywords[:3]:
                tasks.append(self._fetch_newsapi(kw, target_languages, max_per_source))
                task_labels.append(f"newsapi:{kw}")

        # 3e. GDELT
        for kw in keywords[:2]:
            tasks.append(self._fetch_gdelt(kw, max_per_source))
            task_labels.append(f"gdelt:{kw}")

        # 4. 并行执行（限制并发）
        max_concurrency = opts.get("max_fetch_concurrency", 10)
        sem = asyncio.Semaphore(max_concurrency)

        async def _fetch_with_sem(task, label):
            async with sem:
                try:
                    return await task
                except Exception as exc:
                    return []  # 失败返回空列表

        wrapped = [_fetch_with_sem(t, l) for t, l in zip(tasks, task_labels)]
        results = await asyncio.gather(*wrapped, return_exceptions=True)

        # 5. 合并 + 去重
        all_items: List[RawNewsItem] = []
        seen_hashes: set = set()

        for label, result in zip(task_labels, results):
            if isinstance(result, Exception):
                continue
            if not isinstance(result, list):
                continue
            for item in result:
                if not isinstance(item, RawNewsItem):
                    continue
                # 去重：title + content hash
                dup_key = _item_hash(item)
                if dup_key in seen_hashes:
                    continue
                seen_hashes.add(dup_key)
                all_items.append(item)

        # 6. 限制总数
        return all_items[:max_total]

    # -----------------------------------------------------------------------
    # v8: RSS 抓取实现
    # -----------------------------------------------------------------------
    async def _fetch_rss(
        self,
        url: str,
        source_name: str,
        language: LanguageCode,
        reliability: float,
        max_items: int,
    ) -> List[RawNewsItem]:
        """从 RSS URL 抓取新闻。"""
        items: List[RawNewsItem] = []
        try:
            session = await self._get_session()
            async with session.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; FZQ-AI/1.0)"
            }) as resp:
                if resp.status != 200:
                    return items
                text = await resp.text()
                if not text.strip():
                    return items

                # 尝试解析 RSS XML
                try:
                    root = ET.fromstring(text.encode('utf-8'))
                except ET.ParseError:
                    return items

                # 查找所有 item/entry
                entries = root.findall(".//item") or root.findall(".//entry")
                for entry in entries[:max_items]:
                    title = _xml_text(entry, "title", "Untitled")
                    link = _xml_text(entry, "link", "")
                    if not link:
                        link_elem = entry.find("link")
                        if link_elem is not None and link_elem.get("href"):
                            link = link_elem.get("href")
                    desc = _xml_text(entry, "description", "")
                    if not desc:
                        desc = _xml_text(entry, "summary", "")
                    pub_date = _xml_text(entry, "pubDate", "")
                    if not pub_date:
                        pub_date = _xml_text(entry, "published", "")

                    # 构建 source
                    source = NewsSource(
                        name=source_name,
                        url=link,
                        region=RegionCode.GLOBAL,
                        language=language,
                        reliability_score=reliability,
                        source_type="rss",
                    )

                    items.append(
                        RawNewsItem(
                            id=generate_id(),
                            title=title,
                            content=desc or title,
                            source=source,
                            published_at=_parse_rss_date(pub_date),
                            fetched_at=datetime.now(timezone.utc),
                            language=language,
                            region=RegionCode.GLOBAL,
                            url=link,
                        )
                    )
        except Exception:
            pass
        return items

    # -----------------------------------------------------------------------
    # v8: NewsAPI 抓取
    # -----------------------------------------------------------------------
    async def _fetch_newsapi(
        self,
        query: str,
        languages: List[LanguageCode],
        max_items: int,
    ) -> List[RawNewsItem]:
        """从 NewsAPI 抓取新闻。"""
        if not self.newsapi_key:
            return []
        items: List[RawNewsItem] = []
        try:
            session = await self._get_session()
            lang_str = ",".join(l.value for l in languages[:2])
            url = (
                f"https://newsapi.org/v2/everything"
                f"?q={quote(query)}"
                f"&language={lang_str}"
                f"&pageSize={max_items}"
                f"&sortBy=publishedAt"
                f"&apiKey={self.newsapi_key}"
            )
            async with session.get(url) as resp:
                if resp.status != 200:
                    return items
                data = await resp.json()
                articles = data.get("articles", [])
                for article in articles[:max_items]:
                    title = article.get("title", "Untitled")
                    content = article.get("description", "") or article.get("content", "")
                    source_name = article.get("source", {}).get("name", "NewsAPI")
                    pub_at = article.get("publishedAt", "")
                    link = article.get("url", "")
                    lang = _detect_lang_from_text(title) or LanguageCode.EN

                    source = NewsSource(
                        name=source_name,
                        url=link,
                        region=RegionCode.GLOBAL,
                        language=lang,
                        reliability_score=0.75,
                        source_type="api",
                    )
                    items.append(
                        RawNewsItem(
                            id=generate_id(),
                            title=title,
                            content=content,
                            source=source,
                            published_at=_parse_iso_date(pub_at),
                            fetched_at=datetime.now(timezone.utc),
                            language=lang,
                            region=RegionCode.GLOBAL,
                            url=link,
                        )
                    )
        except Exception:
            pass
        return items

    # -----------------------------------------------------------------------
    # v8: GDELT 抓取
    # -----------------------------------------------------------------------
    async def _fetch_gdelt(
        self,
        query: str,
        max_items: int,
    ) -> List[RawNewsItem]:
        """从 GDELT API 抓取新闻。"""
        items: List[RawNewsItem] = []
        try:
            session = await self._get_session()
            # GDELT GKG API
            url = f"https://api.gdeltproject.org/api/v2/doc/doc?query={quote(query)}&mode=artlist&format=json"
            async with session.get(url) as resp:
                if resp.status != 200:
                    return items
                data = await resp.json()
                articles = data.get("articles", []) if isinstance(data, dict) else []
                for article in articles[:max_items]:
                    title = article.get("title", "Untitled")
                    url_link = article.get("url", "")
                    lang = _detect_lang_from_text(title) or LanguageCode.EN
                    source = NewsSource(
                        name=article.get("domain", "GDELT"),
                        url=url_link,
                        region=RegionCode.GLOBAL,
                        language=lang,
                        reliability_score=0.7,
                        source_type="api",
                    )
                    items.append(
                        RawNewsItem(
                            id=generate_id(),
                            title=title,
                            content="",
                            source=source,
                            published_at=datetime.now(timezone.utc),
                            fetched_at=datetime.now(timezone.utc),
                            language=lang,
                            region=RegionCode.GLOBAL,
                            url=url_link,
                        )
                    )
        except Exception:
            pass
        return items

    # -----------------------------------------------------------------------
    # v8: 相关性过滤（LLM 评分）
    # -----------------------------------------------------------------------
    async def filter_by_relevance(
        self,
        items: List[RawNewsItem],
        topic: str,
        min_score: float = 0.5,
    ) -> List[RawNewsItem]:
        """使用 LLM 过滤低相关性新闻。"""
        if not self.llm_router or not items:
            return items

        # 批量过滤（每次最多 10 条）
        filtered: List[RawNewsItem] = []
        batch_size = 10

        for i in range(0, len(items), batch_size):
            batch = items[i : i + batch_size]
            batch_text = "\n\n".join(
                f"[{idx}] Title: {item.title}\nContent: {item.content[:200]}"
                for idx, item in enumerate(batch)
            )

            try:
                prompt = PromptTemplates.render(
                    PromptTemplates.NEWS_RELEVANCE_FILTER_V1,
                    {
                        "topic": topic,
                        "news_batch": batch_text,
                    },
                )
                request = LLMRequest(
                    prompt=prompt,
                    provider=ModelProvider.OPENAI,
                    temperature=0.1,
                    max_tokens=1024,
                )
                resp = await self.llm_router.generate(request)
                data = _try_parse_json(resp.content)
                if data and "scores" in data and isinstance(data["scores"], list):
                    scores = data["scores"]
                    for idx, item in enumerate(batch):
                        if idx < len(scores):
                            score = float(scores[idx]) if isinstance(scores[idx], (int, float)) else 0.5
                            if score >= min_score:
                                item.raw_metadata["relevance_score"] = score
                                filtered.append(item)
                        else:
                            filtered.append(item)
                else:
                    filtered.extend(batch)
            except Exception:
                filtered.extend(batch)

        return filtered

    # -----------------------------------------------------------------------
    # v8: 过滤广告 / PR / 非新闻
    # -----------------------------------------------------------------------
    def filter_non_news(self, items: List[RawNewsItem]) -> List[RawNewsItem]:
        """过滤广告、PR、非新闻内容。"""
        filtered = []
        ad_keywords = [
            "advertisement", "sponsored", "promoted", "pr newswire",
            "press release", "advertorial", "buy now", "discount", "coupon",
        ]
        for item in items:
            title_lower = item.title.lower()
            content_lower = item.content.lower() if item.content else ""
            combined = title_lower + " " + content_lower
            if any(kw in combined for kw in ad_keywords):
                continue
            filtered.append(item)
        return filtered

    # -----------------------------------------------------------------------
    # v8: 计算 intake 平衡报告
    # -----------------------------------------------------------------------
    def compute_balance_report(self, items: List[RawNewsItem]) -> Dict[str, Any]:
        """计算新闻 intake 的区域/语言/来源平衡分布。"""
        region_counts: Dict[str, int] = {}
        language_counts: Dict[str, int] = {}
        source_counts: Dict[str, int] = {}

        for item in items:
            r = item.region.value if item.region else "unknown"
            region_counts[r] = region_counts.get(r, 0) + 1

            l = item.language.value if item.language else "unknown"
            language_counts[l] = language_counts.get(l, 0) + 1

            s = item.source.name if item.source else "unknown"
            source_counts[s] = source_counts.get(s, 0) + 1

        total = len(items) if items else 1

        return {
            "region_distribution": {
                k: {"count": v, "percentage": round(v / total * 100, 1)}
                for k, v in sorted(region_counts.items(), key=lambda x: -x[1])
            },
            "language_distribution": {
                k: {"count": v, "percentage": round(v / total * 100, 1)}
                for k, v in sorted(language_counts.items(), key=lambda x: -x[1])
            },
            "source_distribution": {
                k: {"count": v, "percentage": round(v / total * 100, 1)}
                for k, v in sorted(source_counts.items(), key=lambda x: -x[1])[:10]
            },
            "total_items": len(items),
            "region_balance_score": _compute_balance_score(region_counts),
            "language_balance_score": _compute_balance_score(language_counts),
            "source_balance_score": _compute_balance_score(source_counts),
        }

    # -----------------------------------------------------------------------
    # 旧接口兼容（保留）
    # -----------------------------------------------------------------------
    async def fetch_from_source(
        self, source: NewsSource, max_items: int = 50
    ) -> List[RawNewsItem]:
        return await self._fetch_rss(
            source.url or "", source.name, source.language,
            source.reliability_score, max_items,
        )

    async def fetch_all(
        self, max_items_per_source: int = 50
    ) -> List[RawNewsItem]:
        all_items: List[RawNewsItem] = []
        for source in self.sources:
            items = await self.fetch_from_source(source, max_items_per_source)
            all_items.extend(items)
        return all_items

    async def fetch_stream(
        self, source: NewsSource
    ) -> AsyncIterator[RawNewsItem]:
        items = await self.fetch_from_source(source)
        for item in items:
            yield item


# ===========================================================================
# 辅助函数
# ===========================================================================

def _try_parse_json(text: str) -> Optional[Dict[str, Any]]:
    """尝试解析 JSON，失败返回 None。"""
    import json
    try:
        return json.loads(text.strip())
    except Exception:
        return None


def _xml_text(parent, tag: str, default: str = "") -> str:
    """从 XML 元素安全提取文本。"""
    elem = parent.find(f".//{tag}")
    if elem is not None and elem.text:
        return elem.text.strip()
    return default


def _parse_rss_date(date_str: str) -> datetime:
    """解析 RSS 日期字符串。"""
    from email.utils import parsedate_to_datetime
    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        return datetime.now(timezone.utc)


def _parse_iso_date(date_str: str) -> datetime:
    """解析 ISO 8601 日期字符串。"""
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


def _detect_lang_from_text(text: str) -> Optional[LanguageCode]:
    """根据文本内容简单检测语言。"""
    if not text:
        return None
    if any('\u4e00' <= ch <= '\u9fff' for ch in text):
        return LanguageCode.ZH
    if any('\u0600' <= ch <= '\u06ff' for ch in text):
        return LanguageCode.AR
    if any('\u0400' <= ch <= '\u04ff' for ch in text):
        return LanguageCode.RU
    if any('\u3040' <= ch <= '\u30ff' for ch in text):
        return LanguageCode.JA
    if any('\uac00' <= ch <= '\ud7af' for ch in text):
        return LanguageCode.KO
    return LanguageCode.EN


def _item_hash(item: RawNewsItem) -> str:
    """生成新闻去重 hash（title + content 前 200 字）。"""
    text = (item.title or "") + (item.content or "")[:200]
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _compute_balance_score(counts: Dict[str, int]) -> float:
    """计算平衡度评分（0-1，1 表示完全平衡）。"""
    if not counts:
        return 0.0
    total = sum(counts.values())
    if total == 0:
        return 0.0
    n = len(counts)
    ideal = total / n
    # 使用标准差计算偏差
    variance = sum((v - ideal) ** 2 for v in counts.values()) / n
    std_dev = variance ** 0.5
    max_possible = ideal * (n - 1) / n ** 0.5 if n > 1 else 0
    if max_possible == 0:
        return 1.0
    score = 1.0 - (std_dev / max_possible)
    return max(0.0, min(1.0, round(score, 2)))
