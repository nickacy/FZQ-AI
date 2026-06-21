# fzq_ai/schemas/llm.py

from pydantic import BaseModel


class LLMRequestSchema(BaseModel):
    """LLM 输入请求结构"""
    prompt: str


class LLMResponseSchema(BaseModel):
    """LLM 输出响应结构"""
    content: str
