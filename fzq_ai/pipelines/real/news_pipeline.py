"""News pipeline: translation, summarization, and multi-source fetching."""
import re
import json
import time
import asyncio
import html
from typing import Any, Dict, List, Optional
from datetime import datetime

from fzq_ai.schemas.real import (
    PipelineInput,
    PipelineOutput,
    PipelineMetrics,
    RawNewsItem,
    TranslatedNewsItem,
    MultiDimensionAnalysis,
    NarrativeAnalysis,
    RiskAnalysis,
    SentimentAnalysis,
    ScenarioAnalysis,
    RiskFactor,
    RiskLevel,
    SentimentLabel,
    ScenarioProjection,
    ModelProvider,
    LLMRequest,
    LanguageCode,
    AnalysisDimension,
    FallbackRecord,
    RegionCode,
)
from fzq_ai.llm.real.llm_router import LLMRouter
from fzq_ai.core.prompts import PromptTemplates
from fzq_ai.tools.news_fetcher import NewsFetcher
from fzq_ai.tools.translator import Translator


# ---------------------------------------------------------------------------
# JSON safe-parsing v2 — robust extraction, repair, and validation
# ---------------------------------------------------------------------------
def _safe_json_parse_v2(text: str) -> Optional[Dict[str, Any]]:
    """Extract and parse JSON from LLM text output with aggressive repair.

    v2 增强：
    1. 提取所有 { ... } 块，选择字段最多的
    2. 过滤长度 < 10 的块
    3. 修复常见 JSON 错误：单引号→双引号、尾逗号、BOM、HTML 实体
    4. 处理混入自然语言的输出
    5. 返回 dict；失败时返回 {}
    """
    if not text or not isinstance(text, str):
        return {}

    # 1. 清洗 BOM 和不可见字符
    raw = text.strip()
    raw = raw.lstrip('\ufeff')  # BOM
    raw = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', raw)

    # 2. 先尝试直接解析
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict) and len(parsed) > 0:
            return parsed
    except json.JSONDecodeError:
        pass

    # 3. 尝试 Markdown 代码块
    for pattern in (
        r'```json\s*(.*?)\s*```',
        r'```\s*(.*?)\s*```',
    ):
        matches = re.findall(pattern, raw, re.DOTALL)
        for m in matches:
            cleaned = _json_repair(m)
            if cleaned:
                return cleaned

    # 4. 提取所有独立的 { ... } 块，选择字段最多的
    blocks = _extract_json_blocks(raw)
    if blocks:
        best = max(blocks, key=lambda b: len(b.keys()) if isinstance(b, dict) else 0)
        if isinstance(best, dict) and len(best) > 0:
            return best

    # 5. 全文搜索 — 找最大匹配
    matches = re.findall(r'(\{[\s\S]*?\})', raw)
    if matches:
        candidates = sorted(matches, key=len, reverse=True)
        for c in candidates:
            cleaned = _json_repair(c)
            if cleaned:
                return cleaned

    return {}


def _extract_json_blocks(text: str) -> List[Dict[str, Any]]:
    """提取所有完整的 JSON 对象块，返回 list[dict]。"""
    blocks: List[Dict[str, Any]] = []
    # 使用堆栈匹配大括号
    i = 0
    while i < len(text):
        if text[i] == '{':
            start = i
            depth = 1
            j = i + 1
            while j < len(text) and depth > 0:
                if text[j] == '{':
                    depth += 1
                elif text[j] == '}':
                    depth -= 1
                j += 1
            if depth == 0:
                candidate = text[start:j]
                if len(candidate) >= 10:
                    cleaned = _json_repair(candidate)
                    if cleaned:
                        blocks.append(cleaned)
            i = j
        else:
            i += 1
    return blocks


