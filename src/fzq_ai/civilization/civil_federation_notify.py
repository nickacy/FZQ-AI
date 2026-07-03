# V24-Final — FederationNotifier
"""Federation Notifier module."""
import time
from typing import Any, Dict, List

class FederationNotifier:
    def __init__(self):
        self._log: List[Dict] = []

    def snapshot(self) -> dict:
        return {"log": list(self._log[-10:])}
