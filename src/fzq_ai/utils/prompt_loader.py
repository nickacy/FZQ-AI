"""
Prompt Loader
"""
from pathlib import Path

# Base directory: src/fzq_ai -> resolves to the fzq_ai package root
# The prompt files are at: src/fzq_ai/prompts/zh/*.txt
# Pipeline code passes paths like: "fzq_ai/prompts/zh/zh_risk_scan.txt"
# Those are relative to the `src` directory.
_SRC_DIR = Path(__file__).resolve().parent.parent.parent  # utils -> fzq_ai -> src


def load_prompt_template(path: str) -> str:
    """Load a prompt template from file.

    Supports two path forms:
    1. Relative to src/ (e.g. "fzq_ai/prompts/zh/zh_risk_scan.txt")
    2. Absolute path (e.g. "C:/.../prompts.txt")
    3. Relative to CWD (fallback if neither matches)
    """
    p = Path(path)
    if p.is_absolute() and p.exists():
        pass  # use as-is
    elif (_SRC_DIR / path).exists():
        p = _SRC_DIR / path
    # else: fallback to original path (let FileNotFoundError surface)

    with open(p, "r", encoding="utf-8") as f:
        return f.read()
