# pipelines/narrative_pipeline.py

from services.llm_client import LLMClient
from core.config import Config


class NarrativePipeline:
    """
    FZQ‑AI Agent — Narrative Pipeline v1.5
    使用 LLM 对新闻进行叙事分析：
    - Global Summary
    - Narrative Clusters
    - Tension Matrix
    """

    def __init__(self, config: Config):
        self.config = config
        self.llm = LLMClient(config)

    # ------------------------------------------------------------
    # 生成全局总结
    # ------------------------------------------------------------
    def build_global_summary(self, articles):
        titles = [a["title"] for a in articles[: self.config.max_articles]]
        summaries = [a.get("summary", "") for a in articles[: self.config.max_articles]]

        prompt = f"""
你是一名地缘政治与国际新闻分析师。下面是若干新闻标题与摘要，请你生成一段“全球局势总结”（Global Summary），要求：

- 用中文撰写
- 结构清晰，分 2–4 段
- 覆盖主要地区（欧美、中东、亚太等）
- 强调趋势、风险点和潜在演变方向

新闻列表（标题 + 摘要）：
{list(zip(titles, summaries))}
"""

        return self.llm.ask(prompt).strip()

    # ------------------------------------------------------------
    # 生成叙事簇（Narrative Clusters）
    # ------------------------------------------------------------
    def build_narrative_clusters(self, articles):
        items = []
        for a in articles[: self.config.max_articles]:
            items.append({
                "title": a["title"],
                "summary": a.get("summary", ""),
                "source": a.get("source", "")
            })

        prompt = f"""
你是一名叙事分析专家。请根据以下新闻（标题 + 摘要），进行“叙事聚类”（Narrative Clustering）。

要求：
1. 按“叙事主题”分组，例如：
   - 美中竞争
   - 中东冲突
   - 能源与市场
   - 社会抗议与选举
2. 每个聚类给出：
   - cluster_name：简短中文标题
   - items：属于该叙事的新闻标题列表

请严格输出 JSON 格式，例如：
[
  {{
    "cluster_name": "中东局势升级",
    "items": ["标题1", "标题2", ...]
  }},
  ...
]

新闻数据：
{items}
"""

        text = self.llm.ask(prompt)
        import json
        try:
            clusters = json.loads(text)
        except Exception:
            clusters = []
        return clusters

    # ------------------------------------------------------------
    # 生成张力矩阵（Tension Matrix）
    # ------------------------------------------------------------
    def build_tension_matrix(self, articles):
        items = []
        for a in articles[: self.config.max_articles]:
            items.append({
                "title": a["title"],
                "summary": a.get("summary", ""),
                "source": a.get("source", "")
            })

        prompt = f"""
你是一名国际关系分析师。请从以下新闻中，提取“关键行为体之间的张力关系”（Tension Matrix）。

要求：
1. 找出存在明显对立、冲突、博弈的行为体（国家、组织、阵营等）
2. 每条关系包含：
   - actor1：行为体 1
   - actor2：行为体 2
   - description：一句话描述张力来源（中文）

请严格输出 JSON 数组，例如：
[
  {{
    "actor1": "以色列",
    "actor2": "哈马斯",
    "description": "加沙地带军事冲突持续升级，双方伤亡增加。"
  }},
  ...
]

新闻数据：
{items}
"""

        text = self.llm.ask(prompt)
        import json
        try:
            matrix = json.loads(text)
        except Exception:
            matrix = []
        return matrix

    # ------------------------------------------------------------
    # 主入口：对新闻列表进行完整叙事分析
    # ------------------------------------------------------------
    def run(self, articles):
        print("[NarrativePipeline] 开始叙事分析...")

        summary = self.build_global_summary(articles)
        clusters = self.build_narrative_clusters(articles)
        tension_matrix = self.build_tension_matrix(articles)

        print("[NarrativePipeline] 完成叙事分析")

        return {
            "global_summary": summary,
            "clusters": clusters,
            "tension_matrix": tension_matrix
        }
