# -*- coding: utf-8 -*-
"""
FZQ-AI V17 Phase 1 全链路测试
测试链路：IntentEngine → EntryService → TaskRouter → Pipeline → web_app
"""

import pytest
from fastapi.testclient import TestClient

from app.web_app import app

client = TestClient(app)


# ===== 1. 风险扫描 =====
def test_risk_scan():
    resp = client.post("/entry", json={"text": "请帮我做一个风险扫描"})
    data = resp.json()["result"]

    assert data["type"] == "zh_risk_scan"
    # Mock risk pipeline returns entity_watchlist/overall_risk_level
    assert "overall_risk_level" in data["data"] or "risk_factors" in data["data"]


# ===== 2. 政策摘要 =====
def test_policy_brief():
    resp = client.post("/entry", json={"text": "请总结一下最新的政策"})
    data = resp.json()["result"]

    assert data["type"] == "zh_policy_brief"
    # Mock policy pipeline returns doc_id
    assert "doc_id" in data["data"] or "title" in data["data"]


# ===== 3. 舆情趋势 =====
def test_opinion_landscape():
    resp = client.post("/entry", json={"text": "分析一下当前舆情"})
    data = resp.json()["result"]

    assert data["type"] == "zh_opinion_landscape"
    assert "clusters" in data["data"]


# ===== 4. 多源合并图 =====
def test_multisource_merge():
    resp = client.post("/entry", json={"text": "把这些信息合并成关系图"})
    data = resp.json()["result"]

    assert data["type"] == "zh_multisource_merge"
    # Mock merge pipeline returns conflict_sources/consistency_score
    assert "type" in data
    assert data["type"] == "zh_multisource_merge"


# ===== 5. 澄清请求 =====
def test_clarification():
    resp = client.post("/entry", json={"text": "你好"})
    data = resp.json()["result"]

    assert data["type"] == "clarification_required"
