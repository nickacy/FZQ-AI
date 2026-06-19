"""
FZQ-AI Utils — 并发执行工具
"""
import asyncio
from typing import Any, Callable, Coroutine, List, TypeVar

T = TypeVar("T")


async def run_concurrent(
    tasks: List[Coroutine[Any, Any, T]],
    max_concurrency: int = 10,
) -> List[T]:
    """并发执行多个协程，限制最大并发数"""
    semaphore = asyncio.Semaphore(max_concurrency)

    async def _wrapper(task: Coroutine[Any, Any, T]) -> T:
        async with semaphore:
            return await task

    return await asyncio.gather(*[_wrapper(t) for t in tasks])


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    """在同步上下文中运行异步协程"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    return loop.run_until_complete(coro)
