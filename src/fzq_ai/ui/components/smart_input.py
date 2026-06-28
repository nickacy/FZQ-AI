"""
V15 Smart Input Component.

Features:
  - Language auto-detection (zh/en)
  - Character counter
  - Placeholder in current language
  - Wraps st.text_area with consistent styling
"""

from __future__ import annotations
import re
import streamlit as st
from fzq_ai.ui.i18n import t


class SmartInput:
    """Intelligent text input with language detection and char counter."""

    def __init__(self, lang: str = "zh"):
        self.lang = lang
        self.text: str = ""
        self.detected_lang: str = lang

    def detect_language(self, text: str) -> str:
        """Heuristic language detection: count CJK chars vs ASCII alphabetic."""
        if not text:
            return self.lang
        cjk = len(re.findall(r'[\u4e00-\u9fff]', text))
        ascii_alpha = len(re.findall(r'[a-zA-Z]', text))
        return "zh" if cjk > ascii_alpha else "en"

    def render(self, key: str = "smart_input", height: int = 200) -> str:
        """Render the input area and return the text."""
        placeholder = t("app.input_placeholder", self.lang)

        self.text = st.text_area(
            label=t("app.input_label", self.lang),
            value=self.text,
            placeholder=placeholder,
            height=height,
            key=key,
        )

        if self.text:
            self.detected_lang = self.detect_language(self.text)

        # Character counter
        char_count = len(self.text)
        st.caption(
            f"{t('app.char_count', self.lang)}: {char_count}  "
            f"|  {t('app.detected_lang', self.lang)}: "
            f"{'Chinese' if self.detected_lang == 'zh' else 'English'}"
        )

        return self.text


def render_smart_input(lang: str = "zh", key: str = "smart_input",
                       height: int = 200) -> str:
    """Convenience function for inline use."""
    si = SmartInput(lang)
    return si.render(key=key, height=height)
