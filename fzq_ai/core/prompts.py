"""
fzq_ai.core.prompts

统一 Prompt 模板系统：
- Narrative（叙事分析）
- Risk（风险分析）
- Daily Report（日常情报报告）
- 所有 Pipeline、CLI、API、UI 均使用同一套模板
- 支持参数化、版本化、可扩展
"""

from __future__ import annotations

from typing import Any, Dict


class PromptTemplates:
    """
    Prompt 模板统一管理类。
    所有模板均为纯字符串，不依赖 Jinja2，避免额外依赖。
    """

    # ============================
    # v8: 议题扩展模板 Topic Expansion v1
    # ============================
    TOPIC_EXPANSION_V1 = """
你是一名全球情报分析师。请根据以下议题，生成相关搜索关键词。

【议题】
{{topic}}

【任务要求】
1. 生成 5-10 个与议题直接相关的搜索关键词
2. 包括中英文双语关键词
3. 包括不同区域/角度的变体
4. 每个关键词应独立且具体，适合搜索引擎使用

【输出要求】
1. 只输出 JSON，不要输出任何解释性文字、Markdown 代码块标记或自然语言。
2. 不要输出 ```json 或 ``` 等标记。
3. 如果无法分析，返回空 JSON：{}

严格输出 JSON 格式：
{
    "keywords": ["关键词1", "keyword 2", "关键词3", "keyword 4"]
}
"""

    # ============================
    # v8: 议题区域分类模板 Topic Region Classification v1
    # ============================
    TOPIC_REGION_CLASSIFICATION_V1 = """
你是一名地缘政治分析师。请根据以下议题，判断其最相关的地理区域。

【议题】
{{topic}}

【任务要求】
1. 判断议题主要涉及哪些地理区域
2. 区域选项：global, us, cn, eu, uk, jp, kr, in, br, ru, ae, sa, tw, hk, sg, id, th, vn, my, ph, de, fr, it, es, nl, mx, ca, au
3. 可以返回多个相关区域
4. 返回区域的重要性排序（从高到低）

【输出要求】
1. 只输出 JSON，不要输出任何解释性文字、Markdown 代码块标记或自然语言。
2. 不要输出 ```json 或 ``` 等标记。
3. 如果无法分析，返回空 JSON：{}

严格输出 JSON 格式：
{
    "regions": ["us", "cn", "eu"],
    "primary_region": "us",
    "confidence": 0.85
}
"""

    # ============================
    # v8: 议题语言分类模板 Topic Language Classification v1
    # ============================
    TOPIC_LANGUAGE_CLASSIFICATION_V1 = """
你是一名语言分析专家。请根据以下议题，判断应使用哪些语言进行搜索。

【议题】
{{topic}}

【任务要求】
1. 判断议题原始语言
2. 判断搜索时应覆盖哪些语言
3. 语言选项：en, zh, es, fr, de, ja, ko, ar, ru, pt, it, nl, tr, pl, vi, th, id
4. 返回推荐的搜索语言列表

【输出要求】
1. 只输出 JSON，不要输出任何解释性文字、Markdown 代码块标记或自然语言。
2. 不要输出 ```json 或 ``` 等标记。
3. 如果无法分析，返回空 JSON：{}

严格输出 JSON 格式：
{
    "original_language": "en",
    "search_languages": ["en", "zh", "es"],
    "confidence": 0.9
}
"""

    # ============================
    # v8: 新闻相关性过滤模板 News Relevance Filter v1
    # ============================
    NEWS_RELEVANCE_FILTER_V1 = """
你是一名新闻编辑。请评估以下新闻与指定议题的相关性。

【议题】
{{topic}}

【待评估新闻】
{{news_batch}}

【任务要求】
1. 逐条评估每条新闻与议题的相关性
2. 评分标准：0-1（0=完全无关，1=高度相关）
3. 关注：主题匹配度、内容深度、时效性、来源可信度

【输出要求】
1. 只输出 JSON，不要输出任何解释性文字、Markdown 代码块标记或自然语言。
2. 不要输出 ```json 或 ``` 等标记。
3. 如果无法分析，返回空 JSON：{}

严格输出 JSON 格式：
{
    "scores": [0.85, 0.3, 0.7, 0.9]
}
"""

    # ============================
    # 翻译模板 Translation v1
    # ============================
    TRANSLATION_V1 = """
你是一名专业翻译。请将以下新闻翻译成 {{target_language}}。

【原文标题】
{{title}}

【原文内容】
{{content}}

【输出要求】
1. 只输出 JSON，不要输出任何解释性文字、Markdown 代码块标记或自然语言。
2. 不要输出 ```json 或 ``` 等标记。
3. 如果无法翻译，返回空 JSON：{}

严格输出 JSON 格式：
{
    "title": "翻译后的标题",
    "content": "翻译后的内容",
    "confidence": 0.95,
    "provider": "llm-translation"
}
"""

    # ============================
    # 叙事分析模板 Narrative Analysis v1
    # ============================
    NARRATIVE_ANALYSIS_V1 = """
你是一名叙事分析专家。请分析以下新闻内容，提取核心叙事结构。

【新闻内容】
{{text}}

【输出要求】
1. 只输出 JSON，不要输出任何解释性文字、Markdown 代码块标记或自然语言。
2. 不要输出 ```json 或 ``` 等标记。
3. 如果无法分析，返回空 JSON：{}

严格输出 JSON 格式：
{
    "primary_narrative": "主要叙事（一句话描述核心故事）",
    "secondary_narratives": ["次要叙事1", "次要叙事2"],
    "narrative_strength": 0.8,
    "key_actors": ["关键行为者1", "关键行为者2"],
    "key_themes": ["主题1", "主题2"],
    "timeline_indicators": ["时间指标1"],
    "related_events": ["相关事件1"]
}
"""

    # ============================
    # 风险分析模板 Risk Analysis v1
    # ============================
    RISK_ANALYSIS_V1 = """
你是一名风险分析专家。请评估以下新闻内容的风险。

【新闻内容】
{{text}}

【输出要求】
1. 只输出 JSON，不要输出任何解释性文字、Markdown 代码块标记或自然语言。
2. 不要输出 ```json 或 ``` 等标记。
3. 如果无法分析，返回空 JSON：{}

严格输出 JSON 格式：
{
    "overall_risk_level": "medium",
    "composite_risk_score": 0.7,
    "risk_factors": [
        {
            "risk_type": "地缘政治",
            "description": "风险描述",
            "level": "medium",
            "probability": 0.6,
            "impact_score": 0.7,
            "affected_regions": ["us", "cn"],
            "affected_sectors": ["科技"],
            "time_horizon": "short_term",
            "evidence": ["证据1"]
        }
    ],
    "systemic_risk_indicators": ["系统性风险指标1"]
}
"""

    # ============================
    # 情感分析模板 Sentiment Analysis v1
    # ============================
    SENTIMENT_ANALYSIS_V1 = """
你是一名情感分析专家。请分析以下新闻内容的情感倾向。

【新闻内容】
{{text}}

【输出要求】
1. 只输出 JSON，不要输出任何解释性文字、Markdown 代码块标记或自然语言。
2. 不要输出 ```json 或 ``` 等标记。
3. 如果无法分析，返回空 JSON：{}

严格输出 JSON 格式：
{
    "overall_sentiment": "positive",
    "sentiment_score": 0.6,
    "headline_sentiment": "positive",
    "headline_score": 0.5,
    "content_sentiment": "neutral",
    "content_score": 0.0,
    "entity_sentiments": {"Entity Name": 0.5},
    "market_indicators": ["市场指标1"]
}
"""

    # ============================
    # 情景分析模板 Scenario Analysis v1
    # ============================
    SCENARIO_ANALYSIS_V1 = """
你是一名情景分析专家。请基于以下新闻内容构建未来情景。

【新闻内容】
{{text}}

【输出要求】
1. 只输出 JSON，不要输出任何解释性文字、Markdown 代码块标记或自然语言。
2. 不要输出 ```json 或 ``` 等标记。
3. 如果无法分析，返回空 JSON：{}

严格输出 JSON 格式：
{
    "base_case": {
        "scenario_name": "基准情景",
        "description": "最可能的情景描述",
        "probability": 0.5,
        "key_triggers": ["触发因素1"],
        "expected_outcomes": ["预期结果1"],
        "time_horizon": "short_term",
        "affected_regions": ["global"]
    },
    "optimistic_case": {
        "scenario_name": "乐观情景",
        "description": "乐观情景描述",
        "probability": 0.2,
        "key_triggers": ["触发因素1"],
        "expected_outcomes": ["预期结果1"],
        "time_horizon": "short_term",
        "affected_regions": ["global"]
    },
    "pessimistic_case": {
        "scenario_name": "悲观情景",
        "description": "悲观情景描述",
        "probability": 0.2,
        "key_triggers": ["触发因素1"],
        "expected_outcomes": ["预期结果1"],
        "time_horizon": "short_term",
        "affected_regions": ["global"]
    },
    "alternative_scenarios": []
}
"""
    NARRATIVE_V1 = """
你是一名资深国际关系叙事分析专家。请基于以下新闻内容，提取叙事结构并输出结构化 JSON。

【任务要求】
1. 提取 3 条主要叙事线索（Narrative Frames）
2. 每条叙事需包含：
   - 叙事主题（不超过 12 字）
   - 涉及的核心实体（国家/组织/人物）
   - 情绪基调（正面/中性/负面）
   - 叙事倾向（政治/经济/军事/社会/科技）
   - 演变趋势（上升/下降/稳定）
   - 潜在影响评分（1–10）

【新闻内容】
{{news_content}}

【输出格式】
严格输出 JSON 数组，每个元素为一个对象：
[
  {
    "topic": "...",
    "entities": ["...", "..."],
    "tone": "...",
    "category": "...",
    "trend": "...",
    "impact_score": 7
  }
]
"""

    # ============================
    # 风险分析模板 Risk v1
    # ============================
    RISK_V1 = """
你是一名全球风险分析专家。请基于叙事分析结果与新闻内容，生成结构化风险评估。

【任务要求】
识别最高 3 项风险，每项包含：
- 风险名称
- 风险类别（地缘政治/经济/社会/科技/环境）
- 风险等级（低/中/高/极高）
- 触发条件
- 关键驱动因素
- 24 小时展望
- 未来 7 天展望
- 相关叙事引用（引用叙事 topic）

【新闻内容】
{{news_content}}

【叙事分析结果】
{{narrative_result}}

【输出格式】
严格输出 JSON 数组，每个元素为一个对象。
"""

    # ============================
    # v10: 合并多维度分析模板 Multi-Dimension Analysis v1
    # 将 narrative / risk / sentiment / scenario 合并为单 prompt
    # 降低 75% LLM 调用成本（4 次 → 1 次）
    # ============================
    MULTI_DIMENSION_ANALYSIS_V1 = """
你是一名全球情报分析专家。请对以下新闻内容进行全面的多维度分析，输出叙事、风险、情感、情景四个维度。

【新闻内容】
{{text}}

【输出要求】
1. 只输出 JSON，不要输出任何解释性文字、Markdown 代码块标记或自然语言。
2. 不要输出 ```json 或 ``` 等标记。
3. 如果无法分析，返回空 JSON：{}

严格输出 JSON 格式：
{
    "narrative": {
        "primary_narrative": "主要叙事（一句话描述核心故事）",
        "secondary_narratives": ["次要叙事1", "次要叙事2"],
        "narrative_strength": 0.8,
        "key_actors": ["关键行为者1", "关键行为者2"],
        "key_themes": ["主题1", "主题2"],
        "timeline_indicators": ["时间指标1"],
        "related_events": ["相关事件1"]
    },
    "risk": {
        "overall_risk_level": "medium",
        "composite_risk_score": 0.7,
        "risk_factors": [
            {
                "risk_type": "地缘政治",
                "description": "风险描述",
                "level": "medium",
                "probability": 0.6,
                "impact_score": 0.7,
                "affected_regions": ["us", "cn"],
                "affected_sectors": ["科技"],
                "time_horizon": "short_term",
                "evidence": ["证据1"]
            }
        ],
        "systemic_risk_indicators": ["系统性风险指标1"]
    },
    "sentiment": {
        "overall_sentiment": "positive",
        "sentiment_score": 0.6,
        "headline_sentiment": "positive",
        "headline_score": 0.5,
        "content_sentiment": "neutral",
        "content_score": 0.0,
        "entity_sentiments": {"Entity Name": 0.5},
        "market_indicators": ["市场指标1"]
    },
    "scenario": {
        "base_case": {
            "scenario_name": "基准情景",
            "description": "最可能的情景描述",
            "probability": 0.5,
            "key_triggers": ["触发因素1"],
            "expected_outcomes": ["预期结果1"],
            "time_horizon": "short_term",
            "affected_regions": ["global"]
        },
        "optimistic_case": {
            "scenario_name": "乐观情景",
            "description": "乐观情景描述",
            "probability": 0.2,
            "key_triggers": ["触发因素1"],
            "expected_outcomes": ["预期结果1"],
            "time_horizon": "short_term",
            "affected_regions": ["global"]
        },
        "pessimistic_case": {
            "scenario_name": "悲观情景",
            "description": "悲观情景描述",
            "probability": 0.2,
            "key_triggers": ["触发因素1"],
            "expected_outcomes": ["预期结果1"],
            "time_horizon": "short_term",
            "affected_regions": ["global"]
        },
        "alternative_scenarios": []
    },
    "confidence": 0.85,
    "provider_used": "deepseek",
    "latency_ms": 0
}
"""

    # ============================
    # 日报模板 Daily Report v1
    # ============================
    DAILY_REPORT_V1 = """
你是一名专业的全球情报分析师，请基于以下输入生成《全球情报日报》。

【输入：新闻摘要】
{{news_content}}

【输入：叙事分析】
{{narratives}}

【输入：风险分析】
{{risks}}

【输出结构要求】
1. 《今日摘要》：用一段话总结今日最重要的三件事
2. 《叙事演变》：逐条列出叙事主题、趋势、影响评分
3. 《风险聚焦》：逐条列出风险名称、等级、触发条件、展望
4. 《综合评估》：对全球稳定性做出 1–10 的评分，并说明理由
5. 《推荐关注点》：列出未来 24 小时需重点关注的 3 个事项

【输出格式】
严格输出纯文本，不包含 JSON。
"""

    # ============================
    # 模板渲染函数（无依赖）
    # ============================
    @staticmethod
    def render(template: str, variables: Dict[str, Any]) -> str:
        """
        简单模板渲染器：
        将 {{var}} 替换为 variables[var]
        不依赖 Jinja2，避免额外依赖导致部署复杂化。
        """
        output = template
        for key, value in variables.items():
            placeholder = "{{" + key + "}}"
            output = output.replace(placeholder, str(value))
        return output
