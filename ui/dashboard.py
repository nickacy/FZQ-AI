from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich import box

console = Console()

class Dashboard:
    """
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

                "\n[bold cyan]输入新闻编号查看详情，或按 q 返回退出：[/] "

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

        # Summary
        summary_text = self.narrative.get("global_summary", "N/A")
        layout["summary"].update(
            Panel(summary_text, title="[bold magenta]Global Narrative Summary[/]")
        )

        # News List

        for i, item in enumerate(self.news_list):
            news_table.add_row(str(i), item.get("title", ""), item.get("source", ""))

        # Narrative Clusters
        clusters = self.narrative.get("narrative_clusters", [])
        cluster_text = ""

        for c in clusters:
            for h in c.get("headlines", []):
                cluster_text += f"  - {h}\n"

        # Tension Matrix
        tension = self.narrative.get("tension_matrix", [])
        tension_table = Table(box=box.SIMPLE)
        tension_table.add_column("Actor 1", width=15)
        tension_table.add_column("Actor 2", width=15)
        tension_table.add_column("Description", width=60)

        for t in tension:

        console.print(layout)

    # ============================================================
    # 新闻详情页
    # ============================================================

    def render_news_detail(self, idx):
        item = self.news_list[idx]

        console.print(Panel(detail_text, title=f"[bold green]News Detail — #{idx}[/]"))
