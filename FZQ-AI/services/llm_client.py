# services/llm_client.py

from openai import OpenAI
from core.config import Config


class LLMClient:
    """
    多模型 LLM 客户端
    支持：
    - DeepSeek
    - Qwen
    - OpenAI GPT
    """

    def __init__(self, config: Config):
        self.config = config
        self.provider = config.llm_provider.lower()

        # -----------------------------
        # DeepSeek
        # -----------------------------
        if self.provider == "deepseek":
            # ❗ 正确的 DeepSeek API URL（不能加 /v1）
            self.client = OpenAI(
                api_key=config.api_key,
                base_url="https://api.deepseek.com"
            )

        # -----------------------------
        # Qwen（阿里 DashScope）
        # -----------------------------
        elif self.provider == "qwen":
            self.client = OpenAI(
                api_key=config.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )

        # -----------------------------
        # OpenAI GPT
        # -----------------------------
        elif self.provider == "openai":
            self.client = OpenAI(
                api_key=config.api_key
            )

        else:
            raise ValueError(f"未知的 LLM provider: {self.provider}")

    # ------------------------------------------------------------
    # 统一 ask() 接口（所有模型都走这里）
    # ------------------------------------------------------------
    def ask(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content

        except Exception as e:
            print(f"[LLM ERROR] {e}")
            return ""
