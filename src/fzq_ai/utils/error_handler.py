"""
增强型错误处理和恢复系统
"""
from __future__ import annotations
import asyncio
import logging
import traceback
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union, Awaitable
from functools import wraps
from dataclasses import dataclass, field


@dataclass
class ErrorInfo:
    """错误信息封装"""
    exception: Exception
    traceback_str: str
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryAttempt:
    """恢复尝试记录"""
    attempt_number: int
    error_info: ErrorInfo
    recovered: bool
    recovery_method: str
    duration: float


class CircuitBreaker:
    """熔断器模式实现"""
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self._half_open_attempts = 0
    
    def call(self, func: Callable, *args, **kwargs):
        """调用函数，根据熔断器状态决定是否执行"""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time >= self.timeout:
                self.state = "HALF_OPEN"
                self._half_open_attempts = 0
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e
    
    def on_success(self):
        """调用成功回调"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def on_failure(self):
        """调用失败回调"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class RetryHandler:
    """重试处理器"""
    def __init__(self, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0, 
                 exceptions: Tuple[Type[Exception], ...] = (Exception,)):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff = backoff
        self.exceptions = exceptions
    
    async def execute_async(self, func: Callable[..., Awaitable], *args, **kwargs) -> Any:
        """异步执行带重试"""
        last_exception = None
        delay = self.delay
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except self.exceptions as e:
                last_exception = e
                if attempt < self.max_retries:
                    await asyncio.sleep(delay)
                    delay *= self.backoff
                else:
                    break
        
        raise last_exception
    
    def execute_sync(self, func: Callable, *args, **kwargs) -> Any:
        """同步执行带重试"""
        last_exception = None
        delay = self.delay
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except self.exceptions as e:
                last_exception = e
                if attempt < self.max_retries:
                    time.sleep(delay)
                    delay *= self.backoff
                else:
                    break
        
        raise last_exception


class ErrorHandler:
    """主要错误处理类"""
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.recovery_history: List[RecoveryAttempt] = []
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_handlers: Dict[str, RetryHandler] = {}
    
    def register_circuit_breaker(self, name: str, cb: CircuitBreaker):
        """注册熔断器"""
        self.circuit_breakers[name] = cb
    
    def register_retry_handler(self, name: str, rh: RetryHandler):
        """注册重试处理器"""
        self.retry_handlers[name] = rh
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> ErrorInfo:
        """处理错误并记录信息"""
        error_info = ErrorInfo(
            exception=error,
            traceback_str=traceback.format_exc(),
            context=context or {}
        )
        
        self.logger.error(f"Error occurred: {str(error)}\nContext: {context}\nTraceback: {error_info.traceback_str}")
        return error_info
    
    def attempt_recovery(self, recovery_func: Callable, error_info: ErrorInfo, 
                       method_name: str = "custom") -> RecoveryAttempt:
        """尝试恢复操作"""
        start_time = time.time()
        try:
            recovery_func(error_info)
            recovered = True
        except Exception as e:
            self.logger.error(f"Recovery failed: {str(e)}")
            recovered = False
        
        duration = time.time() - start_time
        attempt = RecoveryAttempt(
            attempt_number=len(self.recovery_history) + 1,
            error_info=error_info,
            recovered=recovered,
            recovery_method=method_name,
            duration=duration
        )
        
        self.recovery_history.append(attempt)
        return attempt
    
    def retry_on_failure(self, max_retries: int = 3, delay: float = 1.0, 
                         backoff: float = 2.0, exceptions: Tuple[Type[Exception], ...] = (Exception,)):
        """装饰器：在函数上添加重试逻辑"""
        def decorator(func):
            if asyncio.iscoroutinefunction(func):
                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    retry_handler = RetryHandler(max_retries, delay, backoff, exceptions)
                    return await retry_handler.execute_async(func, *args, **kwargs)
                return async_wrapper
            else:
                @wraps(func)
                def sync_wrapper(*args, **kwargs):
                    retry_handler = RetryHandler(max_retries, delay, backoff, exceptions)
                    return retry_handler.execute_sync(func, *args, **kwargs)
                return sync_wrapper
        return decorator
    
    def circuit_breaker(self, name: str, failure_threshold: int = 5, timeout: float = 60.0):
        """装饰器：在函数上添加熔断器逻辑"""
        def decorator(func):
            cb = CircuitBreaker(failure_threshold, timeout)
            self.register_circuit_breaker(name, cb)
            
            if asyncio.iscoroutinefunction(func):
                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    return cb.call(lambda: func(*args, **kwargs))
                return async_wrapper
            else:
                @wraps(func)
                def sync_wrapper(*args, **kwargs):
                    return cb.call(lambda: func(*args, **kwargs))
                return sync_wrapper
        return decorator


# 全局错误处理器实例
error_handler = ErrorHandler()


def safe_execute(func: Callable, *args, default_return=None, 
                context: Dict[str, Any] = None, **kwargs) -> Tuple[bool, Any, Optional[Exception]]:
    """
    安全执行函数
    返回: (success, result, exception)
    """
    try:
        if asyncio.iscoroutinefunction(func):
            # 对于异步函数，需要特殊处理
            import asyncio
            if not asyncio.get_event_loop().is_running():
                result = asyncio.run(func(*args, **kwargs))
            else:
                # 在事件循环中，需要创建新任务
                result = asyncio.create_task(func(*args, **kwargs))
        else:
            result = func(*args, **kwargs)
        return True, result, None
    except Exception as e:
        error_info = error_handler.handle_error(e, context)
        error_handler.attempt_recovery(
            lambda ei: logging.warning(f"Failed to execute {func.__name__}: {ei.exception}"), 
            error_info, 
            "safe_execute"
        )
        return False, default_return, e


def get_error_summary() -> Dict[str, Any]:
    """获取错误处理摘要"""
    return {
        "total_recovery_attempts": len(error_handler.recovery_history),
        "successful_recoveries": sum(1 for attempt in error_handler.recovery_history if attempt.recovered),
        "circuit_breakers": {name: cb.state for name, cb in error_handler.circuit_breakers.items()},
        "recent_errors": [
            {
                "attempt": attempt.attempt_number,
                "method": attempt.recovery_method,
                "recovered": attempt.recovered,
                "duration": attempt.duration,
                "error_type": type(attempt.error_info.exception).__name__,
                "timestamp": attempt.error_info.timestamp
            }
            for attempt in error_handler.recovery_history[-10:]  # 最近10次
        ]
    }


# 常用的恢复策略
def basic_recovery(error_info: ErrorInfo):
    """基本恢复策略"""
    # 这里可以根据错误类型实施不同的恢复策略
    if "connection" in str(error_info.exception).lower() or "timeout" in str(error_info.exception).lower():
        # 对于连接相关错误，可能需要清除连接池
        pass
    elif "rate limit" in str(error_info.exception).lower():
        # 对于速率限制错误，需要等待一段时间
        time.sleep(10)
    # 其他类型的错误可以在这里添加处理逻辑


def register_default_recovery_strategies():
    """注册默认恢复策略"""
    # 这里可以注册常用的恢复策略
    pass


# 初始化默认恢复策略
register_default_recovery_strategies()