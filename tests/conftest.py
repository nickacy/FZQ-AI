# tests/conftest.py — pytest 路径配置
# 确保 pytest 可以正确导入 src/fzq_ai 包

import sys
from pathlib import Path

src_dir = Path(__file__).resolve().parents[1] / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
