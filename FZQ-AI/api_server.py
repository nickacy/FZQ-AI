# api_server.py

import os
import yaml
from typing import List, Any

from fastapi import FastAPI
from pydantic import BaseModel

from fzq_ai.agent_hub import AgentHub


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

app = FastAPI(title="FZQ-AI Agent API", version="1.0.0")


# -----------------------------
# 请求模型
# -----------------------------
class NewsRequest(BaseModel):
    items: List[str]


class DailyReportRequest(BaseModel):
    items: List[str]


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
    merged = "\n".join(req.items)
    result = hub.run_news(merged)
    return {"summary": result}


# -----------------------------
# 叙事分析
# -----------------------------
@app.post("/narrative/analyze")
def narrative_analyze(req: NewsRequest):
    return hub.run_narrative(req.items)


# -----------------------------
# 风险分析
# -----------------------------
@app.post("/risk/analyze")
def risk_analyze(req: NewsRequest):
    return hub.run_risk(req.items)


# -----------------------------
# 每日简报
# -----------------------------
@app.post("/daily/report")
def daily_report(req: DailyReportRequest):
    return hub.run_daily_report(req.items)


# -----------------------------
# Metrics
# -----------------------------
@app.get("/metrics")
def metrics():
    return {"metrics": hub.get_metrics()}
