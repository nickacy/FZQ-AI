"""
Unified ModelClient for V20 multi-model routing.
Delegates actual work to provider.run()
"""

from __future__ import annotations
from typing import Any, Dict


class ModelClient:
    """
    V20 ModelClient — unified interface for all providers.
    Providers must implement async run(req: Dict[str, Any]).
    """

    def __init__(self, provider):
        """
        provider: instance of DeepSeekProvider / GLMProvider / QwenProvider / etc.
        """
        self.provider = provider

    async def chat(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """
        Unified chat interface — delegates to provider.run().
        """
        return await self.provider.run(req)
