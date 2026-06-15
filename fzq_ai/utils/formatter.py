class NewsFormatter:
    @staticmethod
    def format(raw: str) -> str:
        """
        输入：LLM 输出的新闻摘要文本
        输出：格式化后的 Markdown 文本
        """
        return f"### 📰 新闻摘要\n\n{raw.strip()}"


class NarrativeFormatter:
    @staticmethod
    def format(raw: str) -> str:
        """
        输入：LLM 输出的叙事分析文本
        输出：格式化后的 Markdown 文本
        """
        return f"### 📚 叙事分析\n\n{raw.strip()}"


class RiskFormatter:
    @staticmethod
    def format(raw: str) -> dict:
        """
        输入：LLM 输出的风险扫描文本（通常是 JSON 风格）
        输出：结构化 dict（如果解析失败则返回原始文本）
        """
        try:
            import json

            data = json.loads(raw)
            return data
        except Exception:
            return {"summary": "LLM 输出非 JSON 格式，已返回原始文本", "raw": raw}


class DailyReportFormatter:
    @staticmethod
    def format(news_summary: str, narrative: dict, risk: dict) -> str:
        """
        生成最终日报 Markdown 文本
        """
        narrative_text = narrative if isinstance(narrative, str) else str(narrative)

        risk_text = risk if isinstance(risk, str) else str(risk)

        return f"""
# 📅 每日简报（Daily Report）

---

## 📰 新闻摘要
{news_summary}

---

## 📚 叙事分析
{narrative_text}

---

## ⚠️ 风险扫描
{risk_text}

---

*由 FZQ-AI Agent 自动生成*
""".strip()
