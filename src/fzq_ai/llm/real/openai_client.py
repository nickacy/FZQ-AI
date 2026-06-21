"""OpenAI LLM client with async generate, health check, and retry backoff."""
import asyncio
import time
from typing import Any, Dict, Optional

from openai import AsyncOpenAI
from openai import APIError, APITimeoutError, RateLimitError

from fzq_ai.schemas.real import LLMRequest, LLMResponse, ModelProvider


class OpenAIClient:
    """Async OpenAI client with retry backoff."""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        default_model: str = "gpt-4o",
        timeout_seconds: int = 30,
        max_retries: int = 3,
        retry_backoff_base: float = 2.0,
    ):
        self.provider = ModelProvider.OPENAI
        self.default_model = default_model
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.retry_backoff_base = retry_backoff_base
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout_seconds,
        )

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response from OpenAI with retry backoff."""
        model = request.model or self.default_model
        system_msg = request.system_message or "You are a helpful assistant."
        messages: list[dict[str, str]] = []
        if request.messages:
            messages = [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in request.messages]
        else:
            messages = [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": request.prompt},
            ]

        last_exception: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            start = time.perf_counter()
            try:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,  # type: ignore[arg-type]
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    top_p=request.top_p,
                    stream=False,
                )
                latency_ms = int((time.perf_counter() - start) * 1000)
                content = response.choices[0].message.content or ""
                usage: Dict[str, int] = {}
                if response.usage:
                    usage = {
                        "prompt_tokens": response.usage.prompt_tokens or 0,
                        "completion_tokens": response.usage.completion_tokens or 0,
                        "total_tokens": response.usage.total_tokens or 0,
                    }
                return LLMResponse(
                    content=content,
                    provider=self.provider,
                    model=model,
                    usage=usage,
                    latency_ms=latency_ms,
                    finish_reason=response.choices[0].finish_reason,
                )
            except (APIError, APITimeoutError, RateLimitError) as exc:
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
        """Check if the OpenAI API is reachable."""
        try:
            await self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=1,
            )
            return True
        except Exception:
            return False
