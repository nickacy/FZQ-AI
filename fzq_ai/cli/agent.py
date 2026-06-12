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
    sys.path.insert(0, ROOT)

from fzq_ai.orchestrator.task_orchestrator import TaskOrchestrator
from fzq_ai.domain.models import ServiceResult


def print_report(data: Dict[str, Any]) -> None:
    """
    终端友好格式输出日报。
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
    保存日报到文件。
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path


def main():
    parser = argparse.ArgumentParser(
        description="FZQ-AI Command Line Agent — Generate Daily Intelligence Report"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示调试信息（ServiceResult 原始结构）",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出日报",
    )

    parser.add_argument(
        "--save",
        type=str,
        default=None,
        help="将日报保存到指定文件路径，例如：--save reports/daily.json",
    )

    args = parser.parse_args()

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
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = args.save.replace("{timestamp}", timestamp)
        saved_path = save_report(data, path)
        print(f"\n💾 日报已保存到：{saved_path}")


if __name__ == "__main__":
    main()
