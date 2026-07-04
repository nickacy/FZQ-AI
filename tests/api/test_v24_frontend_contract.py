# -*- coding: utf-8 -*-
"""Frontend-facing V24 API compatibility tests."""

from fastapi.testclient import TestClient

from fzq_ai.api.app import app

client = TestClient(app)


def test_v24_entry_accepts_frontend_input_alias():
    resp = client.post("/api/v1/entry", json={"input": "测试前端输入"})

    assert resp.status_code == 200
    body = resp.json()
    assert "execution" in body
    assert "ui_schema" in body
    assert "output" in body


def test_v24_entry_accepts_workspace_query_alias():
    resp = client.post("/api/v1/entry", json={"query": "测试工作台输入"})

    assert resp.status_code == 200
    assert "execution" in resp.json()


def test_v24_agents_list_matches_frontend_shape():
    resp = client.post("/api/v1/agents/list", json={})

    assert resp.status_code == 200
    agents = resp.json()["agents"]
    assert agents
    assert {"id", "name", "description", "capabilities"}.issubset(agents[0])


def test_v24_entry_stream_returns_sse_done_marker():
    with client.stream("POST", "/api/v1/entry/stream", json={"text": "测试流式"}) as resp:
        body = "".join(resp.iter_text())

    assert resp.status_code == 200
    assert "data: " in body
    assert "data: [DONE]" in body
