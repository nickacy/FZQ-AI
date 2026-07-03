# V24-Final — FederationEventBus
"""Federation EventBus module."""
import time
from typing import Any, Dict, List

class FederationEventBus:
    def __init__(self):
        self._log: List[Dict] = []

    def snapshot(self) -> dict:
        return {"log": list(self._log[-10:])}
