"""
MultiModelOrchestrator
中英文双语版本
-----------------------------------------
This orchestrator coordinates multiple LLMs for a single structured task.
该 Orchestrator 用于在单个结构化任务上协调多个大模型协作：

- GLM-5.2：中文深度理解专家（内容初稿）
- DeepSeek：结构与逻辑优化专家
- Minimax：结构检查与字段补全专家
- 豆包：最终格式化与规范化专家

协作顺序（默认）：
GLM-5.2 → DeepSeek → Minimax → 豆包 → Pydantic Schema 校验
"""

from typing import Optional, List

from fzq_ai.clients.model_client import ModelClient


class MultiModelOrchestrator:
    """
    多模型协作 Orchestrator

    用法示例（以 zh_policy_brief 为例）：

        orchestrator = MultiModelOrchestrator()
        final_json_str = await orchestrator.run_chain(
            base_prompt=prompt,  # 已经拼好的 system + task prompt
            task_name="zh_policy_brief"
        )
    """

    def __init__(
        self,
        enable_glm: bool = True,
        enable_deepseek: bool = True,
        enable_minimax: bool = True,
        enable_doubao: bool = True,
    ):
        # 这里假设你在 ModelClient 内部通过 model_name 路由到不同厂商
        # 例如：glm-5.2 / deepseek-chat / minimax-chat / doubao-chat
        self.enable_glm = enable_glm
        self.enable_deepseek = enable_deepseek
        self.enable_minimax = enable_minimax
        self.enable_doubao = enable_doubao

        self.glm_client: Optional[ModelClient] = ModelClient("glm-5.2") if enable_glm else None
        self.deepseek_client: Optional[ModelClient] = ModelClient("deepseek-chat") if enable_deepseek else None
        self.minimax_client: Optional[ModelClient] = ModelClient("minimax-chat") if enable_minimax else None
        self.doubao_client: Optional[ModelClient] = ModelClient("doubao-chat") if enable_doubao else None

    # ------------------------------------------------------------------
    # 各模型的 Patch Prompt（角色化补丁）
    # ------------------------------------------------------------------

    def _patch_glm(self, task_name: str) -> str:
        return f"""
你是中文深度理解专家，负责任务：{task_name}。
你的目标是：在保证中文理解准确、信息完整的前提下，生成尽可能丰富的结构化初稿。

要求：
1. 必须输出 JSON 格式。
2. 字段名必须与给定 Schema 一致（不要新增字段）。
3. 可以适当冗余内容，但不要省略关键信息。
4. 不要在 JSON 外输出任何解释性文字。
"""

    def _patch_deepseek(self, task_name: str) -> str:
        return f"""
你是结构与逻辑优化专家，负责任务：{task_name}。
你会接收到一个 JSON 初稿，你的任务是：

1. 保留所有有用信息，不得删除关键信息。
2. 优化 JSON 结构，使其更符合 Schema 要求。
3. 修正字段之间的逻辑不一致。
4. 不得新增 Schema 之外的字段。
5. 输出必须是合法 JSON，且不包含任何 JSON 之外的文本。
"""

    def _patch_minimax(self, task_name: str) -> str:
        return f"""
你是结构检查专家，负责任务：{task_name}。
你会接收到一个 JSON，你的任务是：

1. 严格对齐给定 Schema，检查所有字段是否存在。
2. 对缺失但必需的字段进行合理补全。
3. 修正所有非法枚举值，改为 Schema 允许的值。
4. 删除所有 Schema 未定义的字段。
5. 禁止输出空字符串字段，如无内容请省略该字段。
6. 输出必须是合法 JSON，且不包含任何 JSON 之外的文本。
"""

    def _patch_doubao(self, task_name: str) -> str:
        return f"""
你是代码与结构规范化专家，负责任务：{task_name}。
你会接收到一个 JSON，你的任务是：

1. 不改变任何语义内容，只做格式与结构规范化。
2. 确保 JSON 缩进、数组、对象结构清晰。
3. 删除所有值为 null 或空字符串的字段。
4. 确保字段命名与 Schema 完全一致。
5. 输出必须是合法 JSON，且不包含任何 JSON 之外的文本。
"""

    # ------------------------------------------------------------------
    # 单模型调用封装
    # ------------------------------------------------------------------

    async def _call_model(
        self,
        client: ModelClient,
        patch_prompt: str,
        base_prompt: str,
        previous_json: Optional[str] = None,
    ) -> str:
        if previous_json:
            prompt = f"{patch_prompt}\n\n下面是待处理的 JSON：\n```json\n{previous_json}\n```"
        else:
            prompt = f"{patch_prompt}\n\n下面是任务输入：\n{base_prompt}"

        raw = await client.chat_async(prompt)
        return raw

    # ------------------------------------------------------------------
    # 多模型协作主入口
    # ------------------------------------------------------------------

    async def run_chain(
        self,
        base_prompt: str,
        task_name: str,
        enabled_models: Optional[List[str]] = None,
    ) -> str:
        """
        多模型协作主流程：

        默认顺序：
        GLM-5.2 → DeepSeek → Minimax → 豆包

        参数：
        - base_prompt: 已经拼好的 system + task prompt（含输入 JSON）
        - task_name: 任务名（如 zh_policy_brief / zh_risk_scan 等）
        - enabled_models: 可选，指定启用哪些模型，例如 ["glm", "minimax"]
        """
        if enabled_models is None:
            enabled_models = ["glm", "deepseek", "minimax", "doubao"]

        current_json: Optional[str] = None

        # 1. GLM-5.2：内容初稿
        if "glm" in enabled_models and self.glm_client is not None:
            glm_patch = self._patch_glm(task_name)
            current_json = await self._call_model(
                client=self.glm_client,
                patch_prompt=glm_patch,
                base_prompt=base_prompt,
                previous_json=None,
            )

        # 2. DeepSeek：结构与逻辑优化
        if "deepseek" in enabled_models and self.deepseek_client is not None and current_json is not None:
            ds_patch = self._patch_deepseek(task_name)
            current_json = await self._call_model(
                client=self.deepseek_client,
                patch_prompt=ds_patch,
                base_prompt=base_prompt,
                previous_json=current_json,
            )

        # 3. Minimax：结构检查与字段补全
        if "minimax" in enabled_models and self.minimax_client is not None and current_json is not None:
            mm_patch = self._patch_minimax(task_name)
            current_json = await self._call_model(
                client=self.minimax_client,
                patch_prompt=mm_patch,
                base_prompt=base_prompt,
                previous_json=current_json,
            )

        # 4. 豆包：最终格式化与规范化
        if "doubao" in enabled_models and self.doubao_client is not None and current_json is not None:
            db_patch = self._patch_doubao(task_name)
            current_json = await self._call_model(
                client=self.doubao_client,
                patch_prompt=db_patch,
                base_prompt=base_prompt,
                previous_json=current_json,
            )

        if current_json is None:
            return ""

        return current_json
