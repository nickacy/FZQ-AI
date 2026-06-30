"""增强型LLM路由器"""
from __future__ import annotations
import asyncio
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import logging

from fzq_ai.llm.enhanced_cache import llm_response_cache
from fzq_ai.utils.async_manager import async_manager, async_retry, rate_limit
from fzq_ai.metrics.enhanced_metrics import metrics_collector
from fzq_ai.utils.error_handler import CircuitBreaker, GracefulErrorHandler

logger = logging.getLogger(__name__)

@dataclass
class ProviderConfig:
    """提供商配置"""
    name: str
    model: str
    api_key: str
    base_url: Optional[str] = None
    timeout: float = 30.0
    max_retries: int = 3
    weight: int = 1  # 权重，用于负载均衡

@dataclass
class RoutingResult:
    """路由结果"""
    success: bool
    provider: str
    model: str
    response: Optional[Dict[str, Any]]
    latency: float
    error: Optional[str] = None

class EnhancedRouter:
    """增强型路由器，支持负载均衡、熔断、缓存等功能"""
    
    def __init__(self, providers: List[ProviderConfig]):
        self.providers = providers
        self.provider_weights = {p.name: p.weight for p in providers}
        self.total_weight = sum(p.weight for p in providers)
        self.current_index = 0  # 用于轮询算法
        
        # 熔断器集合
        self.circuit_breakers = {
            provider.name: CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=60
            ) for provider in providers
        }
        
        # 错误处理器
        self.error_handler = GracefulErrorHandler()
    
    def _weighted_round_robin(self) -> str:
        """加权轮询算法选择提供商"""
        if not self.providers:
            return ""
        
        # 使用加权轮询算法
        target_weight = self.current_index % self.total_weight
        current_weight = 0
        
        for provider in self.providers:
            current_weight += provider.weight
            if current_weight > target_weight:
                self.current_index += 1
                return provider.name
        
        # 如果计算有误，返回第一个
        return self.providers[0].name
    
    def _get_available_providers(self) -> List[str]:
        """获取可用的提供商列表（未熔断的）"""
        available = []
        for name, breaker in self.circuit_breakers.items():
            if breaker.can_execute():
                available.append(name)
        return available
    
    @async_retry(max_retries=3, delay=1.0, backoff=2.0)
    async def _call_provider(self, provider_name: str, req: Dict[str, Any]) -> Dict[str, Any]:
        """调用指定提供商"""
        # 这里应该集成实际的提供商调用逻辑
        # 为了演示，我们模拟调用
        start_time = time.time()
        
        try:
            # 模拟调用提供商
            # 实际实现中这里会调用对应的provider
            result = {
                "output": f"Response from {provider_name}",
                "provider": provider_name,
                "model": req.get("model", "default-model"),
                "timestamp": time.time(),
                "req": req
            }
            
            latency = time.time() - start_time
            metrics_collector.record_llm_call(
                provider=provider_name,
                model=req.get("model", "default-model"),
                latency=latency,
                success=True,
                tokens_used=req.get("tokens", 100)
            )
            
            return result
        except Exception as e:
            latency = time.time() - start_time
            metrics_collector.record_llm_call(
                provider=provider_name,
                model=req.get("model", "default-model"),
                latency=latency,
                success=False,
                error=str(e)
            )
            raise
    
    async def route(self, req: Dict[str, Any]) -> RoutingResult:
        """路由请求到合适的提供商"""
        start_time = time.time()
        available_providers = self._get_available_providers()
        
        if not available_providers:
            return RoutingResult(
                success=False,
                provider="",
                model="",
                response=None,
                latency=time.time() - start_time,
                error="All providers are circuit-breaked"
            )
        
        # 检查缓存
        cache_key = f"llm:{req.get('prompt', '')}:{req.get('model', '')}"
        cached_result = await llm_response_cache.get(cache_key)
        
        if cached_result:
            logger.info(f"Cache hit for request: {cache_key[:50]}...")
            return RoutingResult(
                success=True,
                provider="cache",
                model=cached_result.get("model", ""),
                response=cached_result,
                latency=time.time() - start_time
            )
        
        # 尝试提供商
        for provider_name in available_providers:
            breaker = self.circuit_breakers[provider_name]
            
            if not breaker.can_execute():
                continue
            
            try:
                # 尝试调用提供商
                result = await self._call_provider(provider_name, req)
                
                # 更新熔断器
                breaker.record_success()
                
                # 缓存结果
                await llm_response_cache.set(
                    cache_key, 
                    result, 
                    ttl=req.get("cache_ttl", 1800)  # 默认30分钟
                )
                
                return RoutingResult(
                    success=True,
                    provider=provider_name,
                    model=result.get("model", ""),
                    response=result,
                    latency=time.time() - start_time
                )
                
            except Exception as e:
                # 记录失败
                breaker.record_failure()
                logger.warning(f"Provider {provider_name} failed: {e}")
                
                # 记录错误以便后续分析
                self.error_handler.handle_error(e, context={
                    "provider": provider_name,
                    "request": req
                })
        
        # 所有提供商都失败了
        return RoutingResult(
            success=False,
            provider="",
            model="",
            response=None,
            latency=time.time() - start_time,
            error="All providers failed"
        )
    
    async def health_check(self) -> Dict[str, bool]:
        """健康检查所有提供商"""
        results = {}
        for provider in self.providers:
            try:
                # 这里应该实现实际的健康检查逻辑
                # 为演示，我们简单地检查熔断器状态
                breaker = self.circuit_breakers[provider.name]
                results[provider.name] = breaker.can_execute()
            except Exception as e:
                results[provider.name] = False
                logger.error(f"Health check failed for {provider.name}: {e}")
        
        return results
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取路由器指标"""
        return {
            "total_providers": len(self.providers),
            "available_providers": len(self._get_available_providers()),
            "circuit_breaker_status": {
                name: {
                    "state": "closed" if cb.can_execute() else "open",
                    "failures": cb.failure_count,
                    "last_failure": cb.last_failure_time
                } for name, cb in self.circuit_breakers.items()
            },
            "cache_size": llm_response_cache.size()
        }

# 全局路由器实例
router_instance = None

def get_enhanced_router() -> EnhancedRouter:
    """获取增强路由器实例"""
    global router_instance
    if router_instance is None:
        # 这里应该从配置中读取提供商配置
        # 为演示，我们使用模拟配置
        providers = [
            ProviderConfig(name="deepseek", model="deepseek-chat", api_key="fake-key", weight=3),
            ProviderConfig(name="openai", model="gpt-4", api_key="fake-key", weight=2),
            ProviderConfig(name="gemini", model="gemini-pro", api_key="fake-key", weight=1)
        ]
        router_instance = EnhancedRouter(providers)
    return router_instance