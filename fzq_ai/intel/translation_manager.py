from __future__ import annotations
from typing import Optional, Dict
import asyncio
import langdetect

from fzq_ai.llm.llm_router import LLMRouter

class TranslationManager:
    def __init__(self):
        self.router = LLMRouter()
        self.cache: Dict[str, str] = {}

    def detect_language(self, text: str) -> str:
        try:
            return langdetect.detect(text)
        except Exception:
            return "unknown"

    async def translate(self, text: str, target_lang: str = "zh") -> str:
        if not text:
            return ""

        if cache_key in self.cache:
            return self.cache[cache_key]

            f"请将以下内容翻译成{ '中文' if target_lang=='zh' else '英文' }：\n\n"
            "要求：忠实、准确、保持原意，不要添加解释。"

        for provider in ["deepseek", "openai", "gemini"]:
            try:
                result = await self.router.run(prompt, model=provider)
                self.cache[cache_key] = result
                return result
            except Exception:

        return text

    async def translate_snippet_en(self, text: str, max_chars: int = 300) -> str:
        snippet = text[:max_chars]
        return await self.translate(snippet, target_lang="en")

    async def process_article(self, article) -> None:
        original = article.content_original or ""
        if not original:
            return

        detected = self.detect_language(original)
        article.language = detected

        if detected != "zh":
            article.content_translated = await self.translate(original, "zh")
        else:

        if detected not in ["zh", "en"]:
            article.content_snippet_en = await self.translate_snippet_en(original)
        else:
