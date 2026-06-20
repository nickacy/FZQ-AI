# ui_app.py — FastAPI 2.0 lifespan 兼容版

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager
from fzq_ai.pipelines.daily_report_pipeline import DailyReportPipeline
from fzq_ai.schemas.pipeline_output import DailyReportPipelineOutput
from fzq_ai.ui.views.zh_intel import render_zh_intel_page

if page == "Chinese Intelligence / 中文情报中心":
    render_zh_intel_page()


# -----------------------------
# lifespan（替代 on_event）
# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    # 如果未来需要初始化缓存、加载模型等，可以放这里
    yield
    # shutdown
    # 清理资源（如果需要）


# -----------------------------
# FastAPI 初始化
# -----------------------------
app = FastAPI(
    title="FZQ-AI Intelligence System",
    description="Daily Intelligence Report Generator",
    version="4.0",
    lifespan=lifespan,   # ⭐ 新写法
)


# -----------------------------
# 请求参数 Schema
# -----------------------------
class DailyReportRequest(BaseModel):
    topic: str
    news_raw_texts: List[str]


# -----------------------------
# 核心接口：一次调用 → 完整日报
# -----------------------------
@app.post("/api/daily_report", response_model=DailyReportPipelineOutput)
async def generate_daily_report(req: DailyReportRequest):
    pipeline = DailyReportPipeline()

    result = await pipeline.run_async(
        topic=req.topic,
        news_raw_texts=req.news_raw_texts,
    )

    return result


# -----------------------------
# 本地运行入口
# -----------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
