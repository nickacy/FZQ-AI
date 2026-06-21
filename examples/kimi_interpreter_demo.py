"""
Kimi v9.3 解释层演示脚本

演示如何使用 KimiInterpreter 将格式化 JSON 转化为 7 类自然语言输出。

运行方式：
    python examples/kimi_interpreter_demo.py

输出：
    7 个部分的中文自然语言报告、英文报告、UI 摘要、用户摘要、
    开发者说明、模型协作解释、提示词优化建议。
"""
import asyncio
import json
from pathlib import Path

# 将 src/ 加入路径（演示用，实际项目中通过 conftest.py 或 pip install 配置）
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fzq_ai.interpreter.kimi_interpreter import KimiInterpreter, interpret_json


# 示例输入：来自 Step 4（豆包）的最终格式化 JSON
SAMPLE_INPUT = {
    "facts": {
        "who": ["X国商务部"],
        "what": ["实施出口管制"],
        "when": ["2024-01-15"],
        "where": ["X国"],
        "why": ["国家安全考虑"],
        "how": ["发布出口管制清单，限制特定技术出口"]
    },
    "events": [
        {"step": 1, "action": "发布出口管制清单", "actor": "X国商务部", "target": "Y国企业", "timestamp": "2024-01-15T10:00:00Z"},
        {"step": 2, "action": "Y国企业提出抗议", "actor": "Y国企业协会", "target": "X国商务部", "timestamp": "2024-01-16T14:00:00Z"},
    ],
    "actors": [
        {"name": "X国商务部", "role": "执行方", "position": "政府部门", "actions": ["发布出口管制清单"]},
        {"name": "Y国企业协会", "role": "受影响方", "position": "行业协会", "actions": ["提出抗议"]},
    ],
    "narratives": [],
    "risks": {
        "political": ["摩擦升级"],
        "economic": ["供应链中断", "技术脱钩加速"],
        "security": [],
        "technological": [],
        "social": []
    },
    "policy_signals": ["出口管制"],
    "trend_signals": ["技术脱钩"],
    "raw_quotes": ["X国商务部声明：基于国家安全考虑，对特定技术实施出口管制。"],
    "error_report": []
}


async def main():
    """演示 KimiInterpreter 的 fallback 生成能力。"""
    print("=" * 60)
    print("Kimi v9.3 解释层演示")
    print("=" * 60)
    print()

    # 创建解释器（无 LLM router，使用 fallback 生成）
    interpreter = KimiInterpreter(llm_router=None)

    # 执行解释
    print("输入 JSON：")
    print(json.dumps(SAMPLE_INPUT, ensure_ascii=False, indent=2))
    print()
    print("-" * 60)
    print()

    result = await interpreter.interpret(SAMPLE_INPUT)

    # 输出 7 个部分
    output_lines = []
    sections = [
        ("1. Chinese_Report", result.chinese_report),
        ("2. English_Report", result.english_report),
        ("3. UI_Summary", result.ui_summary),
        ("4. User_Summary", result.user_summary),
        ("5. Developer_Notes", result.developer_notes),
        ("6. Explainability_Layer", result.explainability_layer),
        ("7. Prompt_Optimization", result.prompt_optimization),
    ]

    for title, content in sections:
        output_lines.append(f"\n{'='*60}")
        output_lines.append(f"{title}")
        output_lines.append("=" * 60)
        output_lines.append(content)

    full_output = "\n".join(output_lines)

    # 尝试输出到控制台（Windows 控制台可能不支持 UTF-8）
    try:
        print(full_output)
    except UnicodeEncodeError:
        print("[控制台编码不支持 UTF-8，跳过控制台输出]")

    # 导出为 Markdown 文件
    output_dir = Path(__file__).resolve().parent
    output_path = output_dir / "kimi_interpreter_demo_output.md"
    output_path.write_text(full_output, encoding="utf-8")
    print(f"\n\n输出已保存至：{output_path}")


if __name__ == "__main__":
    asyncio.run(main())
