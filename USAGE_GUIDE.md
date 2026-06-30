# FZQ-AI 使用指南

## 新增功能使用说明

### 1. 现代化配置管理

```python
from fzq_ai.config.modern_config import ConfigManager

# 创建配置管理器实例
config_manager = ConfigManager()

# 获取配置
config = config_manager.get_config()

# 动态更新配置
config_manager.update_config({"param": "value"})
```

### 2. 熔断器模式

```python
from fzq_ai.utils.error_handler import CircuitBreaker

# 创建熔断器
circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)

# 使用熔断器包装操作
try:
    result = circuit_breaker.call(risky_function)
except Exception as e:
    print(f"操作失败: {e}")
```

### 3. 增强型缓存

```python
from fzq_ai.llm.enhanced_cache import EnhancedCache

# 创建缓存实例
cache = EnhancedCache(max_size=1000, default_ttl=3600)

# 异步设置和获取
await cache.set("key", "value")
result = await cache.get("key")

# 使用全局缓存
from fzq_ai.llm.enhanced_cache import llm_response_cache
await llm_response_cache.set("response_key", response_data)
```

### 4. 异步管理器

```python
from fzq_ai.utils.async_manager import AsyncManager

# 创建异步管理器
manager = AsyncManager(max_concurrent=10, timeout=30)

# 运行单个任务
result = await manager.run_task(your_async_function())

# 并发运行多个任务
coroutines = [task1(), task2(), task3()]
results = await manager.run_concurrent(coroutines)
```

### 5. 重试装饰器

```python
from fzq_ai.utils.async_manager import async_retry

@async_retry(max_retries=3, delay=1.0, backoff=2.0)
async def unreliable_function():
    # 可能失败的操作
    pass
```

### 6. 速率限制装饰器

```python
from fzq_ai.utils.async_manager import rate_limit

@rate_limit(calls=10, period=60)  # 1分钟内最多10次调用
async def rate_limited_function():
    # 受有限制的操作
    pass
```

### 7. 指标收集

```python
from fzq_ai.metrics.enhanced_metrics import MetricsCollector

# 创建指标收集器
collector = MetricsCollector()

# 记录指标
collector.record_metric("api_response_time", 150.0, {"endpoint": "/api/data"})

# 记录计数器
collector.increment_counter("request_count", 1, {"method": "GET"})

# 获取最近的指标
recent_metrics = collector.get_recent_metrics(minutes=5)
```

## 最佳实践

### 1. 错误处理
- 使用熔断器防止级联故障
- 实现重试机制以应对临时性错误
- 记录详细的错误信息以便调试

### 2. 性能优化
- 合理使用缓存减少重复计算
- 控制并发数量避免资源耗尽
- 使用异步操作提高吞吐量

### 3. 监控和可观测性
- 记录关键指标以监控系统状态
- 使用分布式追踪跟踪请求流程
- 设置告警以便及时发现问题

### 4. 配置管理
- 将配置与代码分离
- 支持多环境配置
- 实现配置热更新

## 集成示例

```python
import asyncio
from fzq_ai.config.modern_config import ConfigManager
from fzq_ai.utils.async_manager import AsyncManager
from fzq_ai.llm.enhanced_cache import llm_response_cache
from fzq_ai.metrics.enhanced_metrics import MetricsCollector

async def example_usage():
    # 初始化组件
    config = ConfigManager().get_config()
    manager = AsyncManager(max_concurrent=5)
    collector = MetricsCollector()
    
    # 记录开始时间
    start_time = collector.start_timer()
    
    try:
        # 检查缓存
        cached_result = await llm_response_cache.get("query_hash")
        if cached_result:
            return cached_result
        
        # 执行异步操作
        result = await manager.run_task(expensive_operation())
        
        # 缓存结果
        await llm_response_cache.set("query_hash", result, ttl=1800)
        
        # 记录成功指标
        duration = collector.stop_timer_and_record(start_time, "operation_duration")
        collector.increment_counter("operation_success", 1)
        
        return result
    except Exception as e:
        # 记录错误指标
        collector.stop_timer_and_record(start_time, "operation_duration")
        collector.increment_counter("operation_error", 1)
        raise e

# 运行示例
asyncio.run(example_usage())
```

通过遵循这些最佳实践和使用指南，您可以充分利用FZQ-AI框架的增强功能，构建更加稳定和高效的应用程序。