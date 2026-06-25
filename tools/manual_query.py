# tools/manual_query.py

import json
from fzq_ai.llm.orchestrator.orchestrator import TaskOrchestrator
from fzq_ai.schemas.pipeline_input import PipelineInput


def pretty_print(title, content):
    print(f"\n===== {title} =====")
    if isinstance(content, (dict, list)):
        print(json.dumps(content, indent=2, ensure_ascii=False))
    else:
        print(content)


def main():
    # 你可以随时修改这里的问题，作为 FZQ-AI 的测试输入
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
        task_type="daily_report",  # 你也可以改 narrative / risk / merge 等
    )

    print("\n=== 🚀 FZQ-AI 调试控制台启动 ===")

    # 运行 orchestrator
    result = orchestrator.run(req)

    # 输出：最终结果
    pretty_print("📝 最终输出（Pipeline Output）", result.output)

    # 输出：模型使用情况
    if hasattr(result, "model_used"):
        pretty_print("🤖 使用的模型（model_used）", result.model_used)

    # 输出：元数据
    if hasattr(result, "metadata"):
        pretty_print("📦 元数据（metadata）", result.metadata)

    # 输出：恢复链路（如果有）
    if hasattr(result, "recovery_trace"):
        pretty_print("🛠 恢复链路（Recovery Trace）", result.recovery_trace)

    # 输出：自愈日志（如果有）
    if hasattr(result, "repair_log"):
        pretty_print("🔧 自愈日志（Repair Log）", result.repair_log)

    print("\n=== 🎉 调试完成 ===\n")


if __name__ == "__main__":
    main()
