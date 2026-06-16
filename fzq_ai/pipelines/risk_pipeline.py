# fzq_ai/pipelines/risk_pipeline.py

from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.domain.models import ServiceResult, ok, err
from fzq_ai.storage.intel_store import IntelStore
import uuid


class RiskPipeline:
    """
    风险分析 Pipeline（Legacy 保留版）
    - 保留全部旧功能
    - MINIMAX P0 修复：query 未定义
    """

    def __init__(self, llm_router=None):
        self.llm_router = llm_router or LLMRouter()

    def run(self, topic: str = "", articles=None) -> ServiceResult:
        """
        执行风险分析流程
        """
        # ⭐ P0 修复：补齐 query 变量，避免 NameError
        query = topic or ""

        try:
            # 1. 构建 prompt（旧逻辑保留）
            prompt = self._build_prompt(query, articles)

            # 2. 调用 LLM（旧逻辑保留）
            raw = self.llm_router.route("risk_intel", prompt)

            # 3. 保存到 IntelStore（旧逻辑保留）
            try:
                store = IntelStore()
                run_id = str(uuid.uuid4())
                from fzq_ai.domain.models import IntelBundle, IntelMeta
                bundle = IntelBundle(
                    meta=IntelMeta(topics=[query], regions=[], depth="normal"),
                    articles=articles or [],
                    events=[],
                )
                store.save_bundle(run_id, query, bundle, {"pipeline": "risk_pipeline"})
            except Exception:
                pass

            return ok(raw)

        except Exception as e:
            return err(str(e))

    # ---------------------------------------------------------
    # 私有方法（旧逻辑保留）
    # ---------------------------------------------------------
    def _build_prompt(self, query: str, articles):
        context = ""
        if articles:
            lines = []
            for i, a in enumerate(articles[:10], 1):
                lines.append(f"{i}. {a.title_original}")
            context = "\n".join(lines)

        return (
            f"你是一名风险分析专家，请根据以下主题生成风险评估：\n"
            f"主题：{query}\n\n"
            f"相关新闻：\n{context}\n\n"
            f"请输出：\n"
            f"1. 主要风险点\n"
            f"2. 潜在影响\n"
            f"3. 未来 30 天的风险趋势预测\n"
        )
