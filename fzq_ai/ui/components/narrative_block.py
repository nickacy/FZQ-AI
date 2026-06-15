# fzq_ai/ui/components/narrative_block.py
"""
叙事分析展示组件 (v2.5)

使用统一的防御性渲染模式：
- 成功：展示结构化叙事卡片（按阵营分区）
- 失败：展示友好错误提示
- 空结果：显示提示信息
"""

from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

BLOC_COLORS: Dict[str, str] = {
    "western": "#4A90E2",
    "east_asia": "#D0021B",
    "middle_east": "#9013FE",
    "other": "#7ED321",
}

BLOC_LABELS: Dict[str, str] = {
    "western": "西方",
    "east_asia": "东亚",
    "middle_east": "中东",
    "other": "其他",
}


def render_narrative_block(narrative_data: Any) -> None:
    st.markdown("## 多阵营叙事分析")

    if narrative_data is None:
        st.info("暂无叙事数据")
        return

    data: Dict[str, Any] = {}
    if isinstance(narrative_data, dict):
        data = narrative_data
    elif hasattr(narrative_data, "data"):
        raw = getattr(narrative_data, "data", {})
        if isinstance(raw, dict):
            data = raw
        else:
            data = {}
    else:
        st.info("叙事数据格式暂不支持")
        return

    if not data:
        st.info("暂无叙事数据")
        return

    has_any = False
    for bloc in ["western", "east_asia", "middle_east", "other"]:
        bloc_data: Dict[str, Any] = data.get(bloc, {})
        if not bloc_data:
            continue

        label = BLOC_LABELS.get(bloc, bloc)
        themes: List[str] = bloc_data.get("themes", [])
        articles: List[Dict[str, Any]] = bloc_data.get("articles", [])

        if not themes and not articles:
            continue
        has_any = True

        color = BLOC_COLORS.get(bloc, "#333")
        st.markdown(
            f"""<div style="background-color:{color};padding:6px 12px;
            border-radius:4px;color:white;font-weight:bold;margin-bottom:8px;">
            {label} 阵营</div>""",
            unsafe_allow_html=True,
        )

        if themes:
            st.markdown(f"**核心主题:** {' | '.join(themes[:6])}")

        if articles:
            for a in articles[:5]:
                title = a.get("title", "无标题")
                source = a.get("source", "")
                url = a.get("url", "")
                if url:
                    st.markdown(f"- [{title[:80]}]({url}) ({source})")
                else:
                    st.markdown(f"- {title[:80]} ({source})")

        st.markdown("---")

    if not has_any:
        st.info("各阵营暂无显著叙事数据")
