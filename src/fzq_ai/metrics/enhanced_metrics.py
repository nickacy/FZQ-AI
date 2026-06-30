"""增强型指标收集系统"""
from __future__ import annotations
import time
import threading
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import asyncio
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

@dataclass
class MetricPoint:
    """指标数据点"""
    name: str
    value: float
    labels: Dict[str, str]
    timestamp: float
    unit: str = ""

@dataclass
class PerformanceMetrics:
    """性能指标"""
    duration_ms: float
    throughput: float
    error_rate: float
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float

class MetricsCollector:
    """增强型指标收集器"""
    
    def __init__(self, retention_minutes: int = 60, max_points: int = 10000):
        self.retention_seconds = retention_minutes * 60
        self.max_points = max_points
        self._metrics: List[MetricPoint] = deque(maxlen=max_points)
        self._lock = threading.Lock()
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = defaultdict(float)
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._timers: Dict[str, List[float]] = defaultdict(list)
        
    def record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None, unit: str = "") -> None:
        """记录指标"""
        with self._lock:
            metric_point = MetricPoint(
                name=name,
                value=value,
                labels=labels or {},
                timestamp=time.time(),
                unit=unit
            )
            self._metrics.append(metric_point)
    
    def increment_counter(self, name: str, amount: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """增加计数器"""
        key = f"{name}_{hash(frozenset((k, v) for k, v in (labels or {}).items()))}"
        with self._lock:
            self._counters[key] += amount
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """设置仪表盘值"""
        key = f"{name}_{hash(frozenset((k, v) for k, v in (labels or {}).items()))}"
        with self._lock:
            self._gauges[key] = value
    
    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """观察直方图值"""
        key = f"{name}_{hash(frozenset((k, v) for k, v in (labels or {}).items()))}"
        with self._lock:
            hist = self._histograms[key]
            hist.append(value)
            if len(hist) > 1000:  # 限制历史数据大小
                hist.pop(0)
    
    def record_timer(self, name: str, duration_ms: float, labels: Optional[Dict[str, str]] = None) -> None:
        """记录计时器"""
        key = f"{name}_{hash(frozenset((k, v) for k, v in (labels or {}).items()))}"
        with self._lock:
            timer = self._timers[key]
            timer.append(duration_ms)
            if len(timer) > 1000:  # 限制历史数据大小
                timer.pop(0)
    
    def start_timer(self) -> float:
        """开始计时"""
        return time.perf_counter()
    
    def stop_timer_and_record(self, start_time: float, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """停止计时并记录"""
        duration_ms = (time.perf_counter() - start_time) * 1000
        self.record_timer(name, duration_ms, labels)
        return duration_ms
    
    def get_counter_value(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """获取计数器值"""
        key = f"{name}_{hash(frozenset((k, v) for k, v in (labels or {}).items()))}"
        return self._counters.get(key, 0.0)
    
    def get_gauge_value(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """获取仪表盘值"""
        key = f"{name}_{hash(frozenset((k, v) for k, v in (labels or {}).items()))}"
        return self._gauges.get(key, 0.0)
    
    def get_histogram_quantile(self, name: str, quantile: float, labels: Optional[Dict[str, str]] = None) -> Optional[float]:
        """获取直方图分位数"""
        key = f"{name}_{hash(frozenset((k, v) for k, v in (labels or {}).items()))}"
        values = sorted(self._histograms.get(key, []))
        if not values:
            return None
        index = int(quantile * len(values))
        return values[min(index, len(values) - 1)]
    
    def get_performance_metrics(self, name: str, labels: Optional[Dict[str, str]] = None) -> Optional[PerformanceMetrics]:
        """获取性能指标"""
        key = f"{name}_{hash(frozenset((k, v) for k, v in (labels or {}).items()))}"
        timers = self._timers.get(key, [])
        
        if not timers:
            return None
        
        sorted_timers = sorted(timers)
        n = len(sorted_timers)
        
        avg_response_time = sum(sorted_timers) / n
        p95_idx = int(0.95 * n)
        p99_idx = int(0.99 * n)
        
        return PerformanceMetrics(
            duration_ms=sum(sorted_timers),
            throughput=n / max(1, self.retention_seconds),  # 次/秒
            error_rate=0.0,  # 这里需要结合错误计数器计算
            avg_response_time=avg_response_time,
            p95_response_time=sorted_timers[min(p95_idx, n - 1)],
            p99_response_time=sorted_timers[min(p99_idx, n - 1)]
        )
    
    def get_recent_metrics(self, minutes: int = 5) -> List[MetricPoint]:
        """获取最近的指标"""
        cutoff_time = time.time() - (minutes * 60)
        with self._lock:
            return [m for m in self._metrics if m.timestamp >= cutoff_time]
    
    def export_to_json(self) -> str:
        """导出指标到JSON"""
        with self._lock:
            data = {
                "metrics": [asdict(m) for m in self._metrics],
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {k: v[-100:] for k, v in self._histograms.items()},  # 只取最新的100个值
                "timers": {k: v[-100:] for k, v in self._timers.items()}  # 只取最新的100个值
            }
            return json.dumps(data, indent=2)
    
    def export_prometheus_format(self) -> str:
        """导出Prometheus格式的指标"""
        output = []
        with self._lock:
            # 导出计数器
            for key, value in self._counters.items():
                output.append(f"# TYPE {key.split('_')[0]} counter")
                output.append(f"{key} {value}")
            
            # 导出仪表盘
            for key, value in self._gauges.items():
                output.append(f"# TYPE {key.split('_')[0]} gauge")
                output.append(f"{key} {value}")
            
            # 导出计时器
            for key, values in self._timers.items():
                if values:
                    avg_val = sum(values) / len(values)
                    output.append(f"# TYPE {key.split('_')[0]} gauge")
                    output.append(f"{key}_avg {avg_val}")
        
        return "\n".join(output)

# 全局指标收集器实例
metrics_collector = MetricsCollector(retention_minutes=120, max_points=20000)

class MetricsMiddleware:
    """指标中间件"""
    
    def __init__(self):
        self.collector = metrics_collector
    
    async def track_request(self, name: str, labels: Optional[Dict[str, str]] = None):
        """跟踪请求性能"""
        start_time = self.collector.start_timer()
        try:
            # 这里应该是实际的请求处理
            pass
        finally:
            duration = self.collector.stop_timer_and_record(start_time, f"{name}_duration", labels)
            self.collector.increment_counter(f"{name}_requests_total", 1, labels)
            if duration > 5000:  # 超过5秒视为慢查询
                self.collector.increment_counter(f"{name}_slow_requests_total", 1, labels)