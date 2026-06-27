# app/web_app.py
"""
FZQ-AI Entry Layer · V15
Bloomberg Terminal Theme + IntentEngine + TaskRouter + Pipelines
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ---- 核心依赖（按你现有/规划的模块路径） ----
from core.theme import inject_theme
from core.intent_engine import IntentEngine
from core.task_router import TaskRouter
from core.pipelines import PipelineRegistry


# ---------- FastAPI 应用初始化 ----------
app = FastAPI(title="FZQ-AI Entry Layer V15")

# CORS（方便你后面挂前端 / 移动端）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 你可以后面收紧
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- 主题注入 ----------
# Bloomberg Terminal Dark Theme / 统一 UI 风格
inject_theme(app)


# ---------- 核心组件初始化 ----------
intent_engine = IntentEngine()
pipeline_registry = PipelineRegistry()
task_router = TaskRouter(pipeline_registry=pipeline_registry)


# ---------- 请求 / 响应模型 ----------
class UserQuery(BaseModel):
    text: str
    language: str = "zh"  # "zh" / "en"
    session_id: str | None = None


class EntryResponse(BaseModel):
    intent: dict
    route: dict
    result: dict | str


# ---------- 主入口端点 ----------
@app.post("/entry", response_model=EntryResponse)
async def entry_point(query: UserQuery):
    """
    FZQ-AI 智能入口：
    1) 意图识别
    2) 任务路由
    3) Pipeline 执行
    4) 统一返回结构（含元数据）
    """

    # 1) 意图识别
    try:
        intent = intent_engine.detect_intent(
            text=query.text,
            language=query.language,
            session_id=query.session_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IntentEngine error: {e}")

    # 低置信度时可以在这里做澄清（后续你可以扩展）
    if hasattr(intent, "confidence") and intent.confidence < 0.4:
        # 简单示例：返回澄清提示，而不是直接执行
        return EntryResponse(
            intent=intent.to_dict() if hasattr(intent, "to_dict") else dict(intent=intent),
            route={},
            result={
                "type": "clarification",
                "message": "当前意图置信度较低，请补充说明你的需求。",
            },
        )

    # 2) 路由决策
    try:
        route = task_router.route(
            intent=intent,
            language=query.language,
            session_id=query.session_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TaskRouter error: {e}")

    # 3) 执行 pipeline
    try:
        pipeline = route.pipeline
        result = await pipeline.run(
            input_text=query.text,
            intent=intent,
            route=route,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {e}")

    # 4) 统一返回结构
    return EntryResponse(
        intent=intent.to_dict() if hasattr(intent, "to_dict") else dict(intent=intent),
        route=route.to_dict() if hasattr(route, "to_dict") else dict(route=route),
        result=result.to_dict() if hasattr(result, "to_dict") else result,
    )


# ---------- 健康检查 ----------
@app.get("/health")
def health_check():
    return {"status": "ok", "entry_layer": "v15"}
