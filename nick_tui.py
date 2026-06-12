import cmd
import os
import sys
import time
import shutil
from fzq_ai_agent import report
from services.llm_client import LLMClient
from build_engine.workflow_engine import run_build


SUPPORTED_MODELS = [
    "deepseek-chat",
    "deepseek-reasoner",
    "deepseek-coder",
    "deepseek-r1",
]

SUPPORTED_COMMANDS = [
    "/ask",
    "/model",
    "/theme",
    "/up",
    "/down",
    "/build",
    "/quit",
]


class NickTUI:
    def __init__(self):
        self.llm = LLMClient()
        self.history = []
        self.current_model = "deepseek-chat"
        self.theme = "dark"
        self.page = 0
        self.page_size = 15

    # ---------------------------
    # UI Rendering (Single Column)
    # ---------------------------
    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def render(self):
        self.clear_screen()
        print("=" * 80)
        print(f" Nick‑TUI  |  Model: {self.current_model}  |  Theme: {self.theme}")
        print("=" * 80)

        start = max(0, len(self.history) - (self.page + 1) * self.page_size)
        end = len(self.history) - self.page * self.page_size
        for speaker, msg in self.history[start:end]:
            prefix = "你：" if speaker == "user" else "AI："
            print(f"{prefix} {msg}")
            print("-" * 80)

        print(f"[Page {self.page + 1}]  输入 /quit 退出")
        print("=" * 80)

    # ---------------------------
    # History & Paging
    # ---------------------------
    def add_user_message(self, msg):
        self.history.append(("user", msg))

    def add_ai_message(self, msg):
        self.history.append(("ai", msg))

    def page_up(self):
        self.page += 1

    def page_down(self):
        if self.page > 0:
            self.page -= 1

    # ---------------------------
    # Command Handlers
    # ---------------------------
    def handle_model_switch(self, model):
        if model in SUPPORTED_MODELS:
            self.current_model = model
            self.add_ai_message(f"模型已切换为：{model}")
        else:
            self.add_ai_message(f"未知模型：{model}")

    def handle_theme_switch(self, theme):
        if theme in ["dark", "light"]:
            self.theme = theme
            self.add_ai_message(f"主题已切换为：{theme}")
        else:
            self.add_ai_message("主题仅支持：dark / light")

    def handle_ask_llm(self, prompt):
        self.add_user_message(prompt)
        reply = self.llm.ask(self.current_model, prompt)
        self.add_ai_message(reply)

    # ---------------------------
    # 核心：命令解析
    # ---------------------------
    def handle_command(self, cmd: str) -> bool:
        cmd = cmd.strip()
        if not cmd:
            return True

        if cmd.lower() in ("/quit", "/exit"):
            return False

        if cmd == "/up":
            self.page_up()
            return True

        if cmd == "/down":
            self.page_down()
            return True

        if cmd.startswith("/model "):
            model = cmd.split(" ", 1)[1]
            self.handle_model_switch(model)
            return True

        if cmd.startswith("/theme "):
            theme_name = cmd.split(" ", 1)[1]
            self.handle_theme_switch(theme_name)
            return True

        # ---------------------------
        # Build Engine v1.0‑alpha
        # ---------------------------
        if cmd.startswith("/build"):
            if "--apply" in cmd:
                report = run_build(target="fzq", dry_run=False)
        else:
                report = run_build(target="fzq", dry_run=True)

        self.add_ai_message(report)
        return True


        # ---------------------------
        # /ask llm xxx
        # ---------------------------
        if cmd.startswith("/ask "):
            parts = cmd.split(" ", 2)
            if len(parts) >= 3 and parts[1] == "llm":
                self.handle_ask_llm(parts[2])
            else:
                self.add_ai_message("格式错误，应为：/ask llm 你的问题")
            return True

        # 默认：直接问 LLM
        self.handle_ask_llm(cmd)
        return True

    # ---------------------------
    # Main Loop
    # ---------------------------
    def run(self):
        while True:
            self.render()
            try:
                cmd = input("> ")
            except KeyboardInterrupt:
                break

            if not self.handle_command(cmd):
                break


if __name__ == "__main__":
    app = NickTUI()
    app.run()
