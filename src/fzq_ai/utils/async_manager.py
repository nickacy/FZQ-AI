"""增强型异步管理器"""
from __future__ import annotations
import asyncio
import functools
import time
from typing import Any, Callable, Coroutine, Optional, Dict
from dataclasses import dataclass
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

@dataclass
class TaskStats:
    """任务统计信息"""
    task_id: str
    start_time: float
    end_time: Optional[float] = None
    success: Optional[bool] = None
    error: Optional[str] = None

class AsyncManager:
    """增强型异步任务管理器"""
    
    def __init__(self, max_concurrent: int = 10, timeout: float = 30.0):
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.stats: Dict[str, TaskStats] = {}
        self._task_counter = 0
    
    async def _run_with_semaphore(self, task_id: str, coro: Coroutine) -> Any:
        """使用信号量运行协程"""
        async with self.semaphore:
            start_time = time.time()
            self.stats[task_id] = TaskStats(task_id=task_id, start_time=start_time)
            
            try:
                result = await coro
                self.stats[task_id].end_time = time.time()
                self.stats[task_id].success = True
                return result
            except Exception as e:
                self.stats[task_id].end_time = time.time()
                self.stats[task_id].success = False
                self.stats[task_id].error = str(e)
                raise
            finally:
                if task_id in self.active_tasks:
                    del self.active_tasks[task_id]
    
    async def run_task(self, coro: Coroutine, task_name: Optional[str] = None) -> Any:
        """运行单个任务"""
        self._task_counter += 1
        task_id = task_name or f"task_{self._task_counter}"
        
        task = asyncio.create_task(
            self._run_with_semaphore(task_id, coro),
            name=task_id
        )
        self.active_tasks[task_id] = task
        
        try:
            result = await asyncio.wait_for(task, timeout=self.timeout)
            return result
        except asyncio.TimeoutError:
            task.cancel()
            raise TimeoutError(f"Task {task_id} exceeded timeout of {self.timeout}s")
    
    async def run_concurrent(self, coroutines: list[Coroutine], batch_size: Optional[int] = None) -> list[Any]:
        """并发运行多个任务"""
        batch_size = batch_size or self.max_concurrent
        results = []
        
        for i in range(0, len(coroutines), batch_size):
            batch = coroutines[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[self.run_task(coro) for coro in batch],
                return_exceptions=True
            )
            results.extend(batch_results)
        
        return results
    
    @asynccontextmanager
    async def task_group(self, max_concurrent: Optional[int] = None):
        """异步任务组上下文管理器"""
        old_semaphore = self.semaphore
        if max_concurrent is not None:
            self.semaphore = asyncio.Semaphore(max_concurrent)
        
        try:
            yield self
        finally:
            self.semaphore = old_semaphore
    
    def get_active_tasks(self) -> list[str]:
        """获取活跃任务列表"""
        return list(self.active_tasks.keys())
    
    def get_stats(self, task_id: Optional[str] = None) -> Dict[str, TaskStats] | TaskStats:
        """获取任务统计信息"""
        if task_id:
            return self.stats.get(task_id)
        return self.stats.copy()
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消指定任务"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                return True
        return False
    
    async def cancel_all(self) -> None:
        """取消所有活跃任务"""
        for task_id in list(self.active_tasks.keys()):
            await self.cancel_task(task_id)

# 全局异步管理器实例
async_manager = AsyncManager(max_concurrent=20, timeout=60.0)

def async_retry(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """异步重试装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            retries = 0
            current_delay = delay
            
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {e}")
                        raise
                    
                    logger.warning(f"Function {func.__name__} attempt {retries} failed: {e}. Retrying in {current_delay}s...")
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            
            raise Exception(f"Failed after {max_retries} retries")
        return wrapper
    return decorator

def rate_limit(calls: int, period: float):
    """速率限制装饰器"""
    def decorator(func: Callable) -> Callable:
        calls_made = []
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            nonlocal calls_made
            now = time.time()
            
            # 清理过期的调用记录
            calls_made = [call_time for call_time in calls_made if now - call_time < period]
            
            if len(calls_made) >= calls:
                sleep_time = period - (now - min(calls_made))
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
            
            calls_made.append(now)
            return await func(*args, **kwargs)
        return wrapper
    return decorator