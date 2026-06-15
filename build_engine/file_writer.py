# build_engine/file_writer.py
import os


def ensure_directory(path: str):
    """确保目录存在"""
    dir_path = os.path.dirname(path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)


def safe_write_file(full_path: str, content: str) -> bool:
    """
    安全写盘：
    - 文件不存在 → 询问用户是否创建
    - 文件存在 → 不覆盖
    """
    if os.path.exists(full_path):
        print(f"[SKIP] 已存在：{full_path}")
        return False

    print(f"\n准备创建文件：{full_path}")
    choice = input("是否创建？(y/n): ").strip().lower()

    if choice != "y":
        print("[跳过]")
        return False

    ensure_directory(full_path)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[OK] 已创建：{full_path}")
    return True
