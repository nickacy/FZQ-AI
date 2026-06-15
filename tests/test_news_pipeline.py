# test_news_pipeline.py
from dotenv import load_dotenv

load_dotenv(override=True)

import yaml
import os
from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.pipelines.news_pipeline import NewsPipeline

def load_config():
    # 自动定位项目根目录

    # config.yaml 实际路径：fzq_ai/config/config.yaml

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"找不到 config.yaml，路径检查：{config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":

        "澳洲股市今日上涨 1.2%，科技股领涨。",
        "悉尼房价连续第三个月上涨，需求强劲。",
        "澳洲央行表示将维持利率不变。",

    result = pipeline.run(items)

    print("=== FZQ-AI Agent 新闻摘要（多模型协同） ===")
    print(result)

def test_dummy():
    assert True
