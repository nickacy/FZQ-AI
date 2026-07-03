"""V24 — zh_risk_scan pipeline (refactored to use ZhStructuredPipeline)."""
from fzq_ai.pipelines._zh_pipeline import ZhStructuredPipeline


class ZhRiskScanPipeline(ZhStructuredPipeline):
    task_type = "zh_risk_scan"
    prompt_path = "zh/zh_risk_scan.txt"


# Registry alias
ZhRiskScan = ZhRiskScanPipeline
