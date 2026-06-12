# fzq_ai/config/__init__.py
"""
配置入口：自动加载 .env 并导出 DeepSeek 连接参数。
"""
import os
from dotenv import load_dotenv

# 自动加载项目根目录的 .env 文件
load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
