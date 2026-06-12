# build_engine/plan_builder.py
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class PlanItem:
    path: str
    exists: bool
    description: str


@dataclass
class BuildPlan:
    root_dir: str
    items: List[PlanItem]


def build_plan(root_dir: str, scan_result: Dict[str, bool], target_structure: Dict[str, str]) -> BuildPlan:
    items = []
    for path, desc in target_structure.items():
        exists = scan_result.get(path, False)
        items.append(PlanItem(path=path, exists=exists, description=desc))
    return BuildPlan(root_dir=root_dir, items=items)
