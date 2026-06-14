# fzq_ai/tools/translator.py
import requests
from fzq_ai.config import DEEPSEEK_API_KEY, DEEPSEEK_MODEL

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"


def translate_to_english(text: str) -> str:
    if not text:
        return ""

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a professional translator. Translate the user query into concise English for news search.",
            },
            {"role": "user", "content": text},
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
