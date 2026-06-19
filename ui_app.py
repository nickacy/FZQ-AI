# ui_app.py — Phase 4‑3 修补兼容版（FastAPI ≥ 0.110）

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from fzq_ai.pipelines.daily_report_pipeline import DailyReportPipeline
from fzq_ai.schemas.pipeline_output import DailyReportPipelineOutput


# -----------------------------
# 请求参数 Schema
# -----------------------------
class DailyReportRequest(BaseModel):
    topic: str
    news_raw_texts: List[str]


# -----------------------------
# FastAPI 初始化
# -----------------------------
app = FastAPI(
    title="FZQ-AI Intelligence System",
    description="Daily Intelligence Report Generator",
    version="4.0",
)


# -----------------------------
# 启动事件（替代 on_startup 参数）
# -----------------------------
@app.on_event("startup")
async def startup_event():
    """
    FastAPI ≥ 0.110 不再支持 FastAPI(on_startup=[...])
    改为使用事件装饰器。
    """
    # 如果未来需要初始化缓存、加载模型、warm-up 等，可放在这里
    pass


# -----------------------------
# 核心接口：一次调用 → 完整日报
# -----------------------------
@app.post("/api/daily_report", response_model=DailyReportPipelineOutput)
async def generate_daily_report(req: DailyReportRequest):
    """
    Phase 4‑3：UI 只调用一次 DailyReportPipeline.run_async()
    后端自动并发执行所有 Pipeline
    """
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
