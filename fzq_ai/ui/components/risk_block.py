# fzq_ai/ui/components/risk_block.py
"""
风险分析展示组件 (v2.5)

使用统一的防御性渲染模式：
- 成功：展示结构化风险卡片
- 失败：展示友好错误提示
- 空结果：显示提示信息
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import streamlit as st


def render_risk_block(risk_data: Any) -> None:
    """
    渲染风险分析结果。

    Args:
        risk_data: dict 或任何格式的风险数据。
                   预期结构: {overall_risk_score, category_intensity, items}
    """
    st.markdown("## ⚠️ 风险分析")

    # ── 防御性解析 ────────────────────────────────────────────
    if risk_data is None:
        st.info("暂无风险数据")
        return

    data: Optional[Dict[str, Any]] = None
    if isinstance(risk_data, dict):
        data = risk_data
    elif hasattr(risk_data, "data") and isinstance(getattr(risk_data, "data"), dict):
        data = risk_data.data
    elif hasattr(risk_data, "__dict__"):
        data = getattr(risk_data, "__dict__", {})
    else:
        st.info(f"风险数据格式暂不支持（类型: {type(risk_data).__name__}）")
        return

    if not data:
        st.info("暂无风险数据")
        return

    # ── 整体风险评分 ──────────────────────────────────────────
    overall_score: float = float(data.get("overall_risk_score", 0))
    if overall_score >= 70:
        st.error(f"🔴 整体风险评分: **{overall_score} / 100** — 高风险")
    elif overall_score >= 40:
        st.warning(f"🟡 整体风险评分: **{overall_score} / 100** — 中等风险")
    elif overall_score > 0:
        st.success(f"🟢 整体风险评分: **{overall_score} / 100** — 低风险")
    else:
        st.info("整体风险评分: 暂无数据")

    # ── 各类别强度 ────────────────────────────────────────────
    category_intensity: Dict[str, int] = data.get("category_intensity", {})
    if category_intensity:
        st.markdown("### 风险类别分布")
        cols = st.columns(len(category_intensity))
        for idx, (cat, count) in enumerate(category_intensity.items()):
            label: str = {
                "political": "🏛️ 政治",
                "economic": "💰 经济",
                "military": "⚔️ 军事",
                "social": "👥 社会",
                "technology": "🔧 科技",
            }.get(cat, cat)
            with cols[idx]:
                st.metric(label=label, value=count)

    # ── 高风险条目列表 ────────────────────────────────────────
    items: List[Dict[str, Any]] = data.get("items", [])
    high_risk_items: List[Dict[str, Any]] = [
        i for i in items if i.get("risk_score", 0) >= 50
    ]

    if high_risk_items:
        st.markdown("### ⚡ 高风险条目")
        for item in high_risk_items[:10]:
            title: str = item.get("title", "无标题")
            score: int = item.get("risk_score", 0)
            cats: List[str] = item.get("risk_categories", [])
            st.markdown(
                f"- **{title[:80]}** "
                f"(评分: {score}, 类别: {', '.join(cats) if cats else '无'})"
            )
    elif items:
        st.info(f"已分析 {len(items)} 条新闻，未发现高风险信号")
