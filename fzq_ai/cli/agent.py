"""
fzq_ai.cli.agent

命令行入口：
- 一键运行 TaskOrchestrator
- 支持 verbose / json / save 输出
- 结构专业、可扩展、可维护
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict

# --- 修复路径：确保 fzq_ai 可被正确 import ---
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:

from fzq_ai.orchestrator.task_orchestrator import TaskOrchestrator
from fzq_ai.domain.models import ServiceResult

def print_report(data: Dict[str, Any]) -> None:
    """
    """
    print("\n==============================")
    print("🧠 FZQ-AI Daily Intelligence Report")
    print("==============================\n")

    if isinstance(data, dict):
        for key, value in data.items():
            print(f"--- {key.upper()} ---")
            print(value)
            print()
    else:
        print(data)

async def run_orchestrator(verbose: bool) -> ServiceResult:
    orch = TaskOrchestrator()
    result = await orch.orchestrate()

    if verbose:
        print("\n[DEBUG] Raw ServiceResult:")
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))

    return result

def save_report(data: Dict[str, Any], path: str) -> str:
    """
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path

def main():
    parser = argparse.ArgumentParser(
        description="FZQ-AI Command Line Agent — Generate Daily Intelligence Report"

        "--verbose",

        "--json",

        "--save",

    # --- Run orchestrator ---
    result: ServiceResult = asyncio.run(run_orchestrator(args.verbose))

    if not result.success:
        print("\n❌ 生成失败：", result.error)
        sys.exit(1)

    data = result.data or {}

    # --- JSON 输出 ---
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print_report(data)

    # --- 保存文件 ---
    if args.save:
        print(f"\n💾 日报已保存到：{saved_path}")

if __name__ == "__main__":
