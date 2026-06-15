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

            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": "ping"}],
            "stream": False,

        try:
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
            return True, "OpenAI Key 正常"
        except Exception as e:
            return False, f"OpenAI Key 无效：{e}"

    @staticmethod
    def check_gemini():
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            return False, "GEMINI_API_KEY 缺失"

        try:
            return True, "Gemini Key 正常"
        except Exception as e:
            return False, f"Gemini Key 无效：{e}"
