# tui/news_view.py

class NewsListView:
    """
    """

    def __init__(self, articles, page_size=20):
        self.articles = articles
        self.page_size = page_size
        self.page = 0
        self.total_pages = max(1, (len(articles) - 1) // page_size + 1)

    # ------------------------------------------------------------
    # 分页逻辑
    # ------------------------------------------------------------
    def get_page_items(self):
        start = self.page * self.page_size
        end = start + self.page_size
        return self.articles[start:end]

    def next_page(self):
        if self.page < self.total_pages - 1:
            self.page += 1

    def prev_page(self):
        if self.page > 0:
            self.page -= 1

    def first_page(self):
        self.page = 0

    def last_page(self):
        self.page = self.total_pages - 1

    # ------------------------------------------------------------
    # 渲染新闻列表
    # ------------------------------------------------------------
    def render(self):
        items = self.get_page_items()

        print("\n" + "=" * 80)
        print("📡 News List (Page {}/{} )".format(self.page + 1, self.total_pages))
        print("=" * 80)
        print("{:<4} {:<70} {:<10}".format("ID", "Title", "Source"))
        print("-" * 80)

        for idx, item in enumerate(items):
            global_index = self.page * self.page_size + idx
            print("{:<4} {:<70} {:<10}".format(global_index, title, source))

        print("-" * 80)
        print("[j] 下一页   [k] 上一页   [g] 第一页   [G] 最后一页")
        print("[编号] 查看详情   [q] 返回上一层")
        print("=" * 80)

    # ------------------------------------------------------------
    # 主循环（阻塞式）
    # ------------------------------------------------------------
    def interact(self, on_select_callback):
        """
        """
        while True:
            self.render()
            cmd = input("输入指令：").strip()

            if cmd == "j":
                self.next_page()
            elif cmd == "k":
                self.prev_page()
            elif cmd == "g":
                self.first_page()
            elif cmd == "G":
                self.last_page()
            elif cmd.isdigit():
                index = int(cmd)
                if 0 <= index < len(self.articles):
                    on_select_callback(index)
            elif cmd == "q":
