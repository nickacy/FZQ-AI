# build_engine/skeleton_writer.py
import os

def is_empty_file(path: str) -> bool:
    """判断文件是否为空（0 字节或只有换行/空白）"""
    if not os.path.exists(path):
        return True
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        return len(content) == 0
    except:
        return False

def ensure_directory(path: str):
    """确保目录存在"""
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

def write_skeleton(path: str, content: str):
    """写入骨架内容（UTF‑8）"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def safe_write_skeleton(path: str, content: str):
    """
    """
    if not os.path.exists(path) or is_empty_file(path):
        print(f"[AUTO] 写入骨架：{path}")
        write_skeleton(path, content)
        return True

    # 文件已有内容 → 询问
    print(f"\n检测到文件已有内容：{path}")
    choice = input("是否覆盖为标准骨架？(y/n): ").strip().lower()

    if choice == "y":
        print(f"[OK] 已覆盖：{path}")
        return True

    print("[跳过]")
    return False
