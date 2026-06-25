# tools/manual_query.py

from fzq_ai.orchestrator.task_orchestrator import TaskOrchestrator
from fzq_ai.schemas.pipeline_input import PipelineInput


def main():
    question = (
        "2026年足球世界杯的冠军可能是哪支球队？"
        "其他前三名的球队可能是谁？"
        "大概率的可能性有多高？"
        "中国大概哪一年有可能举办世界杯？"
    )

    orchestrator = TaskOrchestrator()

    req = PipelineInput(
        query=question,
        target_language="zh",
        task_type="daily_report",
    )

    result = orchestrator.run(req)

    print("\n=== FZQ-AI 输出 ===\n")
    print(result.output)


if __name__ == "__main__":
    main()
