# fzq_ai/config/env.py

import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

def get_env(key: str, default=None):
    """统一环境变量读取接口"""
    return os.getenv(key, default)
