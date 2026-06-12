# build_engine/plan_renderer.py
from typing import List
from build_engine.plan_builder import BuildPlan, PlanItem


def _format_item(item: PlanItem) -> str:
    status = "✅ 已存在" if item.exists else "❌ 缺失"
    return f"  - {item.path:<35} {status}  # {item.description}"


def render_plan(plan: BuildPlan) -> str:
    lines = []
    lines.append(f"[SCAN] 根目录: {plan.root_dir}")
    lines.append("")
    lines.append("[STRUCTURE]")

    for item in plan.items:
        lines.append(_format_item(item))

    missing = [i for i in plan.items if not i.exists]

    lines.append("")
    lines.append("[PLAN]")

    if not missing:
        lines.append("  - 所有目标文件均已存在。")
    else:
        lines.append("  - 建议生成以下缺失文件：")
        for item in missing:
            lines.append(f"    * {item.path}  # {item.description}")

    lines.append("")
    lines.append("[NOTE] 当前为 v1.0‑alpha：仅分析，不写入文件。")
    return "\n".join(lines)
