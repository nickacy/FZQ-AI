# src/fzq_ai/utils/monitoring.py
# V24-Final — Prometheus-compatible monitoring (optional prometheus_client)
"""
Unified monitoring for FZQ-AI V24.

Always works (in-memory metrics).  When prometheus_client is installed,
exposes full Prometheus metrics at /metrics.

Metrics:
  fzq_api_requests_total{endpoint}
  fzq_api_latency_seconds{endpoint}
  fzq_pipeline_latency_seconds{pipeline}
  fzq_pipeline_errors_total{pipeline}
  fzq_agent_latency_seconds{agent}
  fzq_agent_errors_total{agent}
  fzq_llm_latency_seconds{model}
  fzq_llm_errors_total{model}
  fzq_cpu_usage
  fzq_memory_usage
"""
from __future__ import annotations
import time
import threading
from contextlib import contextmanager
from typing import Dict, List

# ── Optional Prometheus ───────────────────────────────────────

_PROM_AVAILABLE = False
try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
    _PROM_AVAILABLE = True
except ImportError:
    Counter = Histogram = Gauge = None  # type: ignore
    generate_latest = None
    REGISTRY = None


# ── In-memory fallback ────────────────────────────────────────

class _InMemoryMetric:
    def __init__(self):
        self._lock = threading.Lock()
        self._values: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = {}

    def inc(self, labels: tuple = (), value: float = 1.0):
        key = str(labels)
        with self._lock:
            self._values[key] = self._values.get(key, 0) + value

    def observe(self, value: float, labels: tuple = ()):
        key = str(labels)
        with self._lock:
            if key not in self._histograms:
                self._histograms[key] = []
            self._histograms[key].append(value)

    def set(self, value: float):
        with self._lock:
            self._values["__gauge__"] = value

    def time(self, labels: tuple = ()):
        return _InMemoryTimer(self, labels)


class _InMemoryTimer:
    def __init__(self, metric: _InMemoryMetric, labels: tuple):
        self._metric = metric
        self._labels = labels
        self._start: float = 0.0

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self._metric.observe((time.perf_counter() - self._start) * 1000, self._labels)


# ── Metric definitions ─────────────────────────────────────────

def _make(name: str, desc: str, labelnames: list, cls: str = "counter"):
    """Create a metric — Prometheus when available, in-memory otherwise."""
    if _PROM_AVAILABLE:
        if cls == "histogram":
            return Histogram(name, desc, labelnames=labelnames)
        elif cls == "gauge":
            return Gauge(name, desc)
        else:
            return Counter(name, desc, labelnames=labelnames)
    return _InMemoryMetric()


# API
api_requests = _make("fzq_api_requests_total", "Total API requests", ["endpoint"])
api_latency = _make("fzq_api_latency_seconds", "API latency (ms)", ["endpoint"], "histogram")
api_errors = _make("fzq_api_errors_total", "API errors", ["endpoint"])

# Pipeline
pipeline_latency = _make("fzq_pipeline_latency_seconds", "Pipeline latency (ms)", ["pipeline"], "histogram")
pipeline_errors = _make("fzq_pipeline_errors_total", "Pipeline errors", ["pipeline"])

# Agent
agent_latency = _make("fzq_agent_latency_seconds", "Agent latency (ms)", ["agent"], "histogram")
agent_errors = _make("fzq_agent_errors_total", "Agent errors", ["agent"])

# LLM
llm_latency = _make("fzq_llm_latency_seconds", "LLM latency (ms)", ["model"], "histogram")
llm_errors = _make("fzq_llm_errors_total", "LLM errors", ["model"])

# System
cpu_usage = _make("fzq_cpu_usage", "CPU usage %", [], "gauge")
memory_usage = _make("fzq_memory_usage", "Memory usage %", [], "gauge")


# ── Context managers ──────────────────────────────────────────

@contextmanager
def api_monitor(endpoint: str):
    """Wrap an API handler with metrics."""
    api_requests.inc(labels=(endpoint,))
    t0 = time.perf_counter()
    try:
        yield
    except Exception:
        api_errors.inc(labels=(endpoint,))
        raise
    finally:
        api_latency.observe((time.perf_counter() - t0) * 1000, (endpoint,))


@contextmanager
def pipeline_monitor(pipeline_name: str):
    """Wrap pipeline execution with metrics."""
    t0 = time.perf_counter()
    try:
        yield
    except Exception:
        pipeline_errors.inc(labels=(pipeline_name,))
        raise
    finally:
        pipeline_latency.observe((time.perf_counter() - t0) * 1000, (pipeline_name,))


@contextmanager
def agent_monitor(agent_name: str):
    """Wrap agent execution with metrics."""
    t0 = time.perf_counter()
    try:
        yield
    except Exception:
        agent_errors.inc(labels=(agent_name,))
        raise
    finally:
        agent_latency.observe((time.perf_counter() - t0) * 1000, (agent_name,))


@contextmanager
def llm_monitor(model: str):
    """Wrap LLM call with metrics."""
    t0 = time.perf_counter()
    try:
        yield
    except Exception:
        llm_errors.inc(labels=(model,))
        raise
    finally:
        llm_latency.observe((time.perf_counter() - t0) * 1000, (model,))


# ── System metrics ────────────────────────────────────────────

def update_system_metrics():
    """Update CPU and memory gauges."""
    try:
        import psutil
        cpu_usage.set(psutil.cpu_percent(interval=0.1))
        memory_usage.set(psutil.virtual_memory().percent)
    except ImportError:
        pass  # psutil not installed


# ── Prometheus endpoint ───────────────────────────────────────

def get_metrics_response() -> str:
    """Return Prometheus text format.  Falls back to JSON summary."""
    if _PROM_AVAILABLE and generate_latest:
        return generate_latest(REGISTRY).decode("utf-8")  # type: ignore[union-attr]
    return '{"status": "ok", "message": "prometheus_client not installed. Install: pip install prometheus_client"}'
