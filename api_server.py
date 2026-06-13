# api_server.py
# FZQ-AI Intelligence API Server

import os
from dotenv import load_dotenv

# ============================
#  加载环境变量
# ============================
load_dotenv(override=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fzq_ai.pipelines.news_pipeline import NewsPipeline
from fzq_ai.pipelines.narrative_pipeline import NarrativePipeline
from fzq_ai.pipelines.risk_pipeline import RiskPipeline
from fzq_ai.pipelines.daily_report_pipeline import DailyReportPipeline
from fzq_ai.orchestrator.task_orchestrator import TaskOrchestrator


# ============================
#  FastAPI 初始化
# ============================
app = FastAPI(title="FZQ-AI Intelligence API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================
#  API 路由
# ============================

@app.get("/")
def root():
    return {"status": "ok", "message": "FZQ-AI API Server is running"}


@app.get("/news")
def news(topic: str):
    pipeline = NewsPipeline()
    result = pipeline.run(topic)
    return {"success": True, "data": result}


@app.get("/narrative")
def narrative(text: str):
    pipeline = NarrativePipeline()
    result = pipeline.run(text)
    return {"success": True, "data": result}


@app.get("/risk")
def risk(topic: str):
    pipeline = RiskPipeline()
    result = pipeline.run(topic)
    return {"success": True, "data": result}


@app.get("/daily")
def daily():
    pipeline = DailyReportPipeline()
    result = pipeline.run()
    return {"success": True, "data": result}


@app.get("/task")
def task(cmd: str):
    orchestrator = TaskOrchestrator()
    result = orchestrator.run(cmd)
    return {"success": True, "data": result}


# ============================
#  启动提示
# ============================
if __name__ == "__main__":
    print("FZQ-AI API Server starting...")
    print("Visit: http://localhost:8000")
    print("Use: uvicorn api_server:app --reload --port 8000")
