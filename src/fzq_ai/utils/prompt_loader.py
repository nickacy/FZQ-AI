"""
Prompt Loader — loads prompt templates from package resources.

Uses importlib.resources (PEP 451) so that:
  - works regardless of current working directory
  - works inside zipapp / PyInstaller
  - works inside Docker (no /src baked paths)
"""
from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Union


def load_prompt_template(path: Union[str, Path]) -> str:
    """Load a prompt template from the `fzq_ai.prompts` package.

    Args:
        path: Either:
          - A relative path like "zh/zh_risk_scan.txt" (resolved under fzq_ai.prompts)
          - A package-relative path like "fzq_ai/prompts/zh/zh_risk_scan.txt"
            (legacy: we strip the "fzq_ai/prompts/" prefix)
          - An absolute filesystem path

    Returns:
        File contents as a UTF-8 string.

    Raises:
        FileNotFoundError: if the resource cannot be located.
    """
    # Absolute filesystem path → open directly.
    p = Path(path)
    if p.is_absolute():
        return p.read_text(encoding="utf-8")

    text = str(path).replace("\\", "/")

    # Normalize legacy "fzq_ai/prompts/X" form to "X"
    prefix = "fzq_ai/prompts/"
    if text.startswith(prefix):
        text = text[len(prefix):]

    # Try the package resource
    try:
        return (resources.files("fzq_ai.prompts") / text).read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError):
        pass

    # Fallback: treat as a filesystem path relative to CWD
    return p.read_text(encoding="utf-8")
