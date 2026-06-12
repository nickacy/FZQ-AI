import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))

EXCLUDE_DIRS = {"venv", "venv311", ".git", ".vscode", "__pycache__"}

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"[创建目录] {path}")

def move_file(src, dst_dir):
    if os.path.exists(src):
        ensure_dir(dst_dir)
        dst = os.path.join(dst_dir, os.path.basename(src))
        shutil.move(src, dst)
        print(f"[移动] {src} → {dst}")

def remove_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"[删除目录] {path}")

print("\n=== Nick‑Agent 项目自动清理开始 ===\n")

# 1. 创建标准目录结构
dirs = [
    "services",
    "agent/pipeline",
    "agent/engines",
    "agent/dashboard",
    "tests",
    "tools",
    "data/cache",
    "data/output",
    "data/logs",
]
for d in dirs:
    ensure_dir(os.path.join(ROOT, d))

# 2. 移动测试文件
move_file(os.path.join(ROOT, "test_all.py"), os.path.join(ROOT, "tests"))
move_file(os.path.join(ROOT, "test_deepseek_api.py"), os.path.join(ROOT, "tests"))

# 3. 移动工具脚本
move_file(os.path.join(ROOT, "_convert_to_utf8.py"), os.path.join(ROOT, "tools"))
move_file(os.path.join(ROOT, "_encoding_check.py"), os.path.join(ROOT, "tools"))

# 4. 删除 egg-info（构建残留）
remove_dir(os.path.join(ROOT, "fzq_ai_agent.egg-info"))

# 5. 创建 __init__.py（排除 venv 等目录）
for root, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    if "__init__.py" not in files:
        open(os.path.join(root, "__init__.py"), "a").close()

print("\n=== 清理完成！项目结构已优化 ===\n")
