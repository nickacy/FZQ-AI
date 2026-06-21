# fzq_ai/prompts/template.py
"""Canonical PromptTemplate - all prompts import from here."""

from string import Template


class PromptTemplate:
    """
    Universal Prompt Template class.
    - Uses Python string.Template ($variable syntax)
    - Safe against injection (safe_substitute)
    - All prompts in fzq_ai/ use this class.
    """

    def __init__(self, template: str):
        self.template = Template(template)

    def render(self, **kwargs) -> str:
        """Render template with variables. Unmatched variables are left as-is."""
        return self.template.safe_substitute(**kwargs)
