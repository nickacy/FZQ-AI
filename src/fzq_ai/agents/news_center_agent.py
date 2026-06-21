# src/fzq_ai/agents/news_center_agent.py
from fzq_ai.agents.base import BaseAgent, AgentContext, AgentResult
from fzq_ai.agents.orchestrator import AgentOrchestrator

class NewsCenterAgent(BaseAgent):
    """
    个人全球信息新闻中心总控 Agent：
    - 拉取多源多语言信息
    - 交给下游任务 Agent（policy/risk/opinion/merge）
    - 聚合成“广泛、平衡、尽量无偏”的个人情报视图
    """
    name = "news_center"

    def __init__(self) -> None:
        self._orchestrator = AgentOrchestrator()

    def run(self, ctx: AgentContext) -> AgentResult:
        trace: list[str] = []

        # 1. 拉取多源多语言原始信息（后续可接 RSS/API/抓取）
        # placeholder: ctx.raw_input 视为已获取的多源文本

        # 2. 调用四大任务 Agent（可并行）
        policy = self._orchestrator.run_task("zh_policy_brief", ctx)
        risk = self._orchestrator.run_task("zh_risk_scan", ctx)
        opinion = self._orchestrator.run_task("zh_opinion_landscape", ctx)
        merge = self._orchestrator.run_task("zh_multisource_merge", ctx)

        trace.extend([
            "policy_brief_done",
            "risk_scan_done",
            "opinion_landscape_done",
            "multisource_merge_done",
        ])

        # 3. 聚合为“个人信息中心视图”（后续可细化结构）
        data = {
            "policy_brief": policy.data,
            "risk_scan": risk.data,
            "opinion_landscape": opinion.data,
            "multisource_merge": merge.data,
        }

        return AgentResult(
            ok=True,
            data=data,
            warnings=[*policy.warnings, *risk.warnings, *opinion.warnings, *merge.warnings],
            trace=trace,
        )
