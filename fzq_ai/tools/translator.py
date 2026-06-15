# fzq_ai/tools/translator.py
"""翻译工具：中英文互译 + 语言检测"""

import requests
from fzq_ai.config import DEEPSEEK_API_KEY, DEEPSEEK_MODEL

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"


def translate_to_english(text: str) -> str:
    """将任意语言文本翻译为英文"""
    if not text:
        return ""
    if _is_mostly_english(text):
        return text  # 已经是英文，无需翻译

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a professional translator. "
                    "Translate the following text into concise English. "
                    "Output ONLY the translation, no explanations."
                ),
            },
            {"role": "user", "content": text},
        ],
        "temperature": 0.2,
    }
    return _call_deepseek(payload)


def translate_to_chinese(text: str) -> str:
    """将任意语言文本翻译为中文"""
    if not text:
        return ""
    if _is_mostly_chinese(text):
        return text  # 已经是中文，无需翻译

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是一名专业翻译。将以下文本翻译为简洁的中文。"
                    "只输出译文，不要加任何解释。"
                ),
            },
            {"role": "user", "content": text},
        ],
        "temperature": 0.2,
    }
    return _call_deepseek(payload)


def is_english_or_chinese(text: str) -> bool:
    """检测文本是否已经是英文或中文（不需要额外翻译）"""
    return _is_mostly_english(text) or _is_mostly_chinese(text)


def _is_mostly_english(text: str) -> bool:
    """简单启发式：英文字符占比 > 70%"""
    if not text:
        return False
    alpha_count = sum(1 for c in text if c.isascii() and c.isalpha())
    total = max(len(text), 1)
    return alpha_count / total > 0.5


def _is_mostly_chinese(text: str) -> bool:
    """简单启发式：中文字符占比 > 30%"""
    if not text:
        return False
    cjk_count = sum(
        1 for c in text if '\u4e00' <= c <= '\u9fff'
        or '\u3400' <= c <= '\u4dbf'
    )
    total = max(len(text), 1)
    return cjk_count / total > 0.3


def _call_deepseek(payload: dict) -> str:
    """调用 DeepSeek API，返回翻译结果"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(
            DEEPSEEK_API_URL, json=payload, headers=headers, timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return "[翻译失败]"
