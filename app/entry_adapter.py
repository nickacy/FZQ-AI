# -*- coding: utf-8 -*-
"""
FZQ-AI Entry Service (V23-Final)
Unified Entry Layer → UnifiedOrchestrator(V23) → RouteResult
Author: Nick
Version: V23.3.0
"""

from __future__ import annotations
from typing import Any, Dict, Optional

from fzq_ai.orchestrator.unified_orchestrator import UnifiedOrchestrator
from fzq_ai.schemas.route import RouteResult


class EntryServiceV23:
    """
    V23 Entry Layer
    - Unified input structure
    - Unified error structure
    - Unified RouteResult output
    - No routing logic (delegated to UnifiedOrchestrator)
    """

    def __init__(self) -> None:
        self.orch = UnifiedOrchestrator()

    # ------------------------------------------------------------
    # Unified V23 Entry
    # ------------------------------------------------------------
    async def handle(
        self,
        task: str,
        ctx: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> RouteResult:
        """
        Unified entry point for all tasks.
        Input:
            task: str
            ctx: dict (optional)
            options: dict (optional)

        Output:
            RouteResult
        """

        # ------------------------------
        # Validate input structure
        # ------------------------------
        if not isinstance(task, str):
            return RouteResult.error(
                code="TASK_TYPE_ERROR",
                message="task must be a string",
                debug_info={"task_type": type(task).__name__},
            )

        if ctx is not None and not isinstance(ctx, dict):
            return RouteResult.error(
                code="CTX_TYPE_ERROR",
                message="ctx must be a dict",
                debug_info={"ctx_type": type(ctx).__name__},
            )

        if options is not None and not isinstance(options, dict):
            return RouteResult.error(
                code="OPTIONS_TYPE_ERROR",
                message="options must be a dict",
                debug_info={"options_type": type(options).__name__},
            )

        # ------------------------------
        # Delegate to UnifiedOrchestrator
        # ------------------------------
        try:
            result = self.orch.run_v23(task_name=task, ctx=ctx, options=options)

            # Ensure RouteResult
            if not isinstance(result, RouteResult):
                return RouteResult.error(
                    code="ORCH_RETURN_ERROR",
                    message="UnifiedOrchestrator returned non-RouteResult",
                    debug_info={"return_type": type(result).__name__},
                )

            return result

        except Exception as e:
            return RouteResult.error(
                code="ENTRY_EXCEPTION",
                message=str(e),
                debug_info={"task": task, "ctx": ctx, "options": options},
            )
