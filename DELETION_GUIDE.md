# FZQ-AI 清理指南

以下文件/目录已被审计确认为死代码或重复代码，**建议删除**。

## 一、死代码文件（根级）

这些文件从未被活跃系统导入或使用：

| 文件 | 原因 | 操作 |
|------|------|------|
| `_fix_registry.py` | 草稿代码，目标模块 `llm/task_registry.py` 不存在 | 删除 |
| `fix_utcnow.py` | 一次性迁移脚本（`datetime.utcnow` → `datetime.now(timezone.utc)`） | 删除或移至 `scripts/` |
| `cleanup_project.py` | 一次性目录清理脚本 | 删除 |
| `nick_tui.py` | 遗留 TUI，使用废弃的 `AgentHub` | 删除或移至 `examples/` |
| `run_agent_demo.py` | 遗留演示脚本，使用废弃的 `AgentHub` | 删除或移至 `examples/` |
| `ci_health_check.py` | 若 CI 未使用则删除 | 确认后再删除 |
| `streamlit_app.py` | 孤立的 Streamlit 应用，与 `ui_app.py` 重复 | 删除或移至 `examples/` |
| `api_server.py` | 与 `app.py` 功能重复，端口冲突 | 迁移独有端点后删除 |

**一键删除命令：**

```bash
cd C:\Users\nicka\FZQ-AI-WORKSPACE\FZQ-AI

git rm -f _fix_registry.py fix_utcnow.py cleanup_project.py \
    nick_tui.py run_agent_demo.py streamlit_app.py

# 如果 ci_health_check.py 未被 CI 使用，也删除：
# git rm -f ci_health_check.py
```

## 二、死代码目录（real/ 和 task_registry/）

`real/` 目录下的代码完全未被活跃系统调用，属于架构演化遗留。
`task_registry/` 整个包已无人使用。

**一键删除命令：**

```bash
cd C:\Users\nicka\FZQ-AI-WORKSPACE\FZQ-AI

git rm -rf src/fzq_ai/schemas/real/
git rm -rf src/fzq_ai/pipelines/real/
git rm -rf src/fzq_ai/orchestrator/real/
git rm -rf src/fzq_ai/llm/real/
git rm -rf src/fzq_ai/task_registry/
```

## 三、被 Git 跟踪但应忽略的文件

`fzq_ai_agent.egg-info/` 已在 `.gitignore` 中列出，但因已被 git 跟踪所以无效。

**修复命令：**

```bash
cd C:\Users\nicka\FZQ-AI-WORKSPACE\FZQ-AI

git rm -rf fzq_ai_agent.egg-info/
git commit -m "chore: remove dead code and tracked egg-info"
```

## 四、待删除的重复 FastAPI 应用

| 文件 | 状态 | 说明 |
|------|------|------|
| `src/fzq_ai/api/app.py` | 立即删除 | 文件中重复创建了两个 `FastAPI()` 实例，本身就是 bug |
| `api_server.py` | 先迁移后删除 | 其独有端点 `/version` 和 `/pipelines` 需先迁移到 `app.py` |

**注意：** `api_server.py` 的 `/version` 和 `/pipelines` 端点尚未在 `app.py` 中实现。建议在删除 `api_server.py` 之前，先将这两个端点添加到 `app.py`。

## 五、删除后验证

删除后，请运行以下命令验证项目仍然可用：

```bash
# 1. 检查是否有残留引用
grep -r "from fzq_ai.llm.real" src/ || echo "No references to llm.real"
grep -r "from fzq_ai.pipelines.real" src/ || echo "No references to pipelines.real"
grep -r "from fzq_ai.orchestrator.real" src/ || echo "No references to orchestrator.real"
grep -r "from fzq_ai.schemas.real" src/ || echo "No references to schemas.real"
grep -r "from fzq_ai.task_registry" src/ || echo "No references to task_registry"

# 2. 运行测试
python -m pytest tests/ -v --tb=short

# 3. 尝试启动应用（不实际运行）
python -c "from app import app; print('FastAPI app imports OK')"
python -c "from main import *; print('main.py imports OK')"
```

---

*本指南由审计自动生成，删除前建议备份或确认 git 已提交当前状态。*
