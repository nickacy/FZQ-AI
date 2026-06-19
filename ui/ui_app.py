from fastapi import FastAPI
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List

from fzq_ai.pipelines.daily_report_pipeline import DailyReportPipeline
from fzq_ai.schemas.pipeline_output import DailyReportPipelineOutput


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown


app = FastAPI(
    title="FZQ‑AI Intelligence System",
    version="4.0",
    lifespan=lifespan,
)


class DailyReportRequest(BaseModel):
    topic: str
    news_raw_texts: List[str]


@app.post("/api/daily_report", response_model=DailyReportPipelineOutput)
async def generate_daily_report(req: DailyReportRequest):
    pipeline = DailyReportPipeline()
    result = await pipeline.run_async(
        topic=req.topic,
        news_raw_texts=req.news_raw_texts,
    )
    return result
