# src/fzq_ai/pipelines/base.py
# v13 BasePipeline – 所有 Pipeline 的统一基类

from __future__ import annotations
from typing import Any, Dict


class BasePipeline:
    """
    v13 Pipeline 统一接口
    - preprocess：请求预处理
    - postprocess：结果后处理
    - name：pipeline 名称（用于 metrics）
    """

    name: str = "base"

    async def preprocess(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """
        子类可重写：
        - 添加 task_type
        - 添加 prompt 模板
        - 添加上下文
        """
        return req

    async def postprocess(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        子类可重写：
        - 清洗输出
        - 结构化结果
        - 错误处理
        """
        return result
