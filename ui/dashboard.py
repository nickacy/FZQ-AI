from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich import box

console = Console()


class Dashboard:
    """
    FZQ‑AI Agent — TUI Dashboard v1.4.2
    支持：
    - 主界面显示 Summary / News / Clusters / Tension Matrix
    - 按数字选择新闻查看详情
    - 按 q 返回主界面
    """

    def __init__(self):
        self.news_list = []
        self.narrative = None

    # ============================================================
    # 主入口
    # ============================================================

    def run(self, news_list, narrative):
        self.news_list = news_list
        self.narrative = narrative

        while True:
            self.render_main()

            user_input = console.input("\n[bold cyan]输入新闻编号查看详情，或按 q 返回退出：[/] ")

            if user_input.lower() == "q":
                break

            if user_input.isdigit():
                idx = int(user_input)
                if 0 <= idx < len(self.news_list):
                    self.render_news_detail(idx)
                    console.input("\n[bold cyan]按回车返回主界面[/] ")
                else:
                    console.print("[red]无效编号[/]")
            else:
                console.print("[red]请输入数字或 q[/]")

    # ============================================================
    # 主界面渲染
    # ============================================================

    def render_main(self):
        layout = Layout()

        layout.split(
            Layout(name="summary", size=7),
            Layout(name="body", ratio=1),
            Layout(name="tension", size=10),
        )

        layout["body"].split_row(
            Layout(name="news"),
            Layout(name="clusters"),
        )

        # Summary
        summary_text = self.narrative.get("global_summary", "N/A")
        layout["summary"].update(
            Panel(summary_text, title="[bold magenta]Global Narrative Summary[/]")
        )

        # News List
        news_table = Table(title="News List", box=box.SIMPLE)
        news_table.add_column("ID", width=4)
        news_table.add_column("Title", width=50)
        news_table.add_column("Source", width=12)

        for i, item in enumerate(self.news_list):
            news_table.add_row(str(i), item.get("title", ""), item.get("source", ""))

        layout["news"].update(Panel(news_table, border_style="green"))

        # Narrative Clusters
        clusters = self.narrative.get("narrative_clusters", [])
        cluster_text = ""

        for c in clusters:
            cluster_text += f"[bold yellow]{c.get('name', 'Unnamed')}[/]\n"
            cluster_text += f"Theme: {c.get('theme', '')}\n"
            cluster_text += "Headlines:\n"
            for h in c.get("headlines", []):
                cluster_text += f"  - {h}\n"
            cluster_text += "\n"

        layout["clusters"].update(
            Panel(cluster_text or "No clusters", title="[bold yellow]Narrative Clusters[/]")
        )

        # Tension Matrix
        tension = self.narrative.get("tension_matrix", [])
        tension_table = Table(box=box.SIMPLE)
        tension_table.add_column("Actor 1", width=15)
        tension_table.add_column("Actor 2", width=15)
        tension_table.add_column("Description", width=60)

        for t in tension:
            tension_table.add_row(
                t.get("actor_1", "N/A"),
                t.get("actor_2", "N/A"),
                t.get("description", "N/A"),
            )

        layout["tension"].update(
            Panel(tension_table, title="[bold red]Tension Matrix[/]")
        )

        console.clear()
        console.print(layout)

    # ============================================================
    # 新闻详情页
    # ============================================================

    def render_news_detail(self, idx):
        item = self.news_list[idx]

        title = item.get("title", "")
        source = item.get("source", "")
        url = item.get("url", "")
        summary = item.get("summary", "")

        detail_text = (
            f"[bold]{title}[/]\n"
            f"[cyan]Source:[/] {source}\n"
            f"[cyan]URL:[/] {url}\n\n"
            f"[white]{summary}[/]"
        )

        console.clear()
        console.print(
            Panel(detail_text, title=f"[bold green]News Detail — #{idx}[/]")
        )
