# src/fzq_ai/llm/router_v2/selectors.py

from fzq_ai.llm.router_v2.rules import TASK_RULES, LENGTH_RULES, STRUCTURE_RULES


class TaskSelector:
    """
    根据任务类型、输入长度、结构化程度选择候选模型。
    """

    def select(self, task):
        task_type = task.get("task_type")
        text = task.get("input", "")
        length = len(text)

        # 1. 任务类型规则
        if task_type in TASK_RULES:
            return TASK_RULES[task_type]

        # 2. 输入长度规则
        for min_len, max_len, providers in LENGTH_RULES:
            if min_len <= length <= max_len:
                return providers

        # 3. 默认规则
        return ["glm-5.2", "deepseek", "qwen"]