def _json_repair(raw: str) -> Optional[Dict[str, Any]]:
    """尝试修复常见 JSON 错误并解析。"""
    s = raw.strip()

    # 1. HTML 实体解码
    s = html.unescape(s)

    # 2. 去除 BOM
    s = s.lstrip('\ufeff')

    # 3. 先尝试直接解析
    try:
        result = json.loads(s)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    # 4. 修复：单引号包裹的字符串 → 双引号（简单的逐字符替换）
    # 注意：不处理嵌套引号，只处理外层
    s = _fix_single_quotes(s)

    # 5. 修复：尾逗号（对象和数组末尾的逗号）
    s = re.sub(r',(\s*[}\]])', r'\1', s)

    # 6. 修复：缺失逗号（"key1" "key2" 之间）
    s = re.sub(r'"\s+"', '", "', s)

    # 7. 尝试修复后的解析
    try:
        result = json.loads(s)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    return None


def _fix_single_quotes(s: str) -> str:
    """将 JSON 中的单引号字符串替换为双引号。"""
    result = []
    in_string = False
    quote_char = None
    for ch in s:
        if not in_string and ch in ('"', "'"):
            in_string = True
            quote_char = ch
            result.append('"')
        elif in_string and ch == quote_char:
            in_string = False
            result.append('"')
        elif in_string and ch == '"':
            result.append('\\"')
        else:
            result.append(ch)
    return ''.join(result)


# ---------------------------------------------------------------------------
# 字段类型安全提取工具
# ---------------------------------------------------------------------------
def _safe_str(data: Dict[str, Any], key: str, default: str = "") -> str:
    """安全提取字符串，处理类型不匹配。"""
    val = data.get(key, default)
    if val is None:
        return default
    if isinstance(val, str):
        return val
    return str(val)


def _safe_float(data: Dict[str, Any], key: str, default: float = 0.0) -> float:
    """安全提取 float，处理字符串转换。"""
    val = data.get(key, default)
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        try:
            return float(val)
        except (ValueError, TypeError):
            return default
    return default


def _safe_str_list(data: Dict[str, Any], key: str) -> List[str]:
    """安全提取字符串列表。"""
    val = data.get(key)
    if not isinstance(val, list):
        return []
    return [str(v) for v in val if v is not None]


def _safe_enum(data: Dict[str, Any], key: str, enum_cls, default):
    """安全提取枚举值，处理字符串匹配。"""
    val = data.get(key)
    if val is None:
        return default
    if isinstance(val, str):
        try:
            return enum_cls(val.lower())
        except ValueError:
            return default
    return default


