# build_engine/workflow_engine.py
import os

from build_engine.target_blueprint import TARGET_STRUCTURE
from build_engine.project_scanner import scan_project
from build_engine.plan_builder import build_plan
from build_engine.plan_renderer import render_plan
from build_engine.skeleton_writer import safe_write_skeleton

# === v1.2：标准骨架模板 ===

SKELETONS = {
    "core/config.py": """class Config:
    \"\"\"全局配置对象（标准骨架）\"\"\"

    def __init__(self):
        # TODO: 添加你的全局配置
        pass
""",
    "core/logging_utils.py": """import logging

def setup_logging():
    \"\"\"初始化日志系统（标准骨架）\"\"\"
    logging.basicConfig(level=logging.INFO)
    logging.info("Logging initialized.")
""",
    "agents/fzq_agent.py": """class FZQAgent:
    \"\"\"FZQ 主代理模块（标准骨架）\"\"\"

    def __init__(self, config):
        self.config = config

    def run(self):
        \"\"\"主执行入口\"\"\"
        # TODO: 实现 orchestrator 逻辑
        print("FZQAgent running...")
""",
    "pipelines/news_pipeline.py": """class NewsPipeline:
    \"\"\"新闻聚合 Pipeline（标准骨架）\"\"\"

    def process(self):
        # TODO: 实现新闻抓取与处理
        pass
""",
    "pipelines/narrative_pipeline.py": """class NarrativePipeline:
    \"\"\"叙事分析 Pipeline（标准骨架）\"\"\"

    def process(self):
        # TODO: 实现叙事分析逻辑
        pass
""",
    "data/sources.py": """class DataSources:
    \"\"\"数据源定义（标准骨架）\"\"\"

    def list_sources(self):
        # TODO: 返回数据源列表
        return []
""",
    "ui/dashboard_stub.py": """class DashboardStub:
    \"\"\"UI / Dashboard 桥接层（标准骨架）\"\"\"

    def render(self):
        # TODO: 实现 UI 渲染逻辑
        pass
""",
}


def run_build(target="fzq", root_dir=None, dry_run=True) -> str:
    if root_dir is None:
        root_dir = os.getcwd()

    blueprint = TARGET_STRUCTURE

    scan_result = scan_project(root_dir, blueprint)
    plan = build_plan(root_dir, scan_result, blueprint)
    report = render_plan(plan)

    if dry_run:
        return report

    print("\n进入写盘模式（v1.2 混合模式）")
    print("空文件 → 自动写入骨架")
    print("已有内容 → 询问是否覆盖\n")

    for item in plan.items:
        full_path = os.path.join(root_dir, item.path)

        if item.path in SKELETONS:
            safe_write_skeleton(full_path, SKELETONS[item.path])

    return report + "\n\n[APPLY] v1.2 骨架写入完成（混合模式）"
