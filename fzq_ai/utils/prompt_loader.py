"""
Prompt Loader
Prompt 加载工具（中英文双语）
"""

def load_prompt_template(path: str) -> str:
    """
    Load a prompt template from file.
    从文件加载 Prompt 模板。
    """
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
