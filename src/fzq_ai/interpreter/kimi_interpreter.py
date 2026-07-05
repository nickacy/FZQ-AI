"""KimiInterpreter — Explanation Layer for FZQ-AI.

Pipeline: GLM → DeepSeek → Minimax → Doubao → Kimi(Explain) → Qwen

Kimi's ONLY mission: interpret structured data into human-readable text
without altering facts, structure, or inventing content.

Rules (R1-R6):
  R1: No inference — explain only what's explicitly present
  R2: No supplementation — never fill missing fields
  R3: No invention — never fabricate events or facts
  R4: No structural change — input fields must pass through unchanged
  R5: Natural language output — produce readable Chinese/English text
  R6: Output must be valid JSON (Pydantic model)
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from fzq_ai.interpreter.models import ExplanationResult


class KimiInterpreter:
    """Interpret structured FZQ-AI output into human-readable explanations."""

    # ── Risk severity labels ──
    _SEVERITY_ZH: dict[str, str] = {
        "low": "低", "medium": "中", "high": "高", "critical": "严重",
    }
    _RISK_CATEGORY_ZH: dict[str, str] = {
        "political": "政治", "economic": "经济", "social": "社会",
        "tech": "技术", "international": "国际",
    }

    def interpret(self, strict_schema: dict, feedback_context: Optional[dict] = None) -> ExplanationResult:
        """Main entry point — generate all 6 explanation fields.

        feedback_context (optional) supports lightweight consumption of Minimax Phase 2:
        - 'requires_action' (bool): when true, emphasize action in top-level briefs.
        - 'consistency_score' (int 0-100): when low, add explicit structure warning.
        - 'suggestions' (list[str]): structural suggestions from Minimax; included as a short '结构建议摘要' section.
        """
        # Feedback-driven flags (non-destructive, only affect wording)
        action_prefix = ""
        structure_warning = ""
        structure_suggestions_text = ""

        if feedback_context:
            if feedback_context.get("requires_action"):
                action_prefix = "[ACTION REQUIRED] "

            consistency = feedback_context.get("consistency_score")
            if isinstance(consistency, (int, float)) and consistency < 80:
                structure_warning = (
                    f"\n\n[结构一致性提醒] 当前结构一致性评分较低（{consistency}），"
                    "请注意以下可能不稳定或缺失的字段。"
                )

            suggestions = feedback_context.get("suggestions", [])
            if suggestions:
                # Build a concise structure suggestions summary (no fabrication)
                lines = []
                for s in suggestions[:6]:
                    # ensure each suggestion is short and safe to include
                    lines.append(f"  · {str(s)[:200]}")
                structure_suggestions_text = "\n\n[结构建议摘要]\n" + "\n".join(lines)

        # Build explanation parts
        policy_brief = action_prefix + self._policy_brief(strict_schema)
        risk_summary = action_prefix + self._risk_summary(strict_schema)
        narrative_analysis = self._narrative_analysis(strict_schema)
        trend_insights = self._trend_insights(strict_schema)
        quotes_analysis = self._quotes_analysis(strict_schema)

        # Append structure-aware notes to one or more explanation fields.
        # We choose to append to narrative_analysis and risk_summary to surface structure issues
        # without changing the ExplanationResult schema.
        if structure_warning:
            # Put the warning into risk_summary (structure risk is relevant to risk section)
            risk_summary = risk_summary + structure_warning

        if structure_suggestions_text:
            # Add suggestions to narrative_analysis as a separate small section
            narrative_analysis = narrative_analysis + structure_suggestions_text

        return ExplanationResult(
            policy_brief=policy_brief,
            risk_summary=risk_summary,
            narrative_analysis=narrative_analysis,
            trend_insights=trend_insights,
            quotes_analysis=quotes_analysis,
            structured_explanation=strict_schema,
        )

    # ── Policy Brief ──────────────────────────────────────
    def _policy_brief(self, s: dict) -> str:
        """Generate policy summary from facts, policy signals, and actors."""
        facts = s.get("facts", [])
        policy = s.get("policy", [])
        actors = s.get("actors", [])

        parts: list[str] = []
        if facts:
            fact_count = len(facts)
            parts.append(f"根据已提取的 {fact_count} 条核心事实")

        actor_names = [a.get("name", a) if isinstance(a, dict) else str(a) for a in actors[:5]]
        if actor_names:
            parts.append(f"涉及行为体：{'、'.join(actor_names)}")

        if policy:
            parts.append(f"检测到 {len(policy)} 条政策信号")
            for p in policy[:3]:
                text = p.get("signal", str(p)) if isinstance(p, dict) else str(p)
                parts.append(f"  · {text[:100]}")

        return "。".join(parts) + "。" if parts else "未检测到足够的政策相关信息。"

    # ── Risk Summary ──────────────────────────────────────
    def _risk_summary(self, s: dict) -> str:
        """Generate risk assessment from the 5-category risk data."""
        risks = s.get("risks", {})
        if isinstance(risks, dict) and any(risks.values()):
            parts = ["风险分级总结："]
            total = 0
            for cat, items in risks.items():
                cat_zh = self._RISK_CATEGORY_ZH.get(cat, cat)
                count = len(items) if isinstance(items, list) else 0
                if count > 0:
                    parts.append(f"  {cat_zh}风险：{count} 项")
                    total += count
            if total > 0:
                parts.insert(1, f"共发现 {total} 项风险信号。")
                return "\n".join(parts)
        return "未检测到明确的风险信号。"

    # ── Narrative Analysis ────────────────────────────────
    def _narrative_analysis(self, s: dict) -> str:
        """Analyze narrative conflicts from narratives and events."""
        narratives = s.get("narratives", [])
        events = s.get("events", [])

        parts: list[str] = []
        if narratives:
            themes = []
            for n in narratives[:5]:
                if isinstance(n, dict):
                    theme = n.get("theme", "")
                    stance = n.get("stance", "")
                    themes.append(f"{theme}（{stance}）" if stance else theme)
                else:
                    themes.append(str(n)[:80])
            parts.append(f"识别到 {len(narratives)} 条叙事主线：{'；'.join(themes)}")

        if events:
            ev_count = len(events)
            levels = set(e.get("level", 1) if isinstance(e, dict) else 1 for e in events)
            parts.append(f"提取 {ev_count} 个事件，层级 {min(levels)}-{max(levels)}")

        return "。".join(parts) + "。" if parts else "未检测到明确叙事结构。"

    # ── Trend Insights ────────────────────────────────────
    def _trend_insights(self, s: dict) -> str:
        """Generate trend insights from trend signals and events."""
        trends = s.get("trend", [])
        parts: list[str] = []

        if trends:
            parts.append(f"检测到 {len(trends)} 条趋势信号：")
            for t in trends[:5]:
                text = t.get("trend", str(t)) if isinstance(t, dict) else str(t)
                horizon = t.get("time_horizon", "") if isinstance(t, dict) else ""
                label = f"（{horizon}）" if horizon else ""
                parts.append(f"  · {text[:100]}{label}")

        events = s.get("events", [])
        if len(events) >= 3:
            parts.append(f"事件链包含 {len(events)} 个节点，建议关注后续发展。")

        return "\n".join(parts) if parts else "未检测到明确趋势信号。"

    # ── Quotes Analysis ───────────────────────────────────
    def _quotes_analysis(self, s: dict) -> str:
        """Generate quote attribution analysis."""
        quotes = s.get("raw_quotes", [])
        if not quotes:
            return "未检测到原始引用。"

        parts = [f"共提取 {len(quotes)} 条原始引用："]
        for i, q in enumerate(quotes[:8], 1):
            text = q.get("text", str(q)) if isinstance(q, dict) else str(q)
            speaker = q.get("speaker", "") if isinstance(q, dict) else ""
            attribution = f" — {speaker}" if speaker else ""
            parts.append(f"  {i}. \"{text[:120]}\"{attribution}")

        return "\n".join(parts)
