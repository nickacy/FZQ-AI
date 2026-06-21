# src/fzq_ai/agents/tasks/policy_brief_agent.py
from fzq_ai.agents.base import BaseAgent, AgentContext, AgentResult
from fzq_ai.core.llm_router import LLMRouter
from fzq_ai.quality.deepseek_struct_opt import DeepSeekStructOptimizer
from fzq_ai.quality.minimax import validate_and_fix
from fzq_ai.utils.json_formatter import format_final
from fzq_ai.quality.schemas import get_schema

class PolicyBriefAgent(BaseAgent):
    name = "zh_policy_brief"

    def __init__(self) -> None:
        self._router = LLMRouter()
        self._struct_opt = DeepSeekStructOptimizer()

    def run(self, ctx: AgentContext) -> AgentResult:
        trace: list[str] = []
        schema = get_schema("zh_policy_brief")

        # 1. GLM-5.2：中文深度理解 + 初稿
        glm_output = self._router.route_and_generate(
            prompt=ctx.raw_input,
            task_type="zh_policy_brief",
            enable_repair=False,
            enable_format=False,
        )
        trace.append("glm_done")

        # 2. DeepSeek：结构优化
        ds_result = self._struct_opt.optimize(
            task_name="zh_policy_brief",
            schema=schema,
            raw_draft=glm_output,
        )
        trace.append("deepseek_struct_opt_done")

        # 3. Minimax：Schema 校验 + 字段补全
        mm_result = validate_and_fix(
            raw_json=ds_result.optimized,
            schema=schema,
            schema_name="zh_policy_brief",
            options={
                "strict_mode": True,
                "auto_fix": True,
                "allow_extra_fields": False,
            },
        )
        trace.append("minimax_validate_done")

        # 4. 豆包：最终格式化
        formatted_str = format_final({"json": mm_result.data, "schema": schema})
        trace.append("doubao_format_done")

        return AgentResult(
            ok=True,
            data=formatted_str,  # 或 json.loads(formatted_str)，看下游需要
            warnings=[],
            trace=trace,
        )
