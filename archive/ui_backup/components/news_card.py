def render_news_card(article):
    """
    Render a single news article card for the Streamlit UI.
    """

    title = article.title_original or ""
    content = article.content_original or ""
    source = article.source_name or ""
    region = article.region or ""
    url = article.url or ""
    language = article.language or ""

    # 语言标记（如果不是英文）
    if language and language not in ("en", ""):
        lang_badge = f" [{language}]"
    else:
        lang_badge = ""

    # 渲染 HTML 卡片
    return f"""
    <div style="
        border:1px solid #ddd;
        border-radius:8px;
        padding:12px;
        margin-bottom:12px;
        background-color:#fafafa;
    ">
        <h3 style="margin-bottom:6px;">{title}{lang_badge}</h3>
        <p style="margin-top:0; margin-bottom:8px;">{content}</p>
        <p style="font-size:13px; color:#666;">
            <b>Source:</b> {source} &nbsp; | &nbsp;
            <b>Region:</b> {region}
        </p>
        <a href="{url}" target="_blank" style="font-size:14px;">🔗 Read more</a>
    </div>
    """
