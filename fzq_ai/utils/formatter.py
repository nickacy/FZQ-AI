class NewsFormatter:
    @staticmethod
    def format(raw: str) -> str:
        """
        """
        return f"### 📰 新闻摘要\n\n{raw.strip()}"

class NarrativeFormatter:
    @staticmethod
    def format(raw: str) -> str:
        """
        """
        return f"### 📚 叙事分析\n\n{raw.strip()}"

class RiskFormatter:
    @staticmethod
    def format(raw: str) -> dict:
        """
        """
        try:

            return data
        except Exception:
            return {"summary": "LLM 输出非 JSON 格式，已返回原始文本", "raw": raw}

class DailyReportFormatter:
    @staticmethod
    def format(news_summary: str, narrative: dict, risk: dict) -> str:
        """
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
