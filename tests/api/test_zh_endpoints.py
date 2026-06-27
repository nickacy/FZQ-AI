# -*- coding: utf-8 -*-
"""
FZQ-AI API Integration Tests (V15-Final)
中文情报任务 API 集成测试（V15 最终版）

测试内容：
- 4 个 zh-intel 端点是否可正常工作
- TaskRouter 是否正常路由
- 响应格式是否符合 V15 统一规范
"""

from fastapi.testclient import TestClient
from fzq_ai.api.zh_endpoints import router
from fastapi import FastAPI

# Create test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)


# ============================================================
# 1. Helper: Validate unified response format
# ============================================================

def assert_response_structure(resp_json):
    assert "success" in resp_json
    assert "task_type" in resp_json
    assert "pipeline" in resp_json
    assert "agent" in resp_json
    assert "model" in resp_json
    assert "fallback_used" in resp_json
    assert "error" in resp_json
    assert "output" in resp_json


# ============================================================
# 2. Test: zh_policy_brief
# ============================================================

def test_zh_policy_brief():
    payload = {"text": "请分析国务院最新政策"}
    resp = client.post("/api/zh/policy_brief", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert_response_structure(data)
    assert data["task_type"] == "zh_policy_brief"


# ============================================================
# 3. Test: zh_risk_scan
# ============================================================

def test_zh_risk_scan():
    payload = {"text": "请扫描当前地缘政治风险"}
    resp = client.post("/api/zh/risk_scan", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert_response_structure(data)
    assert data["task_type"] == "zh_risk_scan"


# ============================================================
# 4. Test: zh_opinion_landscape
# ============================================================

def test_zh_opinion_landscape():
    payload = {"text": "请分析公众舆论"}
    resp = client.post("/api/zh/opinion_landscape", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert_response_structure(data)
    assert data["task_type"] == "zh_opinion_landscape"


# ============================================================
# 5. Test: zh_multisource_merge
# ============================================================

def test_zh_multisource_merge():
    payload = {"text": "请合并多源新闻"}
    resp = client.post("/api/zh/multisource_merge", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert_response_structure(data)
    assert data["task_type"] == "zh_multisource_merge"


# ============================================================
# 6. Test: Error Path (missing text)
# ============================================================

def test_error_missing_text():
    resp = client.post("/api/zh/policy_brief", json={})
    assert resp.status_code == 422  # FastAPI validation error
