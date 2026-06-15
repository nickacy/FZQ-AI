# run_agent_demo.py

import os
import yaml

from fzq_ai.agent_hub import AgentHub
from fzq_ai.orchestrator.task_orchestrator import TaskOrchestrator

def load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "fzq_ai", "config", "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":

        "澳洲股市今日上涨 1.2%，科技股领涨。",
        "悉尼房价连续第三个月上涨，需求强劲。",
        "澳洲央行表示将维持利率不变。",
        "全球地缘政治紧张，可能影响大宗商品出口。",
        "本地失业率短期内略有上升迹象。",

    print("=== TaskOrchestrator 测试：每日简报 ===")
    result = orchestrator.run("daily_report", items)
    print(result)

    print("\n=== Metrics 调用统计 ===")
    print(hub.get_metrics())
