"""
fzq_ai.domain.errors

统一异常体系：
- FZQAIError 基类（所有领域异常的根）
- LLMError：大模型调用相关错误
- ToolExecutionError：工具执行失败
- NewsFetchError：新闻抓取失败
- PipelineError：Pipeline 执行失败
- ServiceError：服务层错误（可选扩展）
"""

from __future__ import annotations


class FZQAIError(Exception):
    """
    FZQ-AI 系统内的基础异常类型。

    特点：
    - 所有自定义异常继承自此类
    - 内置 error_code，便于 ServiceResult 映射
    - message 为人类可读错误信息
    """

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


class LLMError(FZQAIError):
    """LLM 调用相关异常（如超时、限流、模型不可用）"""

    pass


class ToolExecutionError(FZQAIError):
    """工具执行相关异常（如参数错误、外部 API 失败）"""

    pass


class NewsFetchError(FZQAIError):
    """新闻抓取相关异常（如网络错误、数据源不可用）"""

    pass


class PipelineError(FZQAIError):
    """Pipeline 执行相关异常（如数据格式错误、步骤失败）"""

    pass


class ServiceError(FZQAIError):
    """服务层异常（如 orchestrator 逻辑错误）"""

    pass
