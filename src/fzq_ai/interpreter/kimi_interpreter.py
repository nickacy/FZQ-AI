"""
FZQ-AI v9.3 · Kimi 文档与提示词优化专家
解释层（Interpretation Layer）

职责：接收来自 Step 4（豆包）的最终格式化 JSON，生成 7 类自然语言输出。

7 个输出部分：
1. Chinese_Report      — 中文自然语言报告
2. English_Report      — 英文自然语言报告
3. UI_Summary          — 卡片式摘要、要点
4. User_Summary        — 面向用户的简短总结
5. Developer_Notes     — 字段解释、结构说明
6. Explainability_Layer — 模型协作解释
7. Prompt_Optimization  — 提示词优化建议

使用示例：
    from fzq_ai.interpreter.kimi_interpreter import KimiInterpreter

    interpreter = KimiInterpreter(llm_router)
    result = await interpreter.interpret(json_data)
    # result.chinese_report
    # result.english_report
    # result.ui_summary
    # ...
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from pathlib import Path

from fzq_ai.schemas import LLMRequest, ModelProvider

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. 输出数据结构（7 个部分）
# ---------------------------------------------------------------------------

@dataclass
class KimiInterpretationResult:
    """Kimi 解释层输出结果。包含 7 个固定部分。"""

    chinese_report: str = ""
    """中文自然语言报告。给用户阅读的完整分析报告。"""

    english_report: str = ""
    """英文自然语言报告。国际化输出。"""

    ui_summary: str = ""
    """UI 展示摘要。卡片式、要点式，可直接用于前端渲染。"""

    user_summary: str = ""
    """用户可读摘要。面向非技术用户的简短总结。"""

    developer_notes: str = ""
    """开发者结构说明。字段解释、结构逻辑、数据来源。"""

    explainability_layer: str = ""
    """模型协作解释。说明数据如何从前序步骤流转到当前状态。"""

    prompt_optimization: str = ""
    """提示词优化建议。基于输入 JSON 结构特征，给出 Prompt 改进建议。"""

    raw_json: Dict[str, Any] = field(default_factory=dict)
    """原始输入 JSON（保留用于溯源）。"""

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典。"""
        return {
            "Chinese_Report": self.chinese_report,
            "English_Report": self.english_report,
            "UI_Summary": self.ui_summary,
            "User_Summary": self.user_summary,
            "Developer_Notes": self.developer_notes,
            "Explainability_Layer": self.explainability_layer,
            "Prompt_Optimization": self.prompt_optimization,
        }

    def to_markdown(self) -> str:
        """输出为 Markdown 文档。"""
        lines = [
            "# FZQ-AI v9.3 解释层报告",
            "",
            "---",
            "",
            "## 1. Chinese_Report",
            self.chinese_report,
            "",
            "---",
            "",
            "## 2. English_Report",
            self.english_report,
            "",
            "---",
            "",
            "## 3. UI_Summary",
            self.ui_summary,
            "",
            "---",
            "",
            "## 4. User_Summary",
            self.user_summary,
            "",
            "---",
            "",
            "## 5. Developer_Notes",
            self.developer_notes,
            "",
            "---",
            "",
            "## 6. Explainability_Layer",
            self.explainability_layer,
            "",
            "---",
            "",
            "## 7. Prompt_Optimization",
            self.prompt_optimization,
            "",
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 2. Kimi 解释器核心
# ---------------------------------------------------------------------------

class KimiInterpreter:
    """Kimi v9.3 文档与提示词优化专家。

    接收来自 Step 4（豆包）的最终格式化 JSON，生成 7 类自然语言输出。

    使用方式：
        interpreter = KimiInterpreter(llm_router)
        result = await interpreter.interpret(json_data)
    """

    SYSTEM_PROMPT_PATH: str = "src/fzq_ai/prompts/system/kimi_v9.3.txt"

    def __init__(self, llm_router: Optional[Any] = None):
        """
        Args:
            llm_router: LLM 路由器的异步调用实例。若 None，使用 fallback 生成器。
        """
        self.llm_router = llm_router
        self._system_prompt: Optional[str] = None

    # -----------------------------------------------------------------------
    # 主入口
    # -----------------------------------------------------------------------
    async def interpret(self, data: Dict[str, Any]) -> KimiInterpretationResult:
        """解释输入 JSON，生成 7 类输出。

        Args:
            data: 来自 Step 4（豆包）的最终格式化 JSON

        Returns:
            KimiInterpretationResult: 包含 7 个部分的解释结果
        """
        result = KimiInterpretationResult(raw_json=data)

        if not data:
            logger.warning("Empty input data, returning empty result")
            return result

        # 加载系统 Prompt
        system_prompt = self._load_system_prompt()

        # 构建用户 Prompt（将 JSON 注入）
        user_prompt = self._build_user_prompt(data)

        # 调用 LLM 生成完整 7 部分输出
        if self.llm_router is not None:
            try:
                generated = await self._generate_with_llm(system_prompt, user_prompt)
                result = self._parse_generated_output(generated, data)
            except Exception as exc:
                logger.warning("LLM generation failed (%s), using fallback", exc)
                result = self._generate_fallback(data)
        else:
            logger.info("No LLM router, using fallback generator")
            result = self._generate_fallback(data)

        return result

    # -----------------------------------------------------------------------
    # 内部方法：加载系统 Prompt
    # -----------------------------------------------------------------------
    def _load_system_prompt(self) -> str:
        """加载系统 Prompt 文件。"""
        if self._system_prompt is not None:
            return self._system_prompt

        try:
            # 尝试从项目根目录读取
            root = Path(__file__).resolve().parents[3]
            path = root / self.SYSTEM_PROMPT_PATH
            if path.exists():
                self._system_prompt = path.read_text(encoding="utf-8")
                return self._system_prompt
        except Exception:
            pass

        # Fallback：使用内置系统 Prompt
        self._system_prompt = self._built_in_system_prompt()
        return self._system_prompt

    @staticmethod
    def _built_in_system_prompt() -> str:
        """内置系统 Prompt（当文件不可读时使用）。"""
        return (
            "你是 FZQ-AI 系统中的文档与提示词优化专家。\n"
            "You are the Documentation & Prompt Optimization Expert in the FZQ-AI system.\n\n"
            "你将接收来自豆包的最终格式化 JSON，包含字段：\n"
            "facts, events, actors, narratives, risks, policy_signals, trend_signals, raw_quotes, error_report\n\n"
            "核心任务：基于该 JSON 生成 7 种自然语言内容：\n"
            "1. Chinese_Report — 中文自然语言报告\n"
            "2. English_Report — 英文自然语言报告\n"
            "3. UI_Summary — 卡片式摘要、要点\n"
            "4. User_Summary — 面向用户的简短总结\n"
            "5. Developer_Notes — 字段解释、结构说明\n"
            "6. Explainability_Layer — 模型协作解释\n"
            "7. Prompt_Optimization — 提示词优化建议\n\n"
            "强制规则：\n"
            "1. 不得新增、修改或推测事实。\n"
            "2. 所有内容必须严格基于 JSON 中已有信息。\n"
            "3. 中文与英文版本必须语义一致。\n"
            "4. UI 文本必须简洁、结构化、可直接用于前端。\n"
            "5. Developer Notes 必须解释字段含义、结构逻辑、数据来源。\n"
            "6. Prompt Optimization 必须基于输入 JSON 的结构特征。\n"
            "7. 输出必须是纯文本，不包含 Markdown 代码块。\n"
        )

    # -----------------------------------------------------------------------
    # 内部方法：构建用户 Prompt
    # -----------------------------------------------------------------------
    def _build_user_prompt(self, data: Dict[str, Any]) -> str:
        """将 JSON 数据构建为 LLM 用户 Prompt。"""
        json_text = json.dumps(data, ensure_ascii=False, indent=2)
        return f"""【输入 JSON】
{json_text}

请基于上述 JSON 生成 7 个部分的自然语言输出，按以下固定格式：

1. Chinese_Report
2. English_Report
3. UI_Summary
4. User_Summary
5. Developer_Notes
6. Explainability_Layer
7. Prompt_Optimization

每部分必须有明确的标题行，内容必须基于 JSON 中已有信息，不得新增或修改事实。"""

    # -----------------------------------------------------------------------
    # 内部方法：LLM 调用
    # -----------------------------------------------------------------------
    async def _generate_with_llm(self, system_prompt: str, user_prompt: str) -> str:
        """通过 LLM 路由器生成 7 部分输出。"""
        if self.llm_router is None:
            raise RuntimeError("LLM router not available")

        request = LLMRequest(
            prompt=user_prompt,
            system_prompt=system_prompt,
            provider=ModelProvider.KIMI,  # Kimi 最适合长文本生成
            temperature=0.3,  # 较低温度，减少自由发挥
            max_tokens=4096,
        )

        resp = await self.llm_router.generate(request)
        return resp.content

    # -----------------------------------------------------------------------
    # 内部方法：解析 LLM 输出
    # -----------------------------------------------------------------------
    def _parse_generated_output(
        self, generated: str, raw_data: Dict[str, Any]
    ) -> KimiInterpretationResult:
        """解析 LLM 生成的 7 部分输出。"""
        result = KimiInterpretationResult(raw_json=raw_data)

        sections = {
            "Chinese_Report": "chinese_report",
            "English_Report": "english_report",
            "UI_Summary": "ui_summary",
            "User_Summary": "user_summary",
            "Developer_Notes": "developer_notes",
            "Explainability_Layer": "explainability_layer",
            "Prompt_Optimization": "prompt_optimization",
        }

        # 按标题分割文本
        current_section = None
        current_content = []

        for line in generated.splitlines():
            stripped = line.strip()
            # 检测标题行（支持多种格式："1. Chinese_Report" 或 "Chinese_Report" 或 "## Chinese_Report"）
            for title, attr in sections.items():
                if stripped.startswith(title) or stripped.endswith(title):
                    # 保存上一个 section
                    if current_section and current_content:
                        content = "\n".join(current_content).strip()
                        setattr(result, current_section, content)
                    current_section = attr
                    current_content = []
                    break
            else:
                if current_section is not None:
                    current_content.append(line)

        # 保存最后一个 section
        if current_section and current_content:
            content = "\n".join(current_content).strip()
            setattr(result, current_section, content)

        # 如果解析失败，使用 fallback
        if not result.chinese_report and not result.english_report:
            logger.warning("Failed to parse LLM output, using fallback")
            return self._generate_fallback(raw_data)

        return result

    # -----------------------------------------------------------------------
    # 内部方法：Fallback 生成器（无 LLM 时）
    # -----------------------------------------------------------------------
    def _generate_fallback(self, data: Dict[str, Any]) -> KimiInterpretationResult:
        """当 LLM 不可用时，使用模板生成基础输出。"""
        result = KimiInterpretationResult(raw_json=data)

        # 提取关键信息
        facts = data.get("facts", {})
        events = data.get("events", [])
        actors = data.get("actors", [])
        risks = data.get("risks", {})
        policy_signals = data.get("policy_signals", [])
        trend_signals = data.get("trend_signals", [])
        raw_quotes = data.get("raw_quotes", [])
        error_report = data.get("error_report", [])

        # 1. Chinese_Report
        result.chinese_report = self._generate_chinese_report(
            facts, events, actors, risks, policy_signals, trend_signals, raw_quotes
        )

        # 2. English_Report
        result.english_report = self._generate_english_report(
            facts, events, actors, risks, policy_signals, trend_signals, raw_quotes
        )

        # 3. UI_Summary
        result.ui_summary = self._generate_ui_summary(
            facts, events, risks, policy_signals, trend_signals
        )

        # 4. User_Summary
        result.user_summary = self._generate_user_summary(
            facts, events, risks, policy_signals
        )

        # 5. Developer_Notes
        result.developer_notes = self._generate_developer_notes(data)

        # 6. Explainability_Layer
        result.explainability_layer = self._generate_explainability_layer(
            facts, events, actors, risks, error_report
        )

        # 7. Prompt_Optimization
        result.prompt_optimization = self._generate_prompt_optimization(data)

        return result

    # -----------------------------------------------------------------------
    # Fallback 生成器：各部分的模板生成
    # -----------------------------------------------------------------------
    def _generate_chinese_report(
        self, facts, events, actors, risks, policy_signals, trend_signals, raw_quotes
    ) -> str:
        lines = []
        who = ", ".join(facts.get("who", [])) or "未明确"
        what = ", ".join(facts.get("what", [])) or "未明确"
        when = ", ".join(facts.get("when", [])) or "未明确"
        where = ", ".join(facts.get("where", [])) or "未明确"
        why = ", ".join(facts.get("why", [])) or "未明确"
        how = ", ".join(facts.get("how", [])) or "未明确"

        lines.append(f"事件概述：{who} {what}。")
        if when != "未明确":
            lines.append(f"时间：{when}。")
        if where != "未明确":
            lines.append(f"地点：{where}。")
        if why != "未明确":
            lines.append(f"原因：{why}。")
        if how != "未明确":
            lines.append(f"方式：{how}。")

        if events:
            lines.append("\n事件进展：")
            for e in events:
                action = e.get("action", "")
                actor = e.get("actor", "")
                if action:
                    lines.append(f"- {actor or '相关方'} {action}")

        if actors:
            lines.append("\n主要参与者：")
            for a in actors:
                name = a.get("name", "")
                role = a.get("role", "")
                if name:
                    lines.append(f"- {name} ({role or '角色未明确'})")

        risk_parts = []
        for cat, items in risks.items():
            if items:
                risk_parts.append(f"{cat}风险：{', '.join(items)}")
        if risk_parts:
            lines.append("\n风险分析：")
            for rp in risk_parts:
                lines.append(f"- {rp}")

        if policy_signals:
            lines.append(f"\n政策信号：{', '.join(policy_signals)}")
        if trend_signals:
            lines.append(f"趋势信号：{', '.join(trend_signals)}")

        if raw_quotes:
            lines.append("\n原文引用：")
            for q in raw_quotes:
                lines.append(f"- {q}")

        return "\n".join(lines)

    def _generate_english_report(
        self, facts, events, actors, risks, policy_signals, trend_signals, raw_quotes
    ) -> str:
        # 基于中文报告生成英文版（简化版，实际应由 LLM 翻译）
        who = ", ".join(facts.get("who", [])) or "Not specified"
        what = ", ".join(facts.get("what", [])) or "Not specified"
        when = ", ".join(facts.get("when", [])) or "Not specified"
        where = ", ".join(facts.get("where", [])) or "Not specified"

        lines = [f"Event Overview: {who} {what}."]
        if when != "Not specified":
            lines.append(f"Time: {when}.")
        if where != "Not specified":
            lines.append(f"Location: {where}.")

        if events:
            lines.append("\nEvent Progression:")
            for e in events:
                action = e.get("action", "")
                actor = e.get("actor", "")
                if action:
                    lines.append(f"- {actor or 'Related party'} {action}")

        if actors:
            lines.append("\nKey Actors:")
            for a in actors:
                name = a.get("name", "")
                role = a.get("role", "")
                if name:
                    lines.append(f"- {name} ({role or 'Role unspecified'})")

        risk_parts = []
        for cat, items in risks.items():
            if items:
                risk_parts.append(f"{cat} risk: {', '.join(items)}")
        if risk_parts:
            lines.append("\nRisk Analysis:")
            for rp in risk_parts:
                lines.append(f"- {rp}")

        if policy_signals:
            lines.append(f"\nPolicy Signals: {', '.join(policy_signals)}")
        if trend_signals:
            lines.append(f"Trend Signals: {', '.join(trend_signals)}")

        return "\n".join(lines)

    def _generate_ui_summary(self, facts, events, risks, policy_signals, trend_signals) -> str:
        lines = []
        what = ", ".join(facts.get("what", [])) or "—"
        lines.append(f"• 事件：{what}")

        if events:
            lines.append(f"• 进展：{len(events)} 个关键节点")

        risk_count = sum(len(v) for v in risks.values() if isinstance(v, list))
        if risk_count > 0:
            lines.append(f"• 风险：{risk_count} 项已识别")

        if policy_signals:
            lines.append(f"• 政策：{', '.join(policy_signals[:2])}")
        if trend_signals:
            lines.append(f"• 趋势：{', '.join(trend_signals[:2])}")

        return "\n".join(lines)

    def _generate_user_summary(self, facts, events, risks, policy_signals) -> str:
        what = ", ".join(facts.get("what", [])) or "相关事件"
        who = ", ".join(facts.get("who", [])) or "相关方"

        risk_count = sum(len(v) for v in risks.values() if isinstance(v, list))
        risk_text = f"已识别 {risk_count} 项风险" if risk_count > 0 else "暂未识别明确风险"

        policy_text = ""
        if policy_signals:
            policy_text = f"涉及政策信号：{', '.join(policy_signals[:2])}"

        return f"这是关于 {who} {what} 的分析。{risk_text}。{policy_text}"

    def _generate_developer_notes(self, data: Dict[str, Any]) -> str:
        lines = [
            "【数据结构说明】",
            "",
            "facts: 5W1H 事实提取",
            "- who: 涉事主体（字符串数组）",
            "- what: 核心动作（字符串数组）",
            "- when: 时间信息（字符串数组）",
            "- where: 地点信息（字符串数组）",
            "- why: 原因/动机（字符串数组）",
            "- how: 方式/过程（字符串数组）",
            "",
            "events: 事件时间线（对象数组）",
            "- step: 序号（整数）",
            "- action: 动作（字符串）",
            "- actor: 执行者（字符串）",
            "- target: 目标（字符串）",
            "- timestamp: 时间戳（字符串）",
            "",
            "actors: 参与者列表（对象数组）",
            "- name: 名称（字符串）",
            "- role: 角色（字符串）",
            "- position: 职位/身份（字符串）",
            "- actions: 已执行动作（字符串数组）",
            "",
            "risks: 风险分类（对象）",
            "- political: 政治风险（字符串数组）",
            "- economic: 经济风险（字符串数组）",
            "- security: 安全风险（字符串数组）",
            "- technological: 技术风险（字符串数组）",
            "- social: 社会风险（字符串数组）",
            "",
            "policy_signals: 政策信号（字符串数组）",
            "trend_signals: 趋势信号（字符串数组）",
            "raw_quotes: 原文引用（字符串数组）",
            "error_report: 错误报告（字符串数组）",
        ]
        return "\n".join(lines)

    def _generate_explainability_layer(
        self, facts, events, actors, risks, error_report
    ) -> str:
        lines = [
            "【模型协作解释】",
            "",
            "数据流：GLM-5.2 → DeepSeek → Minimax → 豆包 → Kimi",
            "",
            "1. GLM-5.2（原始提取）：",
            "   - 从原始文本中提取 5W1H 事实骨架",
            f"   - 提取 who: {len(facts.get('who', []))} 个主体",
            f"   - 提取 what: {len(facts.get('what', []))} 个动作",
            "",
            "2. DeepSeek（结构化）：",
            f"   - 构建事件时间线：{len(events)} 个节点",
            f"   - 识别参与者：{len(actors)} 个主体",
            "   - 分析风险分类",
            "",
            "3. Minimax（校验）：",
            "   - Schema 验证",
            "   - 字段补全",
            "   - 枚举修正",
            "",
            "4. 豆包（格式化）：",
            "   - 输出标准化 JSON",
            "   - 错误汇总",
            "",
            "5. Kimi（解释层）：",
            "   - 生成自然语言报告",
            "   - 提供 UI 摘要",
            "   - 输出开发者文档",
        ]

        if error_report:
            lines.append("\n【处理过程中的异常】")
            for err in error_report:
                lines.append(f"- {err}")

        return "\n".join(lines)

    def _generate_prompt_optimization(self, data: Dict[str, Any]) -> str:
        lines = [
            "【提示词优化建议】",
            "",
            "基于输入 JSON 的结构特征，给出以下优化建议：",
            "",
        ]

        facts = data.get("facts", {})
        events = data.get("events", [])
        actors = data.get("actors", [])
        risks = data.get("risks", {})
        error_report = data.get("error_report", [])

        # 根据数据结构特征给出建议
        if not facts.get("who"):
            lines.append("1. 事实提取阶段：")
            lines.append("   - 建议在未来 Prompt 中增加 '识别所有涉事主体' 的明确要求")
            lines.append("   - 当前 who 字段为空，可能导致分析报告主体缺失")
            lines.append("")

        if not facts.get("why"):
            lines.append("2. 因果分析阶段：")
            lines.append("   - 建议增加 '分析事件原因与动机' 的专项指令")
            lines.append("   - 当前 why 字段为空，可能影响深度分析")
            lines.append("")

        if not events:
            lines.append("3. 时间线构建阶段：")
            lines.append("   - 建议增加 '按时间顺序排列事件' 的明确要求")
            lines.append("   - 当前 events 为空，无法生成时间线分析")
            lines.append("")

        if not actors:
            lines.append("4. 参与者识别阶段：")
            lines.append("   - 建议增加 '识别所有参与者及其角色' 的明确要求")
            lines.append("   - 当前 actors 为空，影响主体分析深度")
            lines.append("")

        risk_count = sum(len(v) for v in risks.values() if isinstance(v, list))
        if risk_count == 0:
            lines.append("5. 风险评估阶段：")
            lines.append("   - 建议增加 '识别多维度风险' 的明确要求（政治/经济/安全/技术/社会）")
            lines.append("   - 当前 risks 全为空，可能遗漏风险信号")
            lines.append("")

        if error_report:
            lines.append(f"6. 错误处理：")
            lines.append(f"   - 当前处理过程中出现 {len(error_report)} 个异常")
            lines.append("   - 建议增加输入校验和降级处理机制")
            lines.append("")

        lines.append("7. 通用建议：")
        lines.append("   - 建议在所有阶段增加 '证据溯源' 要求，确保每个结论都有原文支撑")
        lines.append("   - 建议在输出中增加 '置信度' 字段，标注分析可靠性")
        lines.append("   - 建议增加 '缺失信息说明'，明确标注哪些维度无法从输入中提取")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 3. 便捷函数
# ---------------------------------------------------------------------------

async def interpret_json(data: Dict[str, Any], llm_router=None) -> KimiInterpretationResult:
    """便捷函数：解释 JSON 数据。"""
    interpreter = KimiInterpreter(llm_router=llm_router)
    return await interpreter.interpret(data)
