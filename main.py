# main.py
# FZQ-AI Intelligence Dashboard Launcher

import os
from dotenv import load_dotenv

# ============================
#  加载环境变量
# ============================
load_dotenv(override=True)

import subprocess

print("Launching FZQ-AI Intelligence Dashboard...")
subprocess.run(["streamlit", "run", "ui_app.py"])
