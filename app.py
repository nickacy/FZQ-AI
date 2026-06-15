# app.py
# 快捷入口：等同于 main.py
# 直接运行: streamlit run app.py

import runpy
import os
import sys

if __name__ == "__main__" or True:
    # 确保项目根目录在 path
    ROOT = os.path.abspath(os.path.dirname(__file__))
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    runpy.run_path(os.path.join(ROOT, "main.py"), run_name="__main__")
