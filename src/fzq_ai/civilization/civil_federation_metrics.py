# V24-Final — FederationMetrics
"""Federation Metrics module."""
import time
from typing import Any, Dict, List

class FederationMetrics:
    def __init__(self):
        self._log: List[Dict] = []

    def snapshot(self) -> dict:
        return {"log": list(self._log[-10:])}
