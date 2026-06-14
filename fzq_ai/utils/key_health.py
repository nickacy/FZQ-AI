import os
import requests
import google.genai as genai
from openai import OpenAI


class KeyHealth:
    @staticmethod
    def check_deepseek():
        key = os.getenv("DEEPSEEK_API_KEY")
        if not key:
            return False, "DEEPSEEK_API_KEY 缺失"

        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}"}
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": "ping"}],
            "stream": False,
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            if resp.status_code == 200:
                return True, "DeepSeek Key 正常"
            else:
                return False, f"DeepSeek Key 无效：{resp.text}"
        except Exception as e:
            return False, f"DeepSeek 检查失败：{e}"

    @staticmethod
    def check_openai():
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            return False, "OPENAI_API_KEY 缺失"

        try:
            client = OpenAI(api_key=key)
            client.chat.completions.create(
                model="gpt-4o-mini", messages=[{"role": "user", "content": "ping"}]
            )
            return True, "OpenAI Key 正常"
        except Exception as e:
            return False, f"OpenAI Key 无效：{e}"

    @staticmethod
    def check_gemini():
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            return False, "GEMINI_API_KEY 缺失"

        try:
            client = genai.Client(api_key=key)
            client.models.generate_content(model="gemini-1.5-flash", contents="ping")
            return True, "Gemini Key 正常"
        except Exception as e:
            return False, f"Gemini Key 无效：{e}"
