"""DeepSeek LLM client with async generate, health check, and retry backoff."""
import asyncio
import json
import time
from typing import Optional

import aiohttp

from fzq_ai.schemas.real import LLMRequest, LLMResponse, ModelProvider


class DeepSeekClient:
    """Async DeepSeek client using aiohttp with retry backoff."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.deepseek.com",
        default_model: str = "deepseek-chat",
        timeout_seconds: int = 30,
        max_retries: int = 3,
        retry_backoff_base: float = 2.0,
    ):
        self.provider = ModelProvider.DEEPSEEK
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.retry_backoff_base = retry_backoff_base

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response from DeepSeek with retry backoff."""
        model = request.model or self.default_model
        system_msg = request.system_message or "You are a helpful assistant."
        messages = []
        if request.messages:
            messages = [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in request.messages]
        else:
            messages = [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": request.prompt},
            ]

        payload = {
            "model": model,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "top_p": request.top_p,
            "stream": False,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        last_exception: Optional[Exception] = None
        start = time.perf_counter()
        for attempt in range(self.max_retries + 1):
            try:
                timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json={k: v for k, v in payload.items() if v is not None},
                    ) as resp:
                        data = await resp.json()
                        latency_ms = int((time.perf_counter() - start) * 1000)
                        if resp.status != 200:
                            error_msg = data.get("error", {}).get("message", f"HTTP {resp.status}")
                            raise aiohttp.ClientResponseError(
                                request_info=resp.request_info,
                                history=resp.history,
                                status=resp.status,
                                message=error_msg,
                            )
                        choice = data["choices"][0]
                        content = choice.get("message", {}).get("content", "")
                        usage = data.get("usage", {})
                        return LLMResponse(
                            content=content,
                            provider=self.provider,
                            model=model,
                            usage={
                                "prompt_tokens": usage.get("prompt_tokens", 0),
                                "completion_tokens": usage.get("completion_tokens", 0),
                                "total_tokens": usage.get("total_tokens", 0),
                            },
                            latency_ms=latency_ms,
                            finish_reason=choice.get("finish_reason"),
                        )
            except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                last_exception = exc
                if attempt < self.max_retries:
                    backoff = self.retry_backoff_base ** attempt
                    await asyncio.sleep(backoff)
                continue
            except Exception as exc:
                last_exception = exc
                break

        latency_ms = int((time.perf_counter() - start) * 1000)
        return LLMResponse(
            content="",
            provider=self.provider,
            model=model,
            usage={},
            latency_ms=latency_ms,
            error=str(last_exception),
        )

    async def health_check(self) -> bool:
        """Check if the DeepSeek API is reachable."""
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.default_model,
                        "messages": [{"role": "user", "content": "hi"}],
                        "max_tokens": 1,
                    },
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False
