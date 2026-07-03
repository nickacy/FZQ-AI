# V24-Final — Civilization Federation Loop V2
"""Multi-level federation cycle across all v2 subsystems."""
from typing import List, Dict, Any
import time as _t

class CivilizationFederationLoopV2:
    def __init__(self):
        self._results: List[Dict] = []
        self._cycles: int = 0

    def run(self, civ) -> Dict[str, Any]:
        self._cycles += 1
        attrs = ["federation","council_v2","intelligence_v2","protocol_v2","bridge_v2","state_machine_v2","meta_federation","healing_federation","personality_federation","goal_federation","state_federation","reflection_federation"]
        result = {"cycle": self._cycles, "ts": _t.time()}
        for a in attrs:
            obj = getattr(civ, a, None)
            result[a] = obj.snapshot() if obj and hasattr(obj, 'snapshot') else None
        self._results.append(result)
        return result

    def snapshot(self) -> dict:
        return {"cycles": self._cycles, "results": list(self._results[-5:])}
