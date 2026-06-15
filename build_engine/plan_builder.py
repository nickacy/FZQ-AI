# build_engine/plan_builder.py
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class PlanItem:

@dataclass
class BuildPlan:

def build_plan(
    root_dir: str, scan_result: Dict[str, bool], target_structure: Dict[str, str]
) -> BuildPlan:
    for path, desc in target_structure.items():
        exists = scan_result.get(path, False)
        items.append(PlanItem(path=path, exists=exists, description=desc))
    return BuildPlan(root_dir=root_dir, items=items)
