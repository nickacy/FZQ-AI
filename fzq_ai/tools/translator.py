# fzq_ai/tools/translator.py
import os
import requests

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"  # 示例，按你实际为准

def translate_to_english(text: str) -> str:
    """
    用 DeepSeek Expert 把中文/多语言 query 翻译成英文，用于 NewsAPI / GDELT。
    """
    if not text:
        return ""

    payload = {
        "model": "deepseek-chat",  # 或你实际用的 Expert 模型名
        "messages": [
            {
                "role": "system",
                "content": "You are a professional translator. Translate the user query into concise English for news search."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        "temperature": 0.2,
    }

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    resp = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()
