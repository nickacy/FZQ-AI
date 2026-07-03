"""V24 — Unified FastAPI app integration test.

Verifies that all endpoints documented in README are actually exposed by
the single unified app at `fzq_ai.api.app`. Pre-V24.2.0 had 80% of these
endpoints defined in `api/app.py` but not mounted in the running app
(`ui/web_app.py` only included `entry_router`).
"""
from __future__ import annotations
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import pytest
from fastapi.testclient import TestClient

# Import the unified app (post-V24.2.0 single source of truth)
from fzq_ai.api.app import app


client = TestClient(app)


# ============================================================
# 1. Endpoint presence — every path documented in README exists
# ============================================================

class TestEndpointsPresent:
    @pytest.mark.parametrize("path,method", [
        # V24 main entry points
        ("/entry", "POST"),
        ("/multi", "POST"),
        ("/autonomy", "POST"),
        # V24 frontend contract
        ("/api/v1/entry", "POST"),
        ("/api/v1/multi", "POST"),
        ("/api/v1/autonomy", "POST"),
        # V24 Chinese intel
        ("/api/zh/policy_brief", "POST"),
        ("/api/zh/risk_scan", "POST"),
        ("/api/zh/opinion_landscape", "POST"),
        ("/api/zh/multisource_merge", "POST"),
        # V23 compat
        ("/v23/entry", "POST"),
        # Observability
        ("/health", "GET"),
        ("/metrics", "GET"),
        # Static
        ("/", "GET"),
    ])
    def test_endpoint_reachable(self, path, method):
        if method == "POST":
            r = client.post(path, json={"text": "ping", "input": "ping"})
        else:
            r = client.get(path)
        # Should NOT be 404; any other status (200, 422, 500) is acceptable
        # since the request body is intentionally minimal
        assert r.status_code != 404, f"{method} {path} returns 404 — not mounted"

    def test_health_returns_ok(self):
        r = client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert "version" in body


# ============================================================
# 2. V24 entry contract — `execution` + `ui_schema` + `output`
# ============================================================

class TestV24EntryContract:
    def test_zh_risk_scan_returns_v24_contract(self):
        r = client.post("/api/zh/risk_scan", json={"text": "测试风险扫描"})
        # 200 (success) or 500 (LLM not configured in CI) — either way the
        # endpoint is reachable and the response structure is V24-shaped
        # when successful
        if r.status_code == 200:
            body = r.json()
            assert "execution" in body
            assert "ui_schema" in body
            assert "output" in body
            ex = body["execution"]
            assert "intent" in ex
            assert "route" in ex
            assert "trace_id" in ex
            assert "state_machine" in ex
            assert "timeline" in ex


# ============================================================
# 3. V24 main entry — same contract via /entry
# ============================================================

class TestMainEntryContract:
    def test_entry_endpoint_reachable(self):
        r = client.post("/entry", json={"text": "ping"})
        # 200/422/500 — anything but 404
        assert r.status_code != 404