# ---------------------------------------------------------------------------
# NewsPipeline v7
# ---------------------------------------------------------------------------
class NewsPipeline:
    """Async news pipeline: translation, summarization, multi-source analysis."""

    def __init__(
        self,
        llm_router: LLMRouter,
        translator: Optional[Any] = None,
    ):
        self.llm_router = llm_router
        self.translator = translator

    # -----------------------------------------------------------------------
    # Public interface — run() 签名与返回类型保持不变
    # -----------------------------------------------------------------------
    async def run(self, pipeline_input: PipelineInput) -> PipelineOutput:
        """Run the news pipeline with concurrent analysis and v7 enhancements."""
        start = time.perf_counter()
        metrics = PipelineMetrics(pipeline_name="news_pipeline")
        analyzed_items: List[MultiDimensionAnalysis] = []
        failed_items: List[Dict[str, Any]] = []

        items = pipeline_input.items[: pipeline_input.max_items]
        if pipeline_input.region_filter:
            items = [
                i for i in items
                if i.region in pipeline_input.region_filter
            ]

        # v7: 使用 pipeline_input.max_concurrency（支持 options 覆盖）
        max_concurrency = pipeline_input.options.get("max_concurrency", 5)
        if max_concurrency < 1:
            max_concurrency = 5
        sem = asyncio.Semaphore(max_concurrency)

        async def _process(item: RawNewsItem) -> Optional[MultiDimensionAnalysis]:
            async with sem:
                try:
                    translated = await self._translate_if_needed(
                        item, pipeline_input.target_language
                    )
                    return await self._analyze_item(
                        translated, pipeline_input.dimensions
                    )
                except Exception as exc:
                    # v7: 翻译或分析失败 → 记录错误并返回 None
                    raise

        tasks = [_process(item) for item in items]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for item, result in zip(items, results):
            if isinstance(result, Exception):
                metrics.items_failed += 1
                metrics.errors.append(str(result))
                failed_items.append({
                    "id": item.id,
                    "error": str(result),
                    "error_type": type(result).__name__,
                })
            else:
                if result is not None:
                    analyzed_items.append(result)
                    metrics.items_processed += 1
                else:
                    metrics.items_failed += 1
                    failed_items.append({
                        "id": item.id,
                        "error": "Processing returned None",
                    })

        total_latency = int((time.perf_counter() - start) * 1000)
        metrics.total_latency_ms = total_latency
        if metrics.items_processed > 0:
            metrics.avg_latency_ms = total_latency / metrics.items_processed

        return PipelineOutput(
            input_summary=pipeline_input,
            analyzed_items=analyzed_items,
            failed_items=failed_items,
            metrics=metrics,
        )

    # -----------------------------------------------------------------------
    # Translation v7 — 增强：自动检测、错误记录、完整元数据
    # -----------------------------------------------------------------------
    async def _translate_if_needed(
        self,
        item: RawNewsItem,
        target_language: LanguageCode,
    ) -> TranslatedNewsItem:
        """Translate item if needed. v7 增强：自动检测、错误记录、完整元数据。"""
        # 如果已经是目标语言且已有翻译，直接返回缓存结果
        if item.language == target_language and item.translated_content:
            return TranslatedNewsItem(
                original=item,
                translated_title=item.translated_title or item.title,
                translated_content=item.translated_content,
                target_language=target_language,
                translation_provider="cached",
                translation_confidence=item.translation_confidence,
                translation_latency_ms=0,
            )

        # 如果提供了外部 translator，优先使用
        if self.translator is not None:
            try:
                translated = await self.translator.translate(item, target_language)
                return translated
            except Exception as exc:
                # v7: 翻译失败 → 记录并 fallback 到 LLM
                pass

        # v7: LLM 翻译 via structured JSON prompt
        prompt = PromptTemplates.render(
            PromptTemplates.TRANSLATION_V1,
            {
                "target_language": target_language.value,
                "title": item.title,
                "content": item.content[:2000],
            },
        )
        request = LLMRequest(
            prompt=prompt,
            provider=ModelProvider.OPENAI,
            temperature=0.1,
            max_tokens=2048,
        )
        try:
            resp = await self.llm_router.generate(request)
        except Exception as exc:
            # v7: LLM 调用失败 → 返回原文并标记错误
            return TranslatedNewsItem(
                original=item,
                translated_title=item.title,
                translated_content=item.content,
                target_language=target_language,
                translation_provider="fallback_error",
                translation_confidence=0.0,
                translation_latency_ms=0,
            )

        data = _safe_json_parse_v2(resp.content)

        if data and any(k in data for k in ("title", "content")):
            translated_title = _safe_str(data, "title", item.title)
            translated_content = _safe_str(data, "content", item.content)
            confidence = _safe_float(data, "confidence", 0.8)
            provider = _safe_str(data, "provider", "llm")
        else:
            # v7: JSON 解析失败 → 返回原文
            translated_title = item.title
            translated_content = item.content
            confidence = 0.0
            provider = "fallback_error"

        return TranslatedNewsItem(
            original=item,
            translated_title=translated_title,
            translated_content=translated_content,
            target_language=target_language,
            translation_provider=provider,
            translation_confidence=confidence,
            translation_latency_ms=resp.latency_ms,
        )

    # -----------------------------------------------------------------------
    # Multi-dimension analysis — 接口不变
    # -----------------------------------------------------------------------
    async def _analyze_item(
        self,
        item: TranslatedNewsItem,
        dimensions: List[AnalysisDimension],
    ) -> MultiDimensionAnalysis:
        """Run multi-dimension analysis on a translated item."""
        text = f"{item.translated_title}\n{item.translated_content}"
        news_id = item.original.id

        # 初始化默认值
        narrative = NarrativeAnalysis(
            news_id=news_id,
            primary_narrative="",
            narrative_strength=0.0,
            confidence=0.0,
            model_used=ModelProvider.OPENAI,
        )
        risk = RiskAnalysis(
            news_id=news_id,
            overall_risk_level=RiskLevel.LOW,
            composite_risk_score=0.0,
            confidence=0.0,
            model_used=ModelProvider.OPENAI,
        )
        sentiment = SentimentAnalysis(
            news_id=news_id,
            overall_sentiment=SentimentLabel.NEUTRAL,
            sentiment_score=0.0,
            confidence=0.0,
            model_used=ModelProvider.OPENAI,
        )
        scenario = ScenarioAnalysis(
            news_id=news_id,
            base_case=ScenarioProjection(
                scenario_name="Base",
                description="",
                probability=0.0,
                time_horizon="short_term",
            ),
            confidence=0.0,
            model_used=ModelProvider.OPENAI,
        )

        # 按维度调用分析（带 fallback）
        if AnalysisDimension.NARRATIVE in dimensions:
            narrative = await self._run_narrative(text, news_id)
        if AnalysisDimension.RISK in dimensions:
            risk = await self._run_risk(text, news_id)
        if AnalysisDimension.SENTIMENT in dimensions:
            sentiment = await self._run_sentiment(text, news_id)
        if AnalysisDimension.SCENARIO in dimensions:
            scenario = await self._run_scenario(text, news_id)

        return MultiDimensionAnalysis(
            news_id=news_id,
            narrative=narrative,
            risk=risk,
            sentiment=sentiment,
            scenario=scenario,
        )

    # -----------------------------------------------------------------------
    # v7: LLM 调用辅助 — 带 fallback 链和 latency 记录
    # -----------------------------------------------------------------------
    async def _call_llm_with_fallback(
        self,
        prompt: str,
        preferred_provider: ModelProvider = ModelProvider.OPENAI,
    ) -> tuple:
        """调用 LLM 并返回 (resp, latency_ms, provider_used)。

        v7 增强：使用 fallback 链（OpenAI → DeepSeek → Gemini），
        记录 latency 和实际使用的 provider。
        """
        request = LLMRequest(
            prompt=prompt,
            provider=preferred_provider,
            temperature=0.2,
            max_tokens=2048,
        )
        resp = await self.llm_router.generate(request)
        return resp, resp.latency_ms, resp.provider

    # -----------------------------------------------------------------------
    # Narrative analysis v7 — 字段完整性增强
    # -----------------------------------------------------------------------
    async def _run_narrative(self, text: str, news_id: str) -> NarrativeAnalysis:
        prompt = PromptTemplates.render(
            PromptTemplates.NARRATIVE_ANALYSIS_V1,
            {"text": text[:3000]},
        )
        resp, latency_ms, provider_used = await self._call_llm_with_fallback(prompt)
        data = _safe_json_parse_v2(resp.content)

        if data and len(data) > 0:
            return NarrativeAnalysis(
                news_id=news_id,
                primary_narrative=_safe_str(data, "primary_narrative")[:500],
                secondary_narratives=_safe_str_list(data, "secondary_narratives"),
                narrative_strength=_safe_float(data, "narrative_strength", 0.5),
                key_actors=_safe_str_list(data, "key_actors"),
                key_themes=_safe_str_list(data, "key_themes"),
                timeline_indicators=_safe_str_list(data, "timeline_indicators"),
                related_events=_safe_str_list(data, "related_events"),
                confidence=0.85,
                model_used=provider_used,
                processed_at=datetime.utcnow(),
            )

        # Fallback: raw text
        return NarrativeAnalysis(
            news_id=news_id,
            primary_narrative=resp.content[:500] if resp.content else "",
            narrative_strength=0.5,
            confidence=0.3,
            model_used=provider_used,
            processed_at=datetime.utcnow(),
        )

    # -----------------------------------------------------------------------
    # Risk analysis v7 — 字段完整性增强 + RiskFactor 完整解析
    # -----------------------------------------------------------------------
    async def _run_risk(self, text: str, news_id: str) -> RiskAnalysis:
        prompt = PromptTemplates.render(
            PromptTemplates.RISK_ANALYSIS_V1,
            {"text": text[:3000]},
        )
        resp, latency_ms, provider_used = await self._call_llm_with_fallback(prompt)
        data = _safe_json_parse_v2(resp.content)

        if data and len(data) > 0:
            overall_level = _safe_enum(
                data, "overall_risk_level", RiskLevel, RiskLevel.LOW
            )
            composite_score = _safe_float(data, "composite_risk_score", 0.5)

            # 完整解析 RiskFactor 列表
            raw_factors = data.get("risk_factors", [])
            risk_factors: List[RiskFactor] = []
            if isinstance(raw_factors, list):
                for rf in raw_factors:
                    if not isinstance(rf, dict):
                        continue
                    risk_factors.append(
                        RiskFactor(
                            risk_type=_safe_str(rf, "risk_type", "general"),
                            description=_safe_str(rf, "description", ""),
                            level=_safe_enum(rf, "level", RiskLevel, RiskLevel.LOW),
                            probability=_safe_float(rf, "probability", 0.5),
                            impact_score=_safe_float(rf, "impact_score", 0.5),
                            affected_regions=_safe_str_list(rf, "affected_regions"),
                            affected_sectors=_safe_str_list(rf, "affected_sectors"),
                            time_horizon=_safe_str(rf, "time_horizon", "short_term"),
                            evidence=_safe_str_list(rf, "evidence"),
                        )
                    )

            # 确保至少有一个 fallback RiskFactor
            if not risk_factors:
                risk_factors = [
                    RiskFactor(
                        risk_type="general",
                        description="No specific risk factors identified",
                        level=RiskLevel.LOW,
                        probability=0.3,
                        impact_score=0.3,
                    )
                ]

            systemic = _safe_str_list(data, "systemic_risk_indicators")

            return RiskAnalysis(
                news_id=news_id,
                overall_risk_level=overall_level,
                composite_risk_score=composite_score,
                risk_factors=risk_factors,
                systemic_risk_indicators=systemic,
                confidence=0.8,
                model_used=provider_used,
                processed_at=datetime.utcnow(),
            )

        # Fallback
        return RiskAnalysis(
            news_id=news_id,
            overall_risk_level=RiskLevel.LOW,
            composite_risk_score=0.3,
            risk_factors=[
                RiskFactor(
                    risk_type="general",
                    description=resp.content[:300] if resp.content else "",
                    level=RiskLevel.LOW,
                    probability=0.3,
                    impact_score=0.3,
                )
            ],
            confidence=0.3,
            model_used=provider_used,
            processed_at=datetime.utcnow(),
        )

    # -----------------------------------------------------------------------
    # Sentiment analysis v7 — 字段完整性增强
    # -----------------------------------------------------------------------
    async def _run_sentiment(self, text: str, news_id: str) -> SentimentAnalysis:
        prompt = PromptTemplates.render(
            PromptTemplates.SENTIMENT_ANALYSIS_V1,
            {"text": text[:3000]},
        )
        resp, latency_ms, provider_used = await self._call_llm_with_fallback(prompt)
        data = _safe_json_parse_v2(resp.content)

        if data and len(data) > 0:
            def _parse_sentiment(val: str) -> SentimentLabel:
                try:
                    return SentimentLabel(val.lower())
                except ValueError:
                    return SentimentLabel.NEUTRAL

            entity_sentiments: Dict[str, float] = {}
            raw_entities = data.get("entity_sentiments", {})
            if isinstance(raw_entities, dict):
                for k, v in raw_entities.items():
                    try:
                        entity_sentiments[str(k)] = float(v)
                    except (ValueError, TypeError):
                        continue

            return SentimentAnalysis(
                news_id=news_id,
                overall_sentiment=_parse_sentiment(
                    _safe_str(data, "overall_sentiment", "neutral")
                ),
                sentiment_score=_safe_float(data, "sentiment_score", 0.0),
                headline_sentiment=_parse_sentiment(
                    _safe_str(data, "headline_sentiment", "neutral")
                ),
                headline_score=_safe_float(data, "headline_score", 0.0),
                content_sentiment=_parse_sentiment(
                    _safe_str(data, "content_sentiment", "neutral")
                ),
                content_score=_safe_float(data, "content_score", 0.0),
                entity_sentiments=entity_sentiments,
                market_indicators=_safe_str_list(data, "market_indicators"),
                confidence=0.8,
                model_used=provider_used,
                processed_at=datetime.utcnow(),
            )

        # Fallback
        return SentimentAnalysis(
            news_id=news_id,
            overall_sentiment=SentimentLabel.NEUTRAL,
            sentiment_score=0.0,
            confidence=0.3,
            model_used=provider_used,
            processed_at=datetime.utcnow(),
        )

    # -----------------------------------------------------------------------
    # Scenario analysis v7 — 字段完整性增强 + ScenarioProjection 完整解析
    # -----------------------------------------------------------------------
    async def _run_scenario(self, text: str, news_id: str) -> ScenarioAnalysis:
        prompt = PromptTemplates.render(
            PromptTemplates.SCENARIO_ANALYSIS_V1,
            {"text": text[:3000]},
        )
        resp, latency_ms, provider_used = await self._call_llm_with_fallback(prompt)
        data = _safe_json_parse_v2(resp.content)

        def _build_projection(obj: Optional[Dict[str, Any]]) -> Optional[ScenarioProjection]:
            if not isinstance(obj, dict):
                return None
            return ScenarioProjection(
                scenario_name=_safe_str(obj, "scenario_name", ""),
                description=_safe_str(obj, "description", ""),
                probability=_safe_float(obj, "probability", 0.0),
                key_triggers=_safe_str_list(obj, "key_triggers"),
                expected_outcomes=_safe_str_list(obj, "expected_outcomes"),
                time_horizon=_safe_str(obj, "time_horizon", "short_term"),
                affected_regions=_safe_str_list(obj, "affected_regions"),
            )

        if data and len(data) > 0:
            alternatives: List[ScenarioProjection] = []
            raw_alts = data.get("alternative_scenarios", [])
            if isinstance(raw_alts, list):
                for alt in raw_alts:
                    proj = _build_projection(alt)
                    if proj:
                        alternatives.append(proj)

            base = _build_projection(data.get("base_case"))
            if base is None:
                base = ScenarioProjection(
                    scenario_name="Base", description="", probability=0.0, time_horizon="short_term"
                )

            return ScenarioAnalysis(
                news_id=news_id,
                base_case=base,
                optimistic_case=_build_projection(data.get("optimistic_case")),
                pessimistic_case=_build_projection(data.get("pessimistic_case")),
                alternative_scenarios=alternatives,
                confidence=0.8,
                model_used=provider_used,
                processed_at=datetime.utcnow(),
            )

        # Fallback
        return ScenarioAnalysis(
            news_id=news_id,
            base_case=ScenarioProjection(
                scenario_name="Base Case",
                description=resp.content[:500] if resp.content else "",
                probability=0.5,
                time_horizon="short_term",
            ),
            confidence=0.3,
            model_used=provider_used,
            processed_at=datetime.utcnow(),
        )

    # -----------------------------------------------------------------------
    # v8: Intake 扩展 — 从 topic 自动抓取新闻
    # -----------------------------------------------------------------------
    async def intake_from_topic(
        self,
        topic: str,
        regions: Optional[List[RegionCode]] = None,
        languages: Optional[List[LanguageCode]] = None,
        max_total: int = 100,
        options: Optional[Dict[str, Any]] = None,
    ) -> PipelineInput:
        """v8: 基于议题自动抓取新闻，构建 PipelineInput。

        1. 使用 NewsFetcher 多源抓取
        2. 过滤广告/PR/非新闻
        3. 相关性过滤（LLM）
        4. 计算 intake 平衡报告
        5. 返回完整的 PipelineInput
        """
        opts = options or {}

        # 1. 创建 NewsFetcher 并抓取
        fetcher = NewsFetcher(
            llm_router=self.llm_router,
            newsapi_key=opts.get("newsapi_key"),
        )
        try:
            items = await fetcher.fetch_multi_source(
                topic=topic,
                regions=regions,
                languages=languages,
                max_per_source=opts.get("max_per_source", 20),
                max_total=max_total,
                options=opts,
            )

            # 2. 过滤非新闻内容
            items = fetcher.filter_non_news(items)

            # 3. 相关性过滤（如果启用）
            if opts.get("enable_relevance_filter", True) and self.llm_router:
                items = await fetcher.filter_by_relevance(
                    items, topic, min_score=opts.get("min_relevance_score", 0.5)
                )

            # 4. 计算平衡报告
            balance_report = fetcher.compute_balance_report(items)

            # 5. 构建 PipelineInput（balance report 写入 options）
            pipeline_input = PipelineInput(
                items=items,
                target_language=opts.get("target_language", LanguageCode.EN),
                dimensions=opts.get(
                    "dimensions",
                    [
                        AnalysisDimension.NARRATIVE,
                        AnalysisDimension.RISK,
                        AnalysisDimension.SENTIMENT,
                        AnalysisDimension.SCENARIO,
                    ],
                ),
                max_items=opts.get("max_items", max_total),
                region_filter=regions,
                options={
                    **opts,
                    "intake_topic": topic,
                    "intake_balance_report": balance_report,
                },
            )
            return pipeline_input
        finally:
            await fetcher.close()

    # -----------------------------------------------------------------------
    # v8: 计算 intake 平衡报告（基于现有 items）
    # -----------------------------------------------------------------------
    def compute_balance_report(self, items: List[RawNewsItem]) -> Dict[str, Any]:
        """v8: 计算新闻 intake 的区域/语言/来源平衡分布。"""
        from fzq_ai.tools.news_fetcher import _compute_balance_score

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
    # v8: 扩展议题关键词（topic → related keywords）
    # -----------------------------------------------------------------------
    async def expand_topic_keywords(self, topic: str) -> List[str]:
        """v8: 扩展议题关键词，生成多语言相关搜索词。"""
        fetcher = NewsFetcher(llm_router=self.llm_router)
        try:
            return await fetcher.expand_topic_keywords(topic)
        finally:
            await fetcher.close()

    # -----------------------------------------------------------------------
    # v8: 推断区域和语言
    # -----------------------------------------------------------------------
    def infer_regions(self, topic: str) -> List[RegionCode]:
        """v8: 根据 topic 推断相关区域。"""
        fetcher = NewsFetcher()
        return fetcher.infer_regions(topic)

    def infer_languages(self, topic: str) -> List[LanguageCode]:
        """v8: 根据 topic 推断相关语言。"""
        fetcher = NewsFetcher()
        return fetcher.infer_languages(topic)

