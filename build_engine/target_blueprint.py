# build_engine/target_blueprint.py

TARGET_STRUCTURE = {
    "core/__init__.py": "Core package",
    "core/config.py": "Global configuration",
    "core/logging_utils.py": "Logging helpers",
    "agents/__init__.py": "Agents package",
    "agents/fzq_agent.py": "Main FZQ agent entry",
    "pipelines/__init__.py": "Pipelines package",
    "pipelines/news_pipeline.py": "News aggregation pipeline",
    "pipelines/narrative_pipeline.py": "Narrative analysis pipeline",
    "data/__init__.py": "Data sources package",
    "data/sources.py": "Source definitions",
    "ui/__init__.py": "UI bridge package",
    "ui/dashboard_stub.py": "Dashboard / TUI bridge stub",
    "main.py": "Main entry point",
}
