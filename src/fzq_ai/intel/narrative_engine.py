# fzq_ai/intel/narrative_engine.py

from __future__ import annotations
from typing import List, Dict
from textwrap import dedent
import warnings

from fzq_ai.intel.models import Article, Narrative
from fzq_ai.llm.router import LLMRouter


class NarrativeEngine:
    """
    Phase 5.5 LLM 驱动多阵营叙事引擎：
    - Western / China / Russia / Global South
    - 共识事实 / 争议点 / 缺失视角
    """

    BLOCS = ["western", "china", "russia", "global_south"]

    def __init__(self) -> None:
        self.router = LLMRouter()

    async def generate_async(self, articles: List[Article], event_id: str) -> Narrative:
        """
        异步版本：用 LLM 生成完整 Narrative
        """

        corpus = self._build_corpus(articles)

        prompt = self._build_prompt(corpus)

        # 用 DeepSeek 优先，失败再 fallback
        text = await self._run_with_fallback(prompt)

        parsed = self._parse_llm_output(text)

        return Narrative(
            event_id=event_id,
            narratives=parsed["narratives"],
            consensus_facts=parsed["consensus"],
            contested_claims=parsed["contested"],
            missing_perspectives=parsed["missing"],
        )

    # 兼容旧同步接口（已废弃，将在 v5.0 移除）
    def generate(self, articles: List[Article], event_id: str) -> Narrative:
        """
        ⚠️ 已废弃：请直接使用 `await generate_async()` 异步版本。
        在已运行的事件循环中调用 asyncio.run() 会引发 RuntimeError。
        """
        warnings.warn(
            "generate() is deprecated. Use `await generate_async()` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        import asyncio
        return asyncio.run(self.generate_async(articles, event_id))

    # ---------------------------------------------------------
    # 构造语料
    # ---------------------------------------------------------
    def _build_corpus(self, articles: List[Article]) -> str:
        chunks = []
        for a in articles:
            chunks.append(
                f"[Source: {a.source_name} | Region: {a.region}]\n"
                f"Title: {a.title_original}\n"
                f"Content (ZH): {a.content_translated or a.content_original}\n"
            )
        return "\n\n".join(chunks)

    # ---------------------------------------------------------
    # 构造 Prompt
    # ---------------------------------------------------------
    def _build_prompt(self, corpus: str) -> str:
        return dedent(f"""
            你是一名地缘政治情报分析员，任务是从多来源新闻中提炼多阵营叙事。

            请基于以下新闻内容（已尽量翻译为中文）进行分析：

            === 新闻语料开始 ===
            {corpus}
            === 新闻语料结束 ===

            你需要输出四个阵营的叙事：
            - western：欧美主流媒体视角
            - china：中国官方 / 半官方媒体视角
            - russia：俄罗斯官方 / 媒体视角
            - global_south：全球南方国家媒体视角

            以及：
            - 共识事实（consensus_facts）：各方基本认可的事实
            - 争议点（contested_claims）：存在明显分歧的论点
            - 缺失视角（missing_perspectives）：在报道中明显缺失但重要的视角

            请用如下 JSON 结构输出（不要添加任何解释性文字）：

            {{
              "narratives": {{
                "western": "...",
                "china": "...",
                "russia": "...",
                "global_south": "..."
              }},
              "consensus_facts": [
                "fact 1",
                "fact 2"
              ],
              "contested_claims": [
                "claim 1",
                "claim 2"
              ],
              "missing_perspectives": [
                "missing 1",
                "missing 2"
              ]
            }}
            """)

    # ---------------------------------------------------------
    # LLM 调用（带 fallback）
    # ---------------------------------------------------------
    async def _run_with_fallback(self, prompt: str) -> str:
        for provider in ["deepseek", "openai", "gemini"]:
            try:
                return await self.router.run(prompt, model=provider)
            except Exception:
                continue
        # 最终兜底
        return """
        {
          "narratives": {
            "western": "LLM 调用失败，使用兜底叙事。",
            "china": "LLM 调用失败，使用兜底叙事。",
            "russia": "LLM 调用失败，使用兜底叙事。",
            "global_south": "LLM 调用失败，使用兜底叙事。"
          },
          "consensus_facts": [],
          "contested_claims": [],
          "missing_perspectives": []
        }
        """

    # ---------------------------------------------------------
    # 解析 LLM 输出
    # ---------------------------------------------------------
    def _parse_llm_output(self, text: str) -> Dict[str, object]:
        import json

        try:
            data = json.loads(text)
        except Exception:
            # 如果 LLM 没按 JSON 来，做个粗糙兜底
            return {
                "narratives": {
                    "western": text,
                    "china": "解析失败。",
                    "russia": "解析失败。",
                    "global_south": "解析失败。",
                },
                "consensus": [],
                "contested": [],
                "missing": [],
            }

        narratives = data.get("narratives", {})
        consensus = data.get("consensus_facts", [])
        contested = data.get("contested_claims", [])
        missing = data.get("missing_perspectives", [])

        # 保证四个阵营都有键
        for b in self.BLOCS:
            narratives.setdefault(b, "该阵营叙事缺失。")

        return {
            "narratives": narratives,
            "consensus": consensus,
            "contested": contested,
            "missing": missing,
        }
