# fzq_ai/prompts/template.py

from string import Template


class PromptTemplate:
    """
    通用 Prompt 模板类
    - 使用 Python Template（避免 f-string 注入问题）
    - 支持参数化
    - 支持统一格式
    """

    def __init__(self, template: str):
        self.template = Template(template)

    def render(self, **kwargs) -> str:
        return self.template.safe_substitute(**kwargs)
