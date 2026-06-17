# fzq_ai/tools/translator.py

import re
from typing import Optional


# ---------------------------------------------------------
# Unicode 范围
# ---------------------------------------------------------

# 英文：A–Z, a–z
ENGLISH_RE = re.compile(r"[A-Za-z]")

# 中文：CJK Unified Ideographs
CHINESE_RE = re.compile(r"[\u4e00-\u9fff]")

# 日文：平假名 + 片假名 + 日文汉字
JAPANESE_RE = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff]")

# 韩文：Hangul
KOREAN_RE = re.compile(r"[\uac00-\ud7af]")

# 阿拉伯文
ARABIC_RE = re.compile(r"[\u0600-\u06ff]")

# 西里尔文（俄文）
CYRILLIC_RE = re.compile(r"[\u0400-\u04ff]")


# ---------------------------------------------------------
# 增强版语言检测（不改变旧逻辑，只增强准确性）
# ---------------------------------------------------------

def is_english_or_chinese(text: str) -> bool:
    """
    判断文本是否主要由英文或中文组成。
    - 保留旧逻辑：只判断“是否英/中文”
    - 增强准确性：排除日文/韩文/俄文/阿拉伯文等
    """

    if not text:
        return True  # 空文本视为可处理

    # 如果包含日文/韩文/阿拉伯文/俄文 → 直接判定为非英中
    if JAPANESE_RE.search(text):
        return False
    if KOREAN_RE.search(text):
        return False
    if ARABIC_RE.search(text):
        return False
    if CYRILLIC_RE.search(text):
        return False

    # 如果包含中文 → 是中文
    if CHINESE_RE.search(text):
        return True

    # 如果包含英文 → 是英文
    if ENGLISH_RE.search(text):
        return True

    # 其他语言 → 非英中
    return False


# ---------------------------------------------------------
# 翻译函数（保持旧逻辑）
# ---------------------------------------------------------

def translate_to_english(text: str) -> str:
    return f"[EN translation of]: {text}"


def translate_to_chinese(text: str) -> str:
    return f"[CN translation of]: {text}"
