# nick_tui.py
# Simple terminal UI for FZQ-AI

import cmd
import os
import sys
import yaml

from fzq_ai.agent_hub import AgentHub

SUPPORTED_COMMANDS = [
    "/ask",
    "/news",
    "/risk",
    "/report",
    "/quit",
]

def load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "fzq_ai", "config", "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

class NickTUI:
    def __init__(self):
        config = load_config()
        self.hub = AgentHub(config)
        self.history = []
        self.page = 0
        self.page_size = 15

    # ---------------------------
    # UI Rendering
    # ---------------------------
    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def render(self):
        self.clear_screen()
        print("=" * 80)
        print(" Nick-TUI  |  FZQ-AI Intelligence System")
        print("=" * 80)

        start = max(0, len(self.history) - (self.page + 1) * self.page_size)
        end = len(self.history) - self.page * self.page_size
        for speaker, msg in self.history[start:end]:
            prefix = "You: " if speaker == "user" else "AI: "
            print(f"{prefix} {msg}")
            print("-" * 80)

        print(f"[Page {self.page + 1}]  Type /quit to exit")
        print("=" * 80)

    # ---------------------------
    # History
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

        if cmd.startswith("/news "):
            topic = cmd.split(" ", 1)[1]
            self.add_user_message(f"[news] {topic}")
            result = self.hub.run_news(topic)
            self.add_ai_message(str(result.get("data", result)))
            return True

        if cmd.startswith("/risk "):
            text = cmd.split(" ", 1)[1]
            items = [text]
            self.add_user_message(f"[risk] {text}")
            result = self.hub.run_risk(items)
            self.add_ai_message(str(result.get("data", result)))
            return True

        if cmd.startswith("/report "):
            text = cmd.split(" ", 1)[1]
            items = text.split("|")
            self.add_user_message(f"[report] {text}")
            result = self.hub.run_daily_report(items)
            self.add_ai_message(str(result.get("data", result)))
            return True

        # Default: treat as general chat
        self.add_user_message(cmd)
        result = self.hub.run_news(cmd)
        self.add_ai_message(str(result.get("data", result)))
        return True

    # ---------------------------
    # Main Loop
    # ---------------------------
    def run(self):
        while True:
            self.render()
            try:
            except KeyboardInterrupt:

            if not self.handle_command(cmd):
                break

if __name__ == "__main__":
