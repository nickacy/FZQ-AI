# src/fzq_ai/llm/router.py
# V24-Final — Intelligent LLM Router with Model Selection
"""
Unified LLM routing strategy for FZQ-AI.

Selects model by: task_type, language, input length, priority.
Integrated with: tracing, monitoring, structlog, intent_engine.
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional, Literal

from fzq_ai.utils.monitoring import llm_monitor
from fzq_ai.utils.logger import log_event
from fzq_ai.llm.failover import get_failover_chain, format_failover_path

logger = logging.getLogger(__name__)

# ── Model pools ──────────────────────────────────────────────

# Cost tier (cents per 1M tokens, approximate)
MODEL_COST: Dict[str, float] = {
    "deepseek-chat": 0.14,
    "deepseek-reasoner": 0.55,
    "glm-4-flash": 0.10,
    "qwen-max": 0.40,
    "gpt-4o": 5.00,
    "gpt-4o-mini": 0.15,
    "gemini-2.0-flash": 0.10,
}

# Context window sizes
MODEL_CONTEXT: Dict[str, int] = {
    "deepseek-chat": 65536,
    "deepseek-reasoner": 65536,
    "glm-4-flash": 128000,
    "qwen-max": 32768,
    "gpt-4o": 128000,
    "gpt-4o-mini": 128000,
    "gemini-2.0-flash": 1048576,
}

# ── Routing table ─────────────────────────────────────────────

# (task_type, lang) → [model_priority_list]
_ROUTING: Dict[str, Dict[str, List[str]]] = {
    "zh_risk_scan":        {"zh": ["deepseek-chat", "glm-4-flash", "qwen-max"],
                             "en": ["deepseek-chat", "gpt-4o-mini"]},
    "zh_policy_brief":     {"zh": ["deepseek-chat", "deepseek-reasoner", "glm-4-flash"],
                             "en": ["gpt-4o", "deepseek-chat"]},
    "zh_multisource_merge":{"zh": ["deepseek-chat", "qwen-max"],
                             "en": ["deepseek-chat", "gpt-4o-mini"]},
    "zh_opinion_landscape":{"zh": ["glm-4-flash", "deepseek-chat"],
                             "en": ["gpt-4o-mini", "deepseek-chat"]},
    "news":                {"zh": ["deepseek-chat", "qwen-max"],
                             "en": ["gpt-4o-mini", "deepseek-chat"]},
    "narrative":           {"zh": ["deepseek-reasoner", "deepseek-chat"],
                             "en": ["deepseek-chat", "gpt-4o"]},
    "risk":                {"zh": ["deepseek-chat", "glm-4-flash"],
                             "en": ["gpt-4o", "deepseek-chat"]},
    "daily_report":        {"zh": ["deepseek-chat", "qwen-max"],
                             "en": ["gpt-4o-mini", "deepseek-chat"]},
    "code_review":         {"zh": ["deepseek-chat", "gpt-4o"],
                             "en": ["gpt-4o", "deepseek-chat"]},
    "agent_planning":      {"zh": ["deepseek-reasoner", "deepseek-chat"],
                             "en": ["deepseek-chat", "gpt-4o"]},
    "default":             {"zh": ["deepseek-chat", "glm-4-flash", "qwen-max"],
                             "en": ["gpt-4o-mini", "deepseek-chat"]},
}


# ── Model selection ──────────────────────────────────────────

def choose_model(
    task_type: str = "default",
    lang: str = "zh",
    length: int = 0,
    priority: Literal["quality", "cost", "balanced"] = "quality",
    fallback_models: Optional[List[str]] = None,
) -> str:
    """
    Select the best model for the given task.

    Args:
        task_type: e.g. zh_risk_scan, news, code_review
        lang: zh or en
        length: input text length in characters
        priority: quality | cost | balanced
        fallback_models: override candidate list (optional)

    Returns:
        model name string, e.g. deepseek-chat
    """
    # 1. Get candidates from routing table
    candidates = fallback_models or []
    if not candidates:
        entry = _ROUTING.get(task_type, _ROUTING["default"])
        lang_list = entry.get(lang, entry.get("zh", []))
        candidates = list(lang_list)

    if not candidates:
        candidates = ["deepseek-chat", "glm-4-flash", "qwen-max"]

    # 2. Filter by context window
    viable: List[str] = []
    for m in candidates:
        ctx = MODEL_CONTEXT.get(m, 32768)
        if length < ctx:
            viable.append(m)
    if not viable:
        viable = candidates  # fallback: ignore context limit

    # 3. Sort by priority
    if priority == "cost":
        viable.sort(key=lambda m: MODEL_COST.get(m, 1.0))
    elif priority == "quality":
        # Prefer larger context + higher cost (proxy for quality)
        viable.sort(key=lambda m: -(MODEL_CONTEXT.get(m, 0) + int(MODEL_COST.get(m, 0) * 10)))
    # balanced: keep order from routing table

    return viable[0]


# ── Unified LLM call ─────────────────────────────────────────

async def call_llm(
    model: str,
    prompt: str,
    *,
    trace_id: str = "",
    task_type: str = "default",
    max_tokens: int = 4096,
    temperature: float = 0.0,
    **kwargs: Any,
) -> str:
    """
    Unified LLM call through intelligent routing.

    Args:
        model: model name from choose_model()
        prompt: user prompt text
        trace_id: for tracing
        task_type: for logging
        max_tokens: output limit
        temperature: sampling temperature

    Returns:
        completion text string
    """
    from fzq_ai.utils.tracing import Tracer

    log_event("llm_call.start",
        model=model, trace_id=trace_id, task_type=task_type,
        prompt_len=len(prompt), max_tokens=max_tokens)

    with llm_monitor(model):
        try:
            # Route to the appropriate provider client
            completion, used_model, tried = await _dispatch_with_failover(model, prompt, max_tokens, temperature, **kwargs)
            log_event("llm_call.done", used_model=used_model, failover_path=format_failover_path(model, tried, used_model),
                model=model, trace_id=trace_id, completion_len=len(completion))
            return completion
        except Exception as e:
            log_event("llm_call.error",
                model=model, trace_id=trace_id, error=str(e))
            raise


# ── Provider dispatch ────────────────────────────────────────

async def _dispatch_with_failover(
    model: str, prompt: str, max_tokens: int, temperature: float, **kwargs: Any
) -> tuple:
    """Try model + failover chain. Returns (completion, used_model, tried_models)."""
    chain = [model] + get_failover_chain(model)
    tried = []
    last_error = None
    for m in chain:
        tried.append(m)
        try:
            result = await _call_one_model(m, prompt, max_tokens, temperature, **kwargs)
            return result, m, tried
        except Exception as e:
            last_error = e
            logger.warning("Failover: %s failed -> trying next. Error: %s", m, e)
            continue
    raise RuntimeError("All %d models failed. Last: %s" % (len(tried), last_error))


async def _call_one_model(
    model: str, prompt: str, max_tokens: int, temperature: float, **kwargs: Any
) -> str:
    """Try a single model via its provider."""
    import asyncio
    providers = _resolve_provider(model)
    for provider_func, provider_model in providers:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: provider_func(provider_model, prompt, max_tokens, temperature, **kwargs)
        )
    raise RuntimeError("No provider found for model=%s" % model)


def _resolve_provider(model: str) -> list:
    """Map model name → [(func, model_name), ...]."""
    if model.startswith("deepseek"):
        from fzq_ai.llm.providers.deepseek_provider import DeepSeekProvider
        return [(DeepSeekProvider(model=model).run_sync, model)]
    elif model.startswith("glm"):
        from fzq_ai.llm.providers.glm_provider import GLMProvider
        return [(GLMProvider(model=model).run_sync, model)]
    elif model.startswith("qwen"):
        from fzq_ai.llm.providers.qwen_provider import QwenProvider
        return [(QwenProvider(model=model).run_sync, model)]
    elif model.startswith("gpt") or model.startswith("o") or model.startswith("openai"):
        from fzq_ai.llm.providers.openai_provider import OpenAIProvider
        return [(OpenAIProvider(model=model).run_sync, model)]
    elif model.startswith("gemini"):
        from fzq_ai.llm.providers.gemini_provider import GeminiProvider
        return [(GeminiProvider(model=model).run_sync, model)]
    else:
        # Default: try deepseek first, then glm
        from fzq_ai.llm.providers.deepseek_provider import DeepSeekProvider
        from fzq_ai.llm.providers.glm_provider import GLMProvider
        return [
            (DeepSeekProvider(model="deepseek-chat").run_sync, "deepseek-chat"),
            (GLMProvider(model="glm-4-flash").run_sync, "glm-4-flash"),
        ]


# ── Sync helper for intent_engine ────────────────────────────

def get_router_hint(task_type: str, text: str, lang: str = "zh", priority: str = "quality") -> Dict[str, Any]:
    """Build router hint dict for intent_engine → pipeline chain."""
    return {
        "task_type": task_type,
        "lang": lang,
        "length": len(text),
        "priority": priority,
        "suggested_model": choose_model(task_type, lang, len(text), priority),  # type: ignore[arg-type]
    }


class Router:
    def __init__(self):
        pass
    async def run(self, req: dict):
        text = req.get('prompt', '')
        task = req.get('task_type', 'news')
        lang = req.get('language', 'zh')
        model = choose_model(task_type=task, lang=lang, length=len(text))
        result = await call_llm(model, prompt=text)
        return {'output': result}


# ── Backward-compatible LLMRouter (merged from llm_router.py) ──
class LLMRouter:
    """
    v13 Compatibility layer:
    - Retains legacy interface: route(task_name, prompt)
    - Underlying calls v13 Router.run(req)
    """

    def __init__(self):
        self.router = Router()

    async def route(self, task_type: str, prompt: str) -> str:
        req = {
            "task_type": task_type,
            "prompt": prompt,
        }
        result = await self.router.run(req)
        return result.get("output", "")

    async def call(
        self,
        provider: str,
        prompt: str,
        model: str,
        api_key: str,
        base_url: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: int = 60,
    ) -> str:
        """
        v13 unified call() interface used by LLMExecutor.
        Routes to the appropriate provider and returns text output.
        """
        req = {
            "task_type": "chat",
            "prompt": prompt,
            "model": model,
            "api_key": api_key,
            "base_url": base_url,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timeout": timeout,
            "provider": provider,
        }
        result = await self.router.run(req)
        if "error" in result:
            raise RuntimeError(f"LLM call failed: {result['error']}")
        return result.get("output", "")
