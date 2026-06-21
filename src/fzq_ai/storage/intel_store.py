# fzq_ai/storage/intel_store.py

import os
import json
from typing import Any, Dict


class IntelStore:
    """
    IntelStore（统一版）
    - 保留全部旧功能
    - 统一路径：fzq_ai.storage.intel_store
    - 保存结构化情报（bundle）
    """

    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or os.path.join(os.getcwd(), "intel_store")
        os.makedirs(self.base_dir, exist_ok=True)

    def _path(self, run_id: str) -> str:
        return os.path.join(self.base_dir, f"{run_id}.json")

    def save_bundle(self, run_id: str, topic: str, bundle: Any, meta: Dict[str, Any]):
        """
        保存情报 bundle（保持旧格式）
        """
        data = {
            "run_id": run_id,
            "topic": topic,
            "bundle": bundle.dict() if hasattr(bundle, "dict") else bundle,
            "meta": meta,
        }

        with open(self._path(run_id), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_bundle(self, run_id: str) -> Dict[str, Any]:
        """
        加载情报 bundle（保持旧格式）
        """
        path = self._path(run_id)
        if not os.path.exists(path):
            return {}

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
