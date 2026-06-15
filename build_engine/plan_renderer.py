# build_engine/plan_renderer.py
from typing import List
from build_engine.plan_builder import BuildPlan, PlanItem

def _format_item(item: PlanItem) -> str:
    status = "✅ 已存在" if item.exists else "❌ 缺失"
    return f"  - {item.path:<35} {status}  # {item.description}"

def render_plan(plan: BuildPlan) -> str:
    lines = []

    for item in plan.items:

    missing = [i for i in plan.items if not i.exists]

    if not missing:
    else:
        for item in missing:
            lines.append(f"    * {item.path}  # {item.description}")

    return "\n".join(lines)
