# main.py
# 正确的启动器，不会递归启动 Streamlit

import os
from dotenv import load_dotenv
load_dotenv(override=True)

import subprocess

if __name__ == "__main__":
    print("Launching FZQ-AI Intelligence Dashboard...")
    subprocess.run(["streamlit", "run", "ui_app.py"])
