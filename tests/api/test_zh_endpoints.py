# -*- coding: utf-8 -*-
"""FZQ-AI API Integration Tests (V24 — unified contract)"""
from fastapi.testclient import TestClient
from fzq_ai.api.app import app

client = TestClient(app)


def assert_v24_structure(resp_json):
    """Validate V24 contract fields."""
    assert "execution" in resp_json, "Missing 'execution'"
    assert "ui_schema" in resp_json, "Missing 'ui_schema'"
    assert "output" in resp_json, "Missing 'output'"
    ex = resp_json["execution"]
    for field in ["intent", "route", "pipeline", "model", "agent",
                   "timeline", "state_machine", "trace_id"]:
        assert field in ex, f"Missing execution.{field}"


def test_zh_policy_brief():
    payload = {"text": "\u8bf7\u5206\u6790\u56fd\u52a1\u9662\u6700\u65b0\u653f\u7b56"}
    resp = client.post("/api/zh/policy_brief", json=payload)
    assert resp.status_code == 200
    assert_v24_structure(resp.json())


def test_zh_risk_scan():
    payload = {"text": "\u8bf7\u626b\u63cf\u5f53\u524d\u5730\u7f18\u653f\u6cbb\u98ce\u9669"}
    resp = client.post("/api/zh/risk_scan", json=payload)
    assert resp.status_code == 200
    assert_v24_structure(resp.json())


def test_zh_opinion_landscape():
    payload = {"text": "\u8bf7\u5206\u6790\u516c\u4f17\u8206\u8bba"}
    resp = client.post("/api/zh/opinion_landscape", json=payload)
    assert resp.status_code == 200
    assert_v24_structure(resp.json())


def test_zh_multisource_merge():
    payload = {"text": "\u8bf7\u5408\u5e76\u591a\u6e90\u65b0\u95fb"}
    resp = client.post("/api/zh/multisource_merge", json=payload)
    assert resp.status_code == 200
    assert_v24_structure(resp.json())


def test_error_missing_text():
    resp = client.post("/api/zh/policy_brief", json={})
    assert resp.status_code == 422
