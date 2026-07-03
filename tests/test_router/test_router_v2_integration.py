"""V24 — RouterV2 (task-aware) integration tests.

Verifies the v2 router:
  - select() returns a provider from the candidate pool based on task/length/structure
  - get_provider() returns a real ModelClient for the given provider name
  - Unknown provider name raises a clear ValueError
"""
from __future__ import annotations
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import pytest

from fzq_ai.llm.router_v2.router import RouterV2
from fzq_ai.clients.model_client import ModelClient


class TestRouterV2Select:
    def test_select_returns_top_provider_string(self):
        """select() returns the top-ranked provider as a string (not a list)."""
        r = RouterV2()
        provider = r.select({"task_type": "zh_multisource_merge", "input": "x"})
        assert isinstance(provider, str)
        # Must be one of the providers in the pool
        assert provider in ("glm-5.2", "qwen", "deepseek")

    def test_select_falls_back_to_length_rule(self):
        """Long input with unknown task → length rule picks from kimi/glm/deepseek."""
        r = RouterV2()
        provider = r.select({"task_type": "unknown", "input": "x" * 10000})
        assert isinstance(provider, str)
        assert provider in ("kimi", "glm-5.2", "deepseek", "qwen")

    def test_select_uses_default_when_no_match(self):
        """No task + short input → default pool + metrics ranking."""
        r = RouterV2()
        provider = r.select({"task_type": None, "input": ""})
        assert isinstance(provider, str)
        # Default pool is ["glm-5.2", "deepseek", "qwen"]
        assert provider in ("glm-5.2", "deepseek", "qwen")


class TestRouterV2GetProvider:
    def test_get_provider_returns_model_client(self):
        r = RouterV2()
        c = r.get_provider("deepseek")
        assert isinstance(c, ModelClient)
        assert c.provider == "deepseek"
        assert c.model == "deepseek-chat"

    def test_get_provider_openai(self):
        r = RouterV2()
        c = r.get_provider("openai")
        assert c.provider == "openai"

    def test_get_provider_qwen(self):
        r = RouterV2()
        c = r.get_provider("qwen")
        assert c.provider == "qwen"

    def test_get_provider_unknown_raises(self):
        r = RouterV2()
        with pytest.raises(ValueError, match="Unknown provider"):
            r.get_provider("not_a_real_provider")
