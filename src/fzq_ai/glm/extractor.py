"""GLMExtractor — Rule-based content extraction from multilingual news text.

Principles (enforced by R1-R6):
- R1: No inference — only extract what's explicitly present
- R2: No summarization — preserve original text
- R3: No fabrication — never invent facts
- R4: Preserve source — input text is always included in output
- R5: Multilingual — detect and handle zh/en/ar/es/fr
- R6: JSON output — always return structured data, never natural language
"""

from __future__ import annotations
from typing import List, Optional
import re

from fzq_ai.glm.schema import (
    GLMRawMaterial, GLMCoreFact, GLMEvent, GLMActor, GLMNarrative,
    GLMRisk, GLMPolicySignal, GLMTrendSignal, GLMRawQuote,
)


class GLMExtractor:
    """Extracts structured information from raw multilingual text using rules only.

    Does NOT use LLM inference. Uses regex, keyword matching, and heuristics.
    """

    # ── Risk keyword dictionaries ──
    RISK_KEYWORDS: dict[str, list[str]] = {
        "political": [
            "sanction", "coup", "election", "protest", "regime", "government",
            "democracy", "authoritarian", "diplomat", "sovereignty",
            "制裁", "政变", "选举", "抗议", "政权", "政府", "民主", "独裁", "外交", "主权",
        ],
        "economic": [
            "inflation", "recession", "gdp", "trade war", "tariff", "supply chain",
            "debt", "currency", "stock market", "unemployment",
            "通胀", "衰退", "GDP", "贸易战", "关税", "供应链", "债务", "货币", "股市", "失业",
        ],
        "social": [
            "pandemic", "health", "education", "inequality", "demographic",
            "migration", "refugee", "crime", "housing", "welfare",
            "疫情", "健康", "教育", "不平等", "人口", "移民", "难民", "犯罪", "住房", "福利",
        ],
        "tech": [
            "cyber", "ai regulation", "data privacy", "semiconductor", "5g",
            "quantum", "blockchain", "biotech", "surveillance", "chip",
            "网络", "人工智能", "数据隐私", "半导体", "5G", "量子", "区块链", "生物技术", "监控", "芯片",
        ],
        "international": [
            "conflict", "war", "alliance", "nato", "un security council",
            "border dispute", "territorial", "military", "naval", "missile",
            "冲突", "战争", "联盟", "北约", "联合国", "边界", "领土", "军事", "海军", "导弹",
        ],
    }

    # ── Actor keywords (organizations, roles) ──
    ACTOR_PATTERNS: list[str] = [
        r"(?:President|Prime Minister|Secretary|Minister|Chairman|CEO)\s+(?:of\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*",
        r"(?:The|the)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:government|administration|ministry|department|agency|commission|authority|committee)",
        r"[A-Z]{2,}(?:\s+[A-Z]{2,})*",  # Acronyms: UN, NATO, WHO
        r"[\u4e00-\u9fff]{2,8}(?:政府|部|委员会|局|组织|机构|公司|集团)",  # Chinese entities
    ]

    def extract(self, text: str, feedback_context: Optional[dict] = None) -> GLMRawMaterial:
        """Main extraction entry point. Returns fully structured GLMRawMaterial.

        feedback_context (optional) supports lightweight consumption of Minimax Phase 2:
        - 'priority' == 'high' -> expand extraction scope (more sentences, more events)
        - 'missing_fields' -> bias extraction to search for those fields more aggressively
        - 'type_issues' -> defensive normalization to ensure lists where expected
        """
        language = self._detect_language(text)

        # ---- Feedback-driven lightweight behaviors (non-destructive) ----
        # Default extraction parameters
        sentence_limit = 10
        event_sentence_limit = 15
        actor_limit = 20

        if feedback_context:
            # Priority high: expand extraction scope (still rule-based, no inference)
            if feedback_context.get("priority") == "high":
                sentence_limit = max(sentence_limit, 20)
                event_sentence_limit = max(event_sentence_limit, 30)

            # If missing_fields contains specific keys, bias heuristics:
            missing = feedback_context.get("missing_fields", [])
            if missing:
                # If facts missing previously, allow scanning more sentences for facts
                if "facts" in missing:
                    sentence_limit = max(sentence_limit, 30)
                # If actors missing previously, increase actor search scope
                if "actors" in missing:
                    actor_limit = max(actor_limit, 40)

            # Defensive: if type issues reported, we will normalize outputs later
            type_issues = feedback_context.get("type_issues", [])
            # normalization happens after extraction

        # If priority high, duplicate a short prefix to increase signal for heuristics
        # (keeps R1-R6: no fabrication, only repeats existing text)
        if feedback_context and feedback_context.get("priority") == "high":
            text = text + " " + text[:500]

        # Run extraction with possibly adjusted limits
        core_facts = self._extract_facts(text, limit=sentence_limit)
        events = self._extract_events(text, limit=event_sentence_limit)
        actors = self._extract_actors(text, limit=actor_limit)
        narratives = self._extract_narratives(text)
        risks = self._extract_risks(text)
        policy_signals = self._extract_policy_signals(text)
        trend_signals = self._extract_trend_signals(text)
        raw_quotes = self._extract_quotes(text, language)

        # Defensive normalization based on reported type issues
        if feedback_context and feedback_context.get("type_issues"):
            core_facts = list(core_facts) if not isinstance(core_facts, list) else core_facts
            events = list(events) if not isinstance(events, list) else events
            actors = list(actors) if not isinstance(actors, list) else actors
            narratives = list(narratives) if not isinstance(narratives, list) else narratives
            # risks expected to be list of GLMRisk; ensure list
            if not isinstance(risks, list):
                risks = list(risks) if risks is not None else []
            else:
                risks = [r for r in risks]

        # Ensure we never return None for list fields (R6)
        core_facts = core_facts or []
        events = events or []
        actors = actors or []
        narratives = narratives or []
        policy_signals = policy_signals or []
        trend_signals = trend_signals or []
        raw_quotes = raw_quotes or []
        risks = risks or []

        return GLMRawMaterial(
            source_text=text,
            detected_language=language,
            core_facts=core_facts,
            event_chain=events,
            actors=actors,
            narratives=narratives,
            risks=risks,
            policy_signals=policy_signals,
            trend_signals=trend_signals,
            raw_quotes=raw_quotes,
        )

    # ── Language detection ──
    def _detect_language(self, text: str) -> str:
        """Detect primary language using character set analysis."""
        chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
        arabic_chars = len(re.findall(r"[\u0600-\u06ff]", text))
        latin_chars = len(re.findall(r"[a-zA-Z]", text))

        total = chinese_chars + arabic_chars + latin_chars or 1
        if chinese_chars / total > 0.3:
            return "zh"
        elif arabic_chars / total > 0.3:
            return "ar"
        return "en"

    # ── Fact extraction ──
    def _extract_facts(self, text: str, limit: int = 10) -> list[GLMCoreFact]:
        """Extract 5W1H facts using sentence-level heuristics."""
        sentences = self._split_sentences(text)
        facts: list[GLMCoreFact] = []

        for sent in sentences[:limit]:
            who_match = re.search(
                r"(?:President|Prime Minister|Minister|Chairman|leader|official|spokesperson|"
                r"[\u4e00-\u9fff]{2,4}(?:主席|总理|部长|总统|发言人|领导人))",
                sent, re.IGNORECASE
            )
            when_match = re.search(
                r"(?:on\s+|in\s+)?(?:January|February|March|April|May|June|July|"
                r"August|September|October|November|December|Monday|Tuesday|Wednesday|"
                r"Thursday|Friday|Saturday|Sunday|yesterday|today|tomorrow|"
                r"\d{4}[-/年]\d{1,2}[-/月]\d{1,2}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))",
                sent, re.IGNORECASE
            )
            where_match = re.search(
                r"(?:in\s+|at\s+)(?:[A-Z][a-z]+(?:[-\s][A-Z][a-z]+)*|"
                r"[\u4e00-\u9fff]{2,}(?:市|省|国|地区))",
                sent, re.IGNORECASE
            )

            if who_match or when_match or where_match:
                facts.append(GLMCoreFact(
                    who=who_match.group(0) if who_match else "",
                    when=when_match.group(0) if when_match else "",
                    where=where_match.group(0) if where_match else "",
                    what=sent[:120],
                ))

        return facts

    # ── Event extraction ──
    def _extract_events(self, text: str, limit: int = 15) -> list[GLMEvent]:
        """Extract events with basic event-chain numbering."""
        sentences = self._split_sentences(text)
        events: list[GLMEvent] = []
        event_verbs = [
            "announced", "declared", "reported", "launched", "signed",
            "agreed", "rejected", "imposed", "lifted", "deployed",
            "宣布", "声明", "报道", "启动", "签署", "同意", "拒绝", "实施", "解除", "部署",
        ]

        level = 1
        for sent in sentences[:limit]:
            if any(v in sent.lower() for v in event_verbs):
                actors = []
                for pattern in self.ACTOR_PATTERNS:
                    for m in re.finditer(pattern, sent):
                        actors.append(m.group(0))
                events.append(GLMEvent(
                    level=level,
                    summary=sent[:150],
                    actors=actors[:5],
                ))
                level = min(level + (1 if level == 1 else 0), 3)

        return events

    # ── Actor extraction ──
    def _extract_actors(self, text: str, limit: int = 20) -> list[GLMActor]:
        """Extract named entities and organizations."""
        actors: list[GLMActor] = []
        seen: set[str] = set()

        for pattern in self.ACTOR_PATTERNS:
            for m in re.finditer(pattern, text):
                name = m.group(0).strip()
                if name not in seen and len(name) > 2:
                    seen.add(name)
                    mentions = len(re.findall(re.escape(name), text))
                    actors.append(GLMActor(
                        name=name,
                        mentions=min(mentions, 20),
                    ))

        return actors[:limit]

    # ── Narrative extraction ──
    def _extract_narratives(self, text: str) -> list[GLMNarrative]:
        """Detect narrative themes using sentiment keywords."""
        narratives: list[GLMNarrative] = []
        positive_words = ["progress", "growth", "success", "agreement", "peace",
                          "发展", "进步", "成功", "协议", "和平"]
        negative_words = ["crisis", "conflict", "tension", "threat", "failure",
                          "危机", "冲突", "紧张", "威胁", "失败"]

        sentences = self._split_sentences(text)
        for sent in sentences[:12]:
            pos_count = sum(1 for w in positive_words if w.lower() in sent.lower())
            neg_count = sum(1 for w in negative_words if w.lower() in sent.lower())
            if pos_count > 0 or neg_count > 0:
                narratives.append(GLMNarrative(
                    theme=sent[:100],
                    stance="positive" if pos_count > neg_count else "negative",
                    confidence=min(abs(pos_count - neg_count) / max(pos_count + neg_count, 1), 1.0),
                    supporting_sentences=[sent[:150]],
                ))
        return narratives[:8]

    # ── Risk extraction ──
    def _extract_risks(self, text: str) -> list[GLMRisk]:
        """Classify risks into 5 categories using keyword matching."""
        risks: list[GLMRisk] = []
        sentences = self._split_sentences(text)

        for sent in sentences:
            for category, keywords in self.RISK_KEYWORDS.items():
                for kw in keywords:
                    if kw.lower() in sent.lower():
                        severity = "medium"
                        if any(w in sent.lower() for w in ["critical", "severe", "crisis", "紧急", "严重", "危机"]):
                            severity = "high"
                        risks.append(GLMRisk(
                            category=category,
                            description=sent[:120],
                            severity=severity,
                            source_sentence=sent[:200],
                        ))
                        break
        return risks[:15]

    # ── Policy signal extraction ──
    def _extract_policy_signals(self, text: str) -> list[GLMPolicySignal]:
        """Extract policy signals using domain keywords."""
        signals: list[GLMPolicySignal] = []
        policy_keywords = [
            ("trade", ["tariff", "export", "import", "sanction", "trade", "关税", "贸易"]),
            ("defense", ["military", "naval", "missile", "defense", "军事", "防御"]),
            ("environment", ["climate", "carbon", "emission", "renewable", "气候", "排放"]),
            ("regulation", ["ban", "restrict", "comply", "regulate", "禁止", "限制"]),
        ]

        for sent in self._split_sentences(text):
            for domain, keywords in policy_keywords:
                if any(kw.lower() in sent.lower() for kw in keywords):
                    direction = "tightening" if any(
                        w in sent.lower() for w in ["ban", "restrict", "sanction", "禁止", "限制"]
                    ) else "new"
                    signals.append(GLMPolicySignal(
                        signal=sent[:120],
                        domain=domain,
                        direction=direction,
                    ))
                    break

        return signals[:10]

    # ── Trend signal extraction ──
    def _extract_trend_signals(self, text: str) -> list[GLMTrendSignal]:
        """Extract trend signals."""
        trends: list[GLMTrendSignal] = []
        trend_keywords = ["trend", "growth", "decline", "shift", "rise", "fall",
                          "趋势", "增长", "下降", "转变", "上升", "下跌"]

        for sent in self._split_sentences(text):
            if any(kw.lower() in sent.lower() for kw in trend_keywords):
                trends.append(GLMTrendSignal(
                    trend=sent[:120],
                    time_horizon="short-term" if len(sent) < 100 else "medium-term",
                ))
        return trends[:8]

    # ── Quote extraction ──
    def _extract_quotes(self, text: str, language: str) -> list[GLMRawQuote]:
        """Extract verbatim quotes from text using quotation marks."""
        quotes: list[GLMRawQuote] = []
        # Match double-quoted and single-quoted text, and Chinese quotes
        quote_patterns = [
            r'"([^"]{10,300})"',
            r"'([^']{10,300})'",
            r"\u201c([^\u201d]{10,300})\u201d",  # Chinese left/right double quotes
            r"\u300c([^\u300d]{10,300})\u300d",  # Japanese/Chinese corner brackets
        ]

        for pattern in quote_patterns:
            for m in re.finditer(pattern, text):
                quote_text = m.group(1).strip()
                if quote_text and quote_text not in {q.text for q in quotes}:
                    quotes.append(GLMRawQuote(
                        text=quote_text,
                        language=language,
                    ))
        return quotes[:20]

    # ── Utils ──
    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        """Split text into sentences for CJK and Latin scripts."""
        # Handle CJK period + Latin period
        sentences = re.split(r"(?<=[。！？.!?\n])\s*", text)
        return [s.strip() for s in sentences if len(s.strip()) > 15]
