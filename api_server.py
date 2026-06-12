# api_server.py

import os
import yaml
from typing import List, Dict, Any, Union

from fastapi import FastAPI
from pydantic import BaseModel

from fzq_ai.agent_hub import AgentHub
from fzq_ai.task_orchestrator import TaskOrchestrator


# -----------------------------
# 配置加载
# -----------------------------
def load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "fzq_ai", "config", "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


config = load_config()
hub = AgentHub(config)
orchestrator = TaskOrchestrator(hub)

app = FastAPI(title="FZQ‑AI Agent API", version="1.0.0")


# -----------------------------
# 请求模型
# -----------------------------
class NewsRequest(BaseModel):
    items: List[str]


class NarrativeItem(BaseModel):
    title: str
    content: str


class NarrativeRequest(BaseModel):
    items: Union[NarrativeItem, List[NarrativeItem]]


class RiskRequest(BaseModel):
    items: Union[str, List[str]]


class DailyReportRequest(BaseModel):
    items: List[str]


class CodeRequest(BaseModel):
    code: str


# -----------------------------
# 健康检查
# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# -----------------------------
# 新闻摘要
# -----------------------------
@app.post("/news/summary")
def news_summary(req: NewsRequest):
    result = hub.summarize_news_list(req.items)
    return {"summary": result}


# -----------------------------
# 叙事分析
# -----------------------------
@app.post("/narrative/analyze")
def narrative_analyze(req: NarrativeRequest):
    if isinstance(req.items, NarrativeItem):
        payload = {"title": req.items.title, "content": req.items.content}
    else:
        payload = [{"title": x.title, "content": x.content} for x in req.items]

    return hub.run_narrative(payload)


# -----------------------------
# 风险分析
# -----------------------------
@app.post("/risk/analyze")
def risk_analyze(req: RiskRequest):
    return hub.run_risk(req.items)


# -----------------------------
# 每日简报
# -----------------------------
@app.post("/daily/report")
def daily_report(req: DailyReportRequest):
    return hub.run_daily_report(req.items)


# -----------------------------
# 代码解释
# -----------------------------
@app.post("/code/explain")
def code_explain(req: CodeRequest):
    return {"analysis": hub.explain_code(req.code)}


# -----------------------------
# Metrics
# -----------------------------
@app.get("/metrics")
def metrics():
    return {"metrics": hub.get_metrics()}
