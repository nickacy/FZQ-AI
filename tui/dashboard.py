# tui/dashboard.py

from tui.news_view import NewsListView


def show_article_detail(article):
    """
    显示新闻详情
    """
    print("\n" + "=" * 80)
    print("📰 新闻详情")
    print("=" * 80)
    print("标题：", article.get("title", ""))
    print("来源：", article.get("source", ""))
    print("URL：", article.get("url", ""))

    content = article.get("content", "")
    if content:
        print("\n内容：\n")
        print(content)
    else:
        print("\n（无正文内容）")

    print("\n按回车返回列表...")
    input()


def render_news_list(articles):
    """
    新闻列表入口（分页版）
    """
    view = NewsListView(articles)
    view.interact(show_article_detail)


def render_clusters(clusters):
    """
    渲染 Narrative Clusters
    """
    print("\n" + "=" * 80)
    print("🧩 Narrative Clusters")
    print("=" * 80)

    for cluster in clusters:
        print(f"\n【{cluster['cluster_name']}】")
        for item in cluster["items"]:
            print(" -", item)

    print("\n" + "=" * 80)


def render_tension_matrix(matrix):
    """
    渲染 Tension Matrix
    """
    print("\n" + "=" * 80)
    print("⚠️  Tension Matrix")
    print("=" * 80)

    print("{:<20} {:<20} {:<40}".format("Actor 1", "Actor 2", "Description"))
    print("-" * 80)

    for row in matrix:
        print("{:<20} {:<20} {:<40}".format(
            row["actor1"], row["actor2"], row["description"][:40]
        ))

    print("\n" + "=" * 80)


def render_summary(summary):
    """
    渲染 Global Summary
    """
    print("\n" + "=" * 80)
    print("🌍 Global Summary")
    print("=" * 80)
    print(summary)
    print("\n" + "=" * 80)


def dashboard_main(summary, clusters, tension_matrix, articles):
    """
    Dashboard 主入口
    """
    render_summary(summary)
    render_clusters(clusters)
    render_tension_matrix(tension_matrix)

    print("\n按回车进入新闻列表...")
    input()

    render_news_list(articles)
