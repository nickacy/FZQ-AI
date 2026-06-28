# -*- coding: utf-8 -*-
"""
FZQ-AI Entry Adapter (V17 Phase 1)
连接入口层 EntryService 与真实 src/fzq_ai Pipelines
"""

from __future__ import annotations
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# ============================================================
# 1. 确保 src/ 在 Python 路径中
# ============================================================

ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


# ============================================================
# 2. IntentEngine 适配器
# ============================================================

from fzq_ai.core.intent_engine import classify as real_classify, IntentResult as RealIntentResult


class AdaptedIntentResult:
    """
    适配真实 IntentResult → 入口层统一结构
    """

    def __init__(self, real: RealIntentResult, raw_text: str, session_id: Optional[str]):
        self.task_type = real.task_type
        self.confidence = real.confidence
        self.language = real.language
        self.raw_text = raw_text
        self.metadata = {
            "session_id": session_id,
            "keywords_matched": real.keywords_matched,
            "reason": real.reason,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_type": self.task_type,
            "confidence": self.confidence,
            "language": self.language,
            "raw_text": self.raw_text,
            "metadata": self.metadata,
        }


class AdaptedIntentEngine:
    """
    入口层使用的 IntentEngine（统一接口）
    """

    def detect_intent(
        self,
        text: str,
        language: str = "zh",
        session_id: Optional[str] = None,
    ) -> AdaptedIntentResult:

        real = real_classify(text)

        # 覆盖语言（入口层优先）
        real.language = language

        return AdaptedIntentResult(real, text, session_id)


# ============================================================
# 3. Pipeline 适配器
# ============================================================

from fzq_ai.pipelines.zh_risk_scan_pipeline import ZhRiskScanPipeline
from fzq_ai.pipelines.zh_policy_brief_pipeline import ZhPolicyBriefPipeline
from fzq_ai.pipelines.zh_opinion_landscape_pipeline import ZhOpinionLandscapePipeline
from fzq_ai.pipelines.zh_multisource_merge_pipeline import ZhMultiSourceMergePipeline


class AdaptedPipeline:
    """
    适配真实 Pipeline.run(**kwargs) → 入口层统一接口 run(input_text, intent, route)
    """

    def __init__(self, real_pipeline):
        self._real = real_pipeline
        self.name = getattr(real_pipeline, "name", real_pipeline.__class__.__name__)

    async def run(self, input_text: str, intent: Any, route: Any) -> Dict[str, Any]:
        """
        入口层统一 Pipeline 执行接口
        """

        kwargs = {
            "input_text": input_text,
            "task_type": intent.task_type,
            "language": intent.language,
        }

        result = await self._real.run(**kwargs)

        # 错误处理
        if result.get("status") == "error":
            raise Exception(f"Pipeline {self.name} failed: {result.get('errors')}")

        # 注入 type 字段（前端路由用）
        result["type"] = intent.task_type

        return result


# ============================================================
# 4. PipelineRegistry（绕过损坏的 registry.py）
# ============================================================

class AdaptedPipelineRegistry:
    """
    入口层使用的 PipelineRegistry（硬编码注册）
    """

    def __init__(self):
        self._registry: Dict[str, AdaptedPipeline] = {
            "zh_risk_scan": AdaptedPipeline(ZhRiskScanPipeline()),
            "zh_policy_brief": AdaptedPipeline(ZhPolicyBriefPipeline()),
            "zh_opinion_landscape": AdaptedPipeline(ZhOpinionLandscapePipeline()),
            "zh_multisource_merge": AdaptedPipeline(ZhMultiSourceMergePipeline()),
        }

    def resolve_pipeline(self, task_type: str) -> Optional[AdaptedPipeline]:
        return self._registry.get(task_type)
