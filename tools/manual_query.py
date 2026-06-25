# tools/manual_query.py

from fzq_ai.llm.orchestrator.orchestrator import TaskOrchestrator
from fzq_ai.schemas.pipeline import PipelineInput


def main():
    question = (
        "2026年足球世界杯的冠军可能是哪个球队？"
        "其他前三名的球队可能是谁？"
        "大概的可能性百分比是多少？"
        "中国大概哪一年有可能举办世界杯？"
    )

    orchestrator = TaskOrchestrator()

    req = PipelineInput(
        query=question,
        target_language="zh",
        task_type="daily_report",  # 或你想测试的 pipeline 类型
    )

    result = orchestrator.run(req)
    print("\n=== FZQ-AI 输出 ===\n")
    print(result.output)

if __name__ == "__main__":
    main()
