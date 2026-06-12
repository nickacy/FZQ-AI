"""Convert all non-UTF-8 files in project to UTF-8."""
import os, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
BACKUP = os.path.join(BASE, "fzq_ai_agent", "data", "backups", "encoding_fix")
TARGET_DIRS = [
    os.path.join(BASE, "fzq_ai_agent", "utils"),
    os.path.join(BASE, "fzq_ai_agent", "dashboard", "pages"),
    os.path.join(BASE, "fzq_ai_agent", "report"),
]
EXTRA = [os.path.join(BASE, "structure.txt")]
ENCODINGS = ["utf-8", "gbk", "gb18030", "latin-1"]

def is_chinese(text):
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

def detect_encoding(fpath):
    for enc in ENCODINGS:
        try:
            with open(fpath, "r", encoding=enc) as f:
                content = f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
        if enc == "latin-1" and is_chinese(content):
            try:
                with open(fpath, "r", encoding="gbk") as f2:
                    f2.read()
                return "gbk"
            except:
                pass
        return enc
    return None

def collect():
    files = []
    for d in TARGET_DIRS:
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if not fn.endswith(".py"):
                continue
            fp = os.path.join(d, fn)
            enc = detect_encoding(fp)
            if enc and enc != "utf-8":
                files.append((fp, enc))
    for fp in EXTRA:
        if os.path.isfile(fp):
            enc = detect_encoding(fp)
            if enc and enc != "utf-8":
                files.append((fp, enc))
    return files

def convert(fp, enc):
    with open(fp, "r", encoding=enc) as f:
        content = f.read()
    os.makedirs(BACKUP, exist_ok=True)
    shutil.copy2(fp, os.path.join(BACKUP, os.path.basename(fp)))
    with open(fp, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    files = collect()
    if not files:
        print("All UTF-8.")
        return
    print(f"Found {len(files)} non-UTF-8 file(s):")
    for fp, enc in files:
        print(f"  [{enc}] {fp}")
    print(f"\nBackup: {BACKUP}")
    ok = fail = 0
    for fp, enc in files:
        try:
            convert(fp, enc)
            print(f"  OK  {fp}")
            ok += 1
        except Exception as e:
            print(f"  FAIL {fp}: {e}")
            fail += 1
    print(f"\nDone: {ok} ok, {fail} fail.")

if __name__ == "__main__":
    main()
