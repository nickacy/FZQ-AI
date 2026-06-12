# build_engine/project_scanner.py
import os
from typing import Dict


def scan_project(root_dir: str, target_structure: Dict[str, str]) -> Dict[str, bool]:
    result = {}
    for rel_path in target_structure.keys():
        full_path = os.path.join(root_dir, rel_path)
        result[rel_path] = os.path.exists(full_path)
    return result
