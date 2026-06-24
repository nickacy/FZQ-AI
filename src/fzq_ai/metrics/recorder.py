# src/fzq_ai/metrics/recorder.py

from fzq_ai.metrics.metrics_v2 import metrics_v2

class MetricsRecorder:
    """
    记录模型调用的指标。
    """

    def record(self, provider, success, latency_ms, tokens, error=None):
        metrics_v2.record(provider, success, latency_ms, tokens, error)
