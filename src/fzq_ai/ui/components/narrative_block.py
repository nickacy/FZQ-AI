import streamlit as st


def render_narrative_block(narrative_data):
    """
    Render narrative analysis block in the UI.
    """

    if not narrative_data:
        st.info("No narrative data available.")
        return

    title = narrative_data.get("title", "Narrative Summary")
    zh = narrative_data.get("zh", "")
    en = narrative_data.get("en", "")

    st.markdown(
        f"""
        <div style="
            border:1px solid #ddd;
            border-radius:8px;
            padding:12px;
            margin-bottom:12px;
            background-color:#fdfdfd;
        ">
            <h3 style="margin-bottom:10px;">{title}</h3>

            <h4>中文叙事</h4>
            <p>{zh}</p>

            <hr style="margin:12px 0;">

            <h4>English Narrative</h4>
            <p>{en}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
