"""
FZQ‑AI — CI Health Check Script
Purpose:
    Run a full pre‑flight check to ensure GitHub Actions CI will pass.
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path

REQUIRED_ACTIONS = {
    "actions/checkout": "v4",
    "actions/setup-python": "v5",
}

REQUIRED_PYTHON = (3, 11)
REQUIRED_PACKAGES = [
    "streamlit",
    "plotly",
    "networkx",
    "matplotlib",
    "langdetect",
    "feedparser",
    "lxml",
    "numpy",
    "pandas",
    "pillow",
    "openai",
    "google-generativeai",
    "deepseek",
]


def check_python_version():
    print("🔍 Checking Python version...")
    if sys.version_info[:2] != REQUIRED_PYTHON:
        print(f"❌ Python version mismatch: {sys.version_info[:2]} (expected {REQUIRED_PYTHON})")
        return False
    print("✅ Python version OK")
    return True


def check_requirements():
    print("\n🔍 Checking requirements.txt completeness...")
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt missing")
        return False

    with open("requirements.txt", "r", encoding="utf-8") as f:
        content = f.read()

    missing = [pkg for pkg in REQUIRED_PACKAGES if pkg not in content]

    if missing:
        print("❌ Missing packages in requirements.txt:")
        for m in missing:
            print(f"   - {m}")
        return False

    print("✅ requirements.txt OK")
    return True


def check_workflow():
    print("\n🔍 Checking GitHub Actions workflow...")

    wf = Path(".github/workflows/python.yml")
    if not wf.exists():
        print("❌ Workflow file .github/workflows/python.yml not found")
        return False

    content = wf.read_text()

    ok = True
    for action, version in REQUIRED_ACTIONS.items():
        pattern = rf"{action}@v(\d+)"
        match = re.search(pattern, content)
        if not match:
            print(f"❌ Missing action: {action}")
            ok = False
        else:
            found = match.group(1)
            if found != version.replace("v", ""):
                print(f"❌ {action} version outdated: v{found} (expected {version})")
                ok = False

    if ok:
        print("✅ Workflow actions OK")

    return ok


def check_imports():
    print("\n🔍 Checking Python imports...")

    ok = True
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg)
        except Exception:
            print(f"❌ Cannot import: {pkg}")
            ok = False

    if ok:
        print("✅ All imports OK")

    return ok


def check_pytest():
    print("\n🔍 Running pytest dry-run...")

    try:
        result = subprocess.run(["pytest", "--collect-only"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ pytest collection failed")
            print(result.stdout)
            print(result.stderr)
            return False
        print("✅ pytest collection OK")
        return True
    except FileNotFoundError:
        print("❌ pytest not installed")
        return False


def main():
    print("======================================")
    print(" FZQ‑AI — CI HEALTH CHECK")
    print("======================================\n")

    checks = [
        check_python_version(),
        check_requirements(),
        check_workflow(),
        check_imports(),
        check_pytest(),
    ]

    if all(checks):
        print("\n🎉 All checks passed — CI should succeed!")
    else:
        print("\n⚠️ Some checks failed — CI will likely fail.")


if __name__ == "__main__":
    main()
