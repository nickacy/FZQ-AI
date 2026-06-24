# src/fzq_ai/utils/prompt_loader.py

import os

def load_prompt_template(path: str) -> str:
    """
    Load a prompt template using module-style path.
    Example:
        "fzq_ai/prompts/zh/system_zh_intel.txt"
    """

    # 当前文件：src/fzq_ai/utils/prompt_loader.py
    # 项目根目录：.../FZQ-AI/src/
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    # 将 "fzq_ai/prompts/zh/xxx.txt" 转换为文件系统路径
    full_path = os.path.join(project_root, *path.split("/"))

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Prompt file not found: {full_path}")

    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()
