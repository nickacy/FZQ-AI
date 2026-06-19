"""Gemini LLM client with async generate, health check, and retry backoff."""
import asyncio
import time
from typing import Optional

import aiohttp

from fzq_ai.schemas.real import LLMRequest, LLMResponse, ModelProvider


class GeminiClient:
    """Async Gemini client using aiohttp with retry backoff."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
        default_model: str = "gemini-1.5-flash",
        timeout_seconds: int = 30,
        max_retries: int = 3,
        retry_backoff_base: float = 2.0,
    ):
        self.provider = ModelProvider.GEMINI
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.retry_backoff_base = retry_backoff_base

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response from Gemini with retry backoff."""
        model = request.model or self.default_model
        system_msg = request.system_message or "You are a helpful assistant."
        prompt_text = request.prompt
        if request.messages:
            parts = []
            for m in request.messages:
                role = m.get("role", "user")
                content = m.get("content", "")
                parts.append(f"{role}: {content}")
            prompt_text = "\n".join(parts)

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{system_msg}\n\n{prompt_text}"}],
                }
            ],
            "generationConfig": {
                "temperature": request.temperature,
                "maxOutputTokens": request.max_tokens,
                "topP": request.top_p,
            },
        }
        url = (
            f"{self.base_url}/models/{model}:generateContent"
            f"?key={self.api_key}"
        )
        headers = {"Content-Type": "application/json"}

        last_exception: Optional[Exception] = None
        start = time.perf_counter()
        for attempt in range(self.max_retries + 1):
            try:
                timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(
                        url,
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
                        candidates = data.get("candidates", [])
                        if not candidates:
                            raise ValueError("No candidates in Gemini response")
                        content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        usage = data.get("usageMetadata", {})
                        return LLMResponse(
                            content=content,
                            provider=self.provider,
                            model=model,
                            usage={
                                "prompt_tokens": usage.get("promptTokenCount", 0),
                                "completion_tokens": usage.get("candidatesTokenCount", 0),
                                "total_tokens": usage.get("totalTokenCount", 0),
                            },
                            latency_ms=latency_ms,
                            finish_reason=candidates[0].get("finishReason"),
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
        """Check if the Gemini API is reachable."""
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
            url = (
                f"{self.base_url}/models/{self.default_model}:generateContent"
                f"?key={self.api_key}"
            )
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [
                            {
                                "role": "user",
                                "parts": [{"text": "hi"}],
                            }
                        ],
                        "generationConfig": {"maxOutputTokens": 1},
                    },
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False
