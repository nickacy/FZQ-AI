# ============================================================
# FZQ-AI 项目审计与修复报告
# ============================================================

## 执行摘要

本项目（FZQ-AI）是一个多模型情报分析系统，具有良好的功能愿景，但存在严重的架构债务、配置管理混乱、安全风险和测试缺失问题。以下报告列出了发现的所有关键问题及已落实的修复方案。

---

## 1. 架构债务（严重）

### 问题：三重代码重复（root + real/ + test_adapter/）

项目在每个核心模块下都维护了 `real/` 和 `test_adapter/` 子目录：
- `schemas/real/` vs `schemas/test_adapter/` — 近 300 行 schema 重复
- `pipelines/real/` vs `pipelines/test_adapter/` — 6 个 pipeline 重复
- `orchestrator/real/` vs `orchestrator/test_adapter/` — 2 个编排器重复
- `llm/real/` vs `llm/test_adapter/` — 4 个 LLM 模块重复

**影响：** 任何 schema 修改需要在 3 个地方同步维护；`real/` 目录的代码实际上从未被活跃系统调用（死代码）。

**修复方案：**
1. 删除所有 `real/` 目录（纯死代码）
2. 保留 `test_adapter/` 但标记为待重构（因测试仍依赖它们）
3. 长期计划：将 `test_adapter/` 替换为 pytest fixtures + unittest.mock

### 问题：3 个 FastAPI 应用冲突

| 文件 | 版本 | 状态 |
|------|------|------|
| `app.py` | v4.0.0 | ✅ 保留（最现代，使用 lifespan） |
| `api_server.py` | v2.6.0 | ⚠️ 删除（功能重复，端口冲突 8000） |
| `src/fzq_ai/api/app.py` | v1.0.0 | ⚠️ 删除（重复初始化 FastAPI 的 bug） |

**修复方案：** 保留 `app.py`，将 `api_server.py` 中独有的端点（`/version`, `/pipelines`）迁移到 `app.py` 后删除 `api_server.py`。`src/fzq_ai/api/app.py` 直接删除。

### 问题：多个 Streamlit 入口

- `ui_app.py` — 活跃入口
- `streamlit_app.py` — 孤立文件，硬编码 API URL
- `main.py` — 仅启动 `ui_app.py`

**修复方案：** 保留 `main.py` + `ui_app.py`，删除 `streamlit_app.py` 或移至 `examples/`。

### 问题：根级死代码文件

以下文件从未被活跃系统导入：
- `_fix_registry.py` — 草稿代码，目标模块不存在
- `fix_utcnow.py` — 一次性迁移脚本
- `cleanup_project.py` — 一次性清理脚本
- `nick_tui.py` — 遗留 TUI（使用废弃的 `AgentHub`）
- `run_agent_demo.py` — 遗留演示脚本
- `ci_health_check.py` — 仅当 CI 使用时保留

**修复方案：** 全部删除（或移至 `scripts/`/`examples/`）。

---

## 2. 安全与配置管理（严重）

### 问题：5 个独立的 `load_dotenv()` 调用点

| 文件 | 行为 |
|------|------|
| `api_server.py` | `load_dotenv(override=True)` |
| `main.py` | `load_dotenv(override=True)` |
| `src/fzq_ai/config.py` | `load_dotenv()` |
| `src/fzq_ai/config/__init__.py` | `load_dotenv(override=True)`（带 guard） |
| `src/fzq_ai/config/env.py` | `load_dotenv()` |

**影响：** 导入顺序不同会导致环境变量被不可预测地覆盖；多个模块产生副作用。

**修复方案：** 已统一——仅保留 `app.py` 和 `main.py` 的 `load_dotenv()`（应用入口），删除其他所有调用点。`src/fzq_ai/config/__init__.py` 已移除 `load_dotenv()`。`src/fzq_ai/config.py` 已改为从 `config/__init__.py` 导入。`env.py` 已删除。

### 问题：YAML 解析 Bug（config/__init__.py 第 52 行）

```python
# 修复前（BUG）：
config.update(json.load(f))  # 用 json.load 读取 YAML 文件！

# 修复后：
config.update(yaml.safe_load(f))  # 正确解析 YAML
```

**影响：** 此异常被静默吞掉（`except Exception: pass`），导致 `config.yaml` 永远被忽略，用户无法通过 YAML 配置系统。

### 问题：CORS 完全开放

`api_server.py` 中 `allow_origins=["*"]` 允许任何域名跨域请求，且允许所有方法和头。

**修复方案：** 已改为环境变量驱动的白名单模式，默认仅允许 `http://localhost:3000`。

### 问题：错误信息泄露

全局异常处理器和每个端点的 `try/except` 都返回 `str(e)`，可能暴露内部路径、数据库连接字符串或 API 密钥。

**修复方案：** 已修改为生产环境返回通用错误信息，开发环境才返回详细错误。

### 问题：/health 端点泄露运营情报

`/health` 返回各 LLM provider 的 `available`/`not_configured` 状态，帮助攻击者了解系统配置。

**修复方案：** 建议移除 provider 状态，仅返回 `{"status": "healthy"}`。

---

## 3. 依赖与打包（严重）

### 问题：requirements.txt 与 setup.py 严重不同步

setup.py 缺少约 15 个在 requirements.txt 中声明且实际使用的包：
- `openai`, `streamlit`, `plotly`, `networkx`, `matplotlib`, `numpy`, `langdetect`, `pytest`, `pytest-asyncio` 等

**影响：** 如果用户通过 `pip install .` 安装，运行时必然因缺少依赖而崩溃。

### 问题：缺少关键依赖

以下包在代码中被导入，但两个文件中均未声明：
- `redis`（`llm/cache_redis.py`）
- `sentence-transformers`（`tools/embedding.py`）
- `jinja2`（`prompts/template_loader.py`）
- `google-genai`（`utils/key_health.py` 导入 `google.genai`）

### 问题：声明了未使用的依赖

requirements.txt 中 pinned 但代码中从未导入：
- `deepseek==1.0.0`（未使用）
- `httpx==0.27.0`（未使用）
- `pydantic-settings==2.2.1`（未使用）
- `beautifulsoup4==4.12.3`（未使用）
- `lxml==5.2.2`（未使用）
- `pillow==10.4.0`（未使用）
- `pandas==2.2.2`（未使用）

### 问题：google-generativeai vs google-genai 冲突

`requirements.txt` 声明的是 `google-generativeai`（旧 API），但 `utils/key_health.py` 导入的是 `google.genai`（新 API，需 `google-genai` 包）。两者互不兼容。

**修复方案：** 已全面更新 requirements.txt 和 setup.py，移除未使用包，添加缺失包，统一版本声明。新增 `pyproject.toml` 作为单一可信源。

---

## 4. 测试质量（严重）

### 问题：零真实代码测试

8 个测试文件仅测试：
- `test_adapter/` 的 mock 适配器（不是真实代码）
- Schema 的构造函数（仅验证 Pydantic 模型能否实例化）

**以下核心模块完全无测试：**
- 所有 `pipelines/real/` 的 preprocess/postprocess 逻辑
- `llm/real/llm_router.py` 的熔断器、fallback、负载均衡
- `orchestrator/real/task_orchestrator.py` 的 trace_id 和 metrics
- 所有 `agents/` 的业务逻辑
- 所有 `intel/` 引擎（JSON 解析、regex fallback、提示词构建）
- 所有 `api/` 端点（无 FastAPI TestClient 测试）

### 问题：pytest.ini 配置不足

- 缺少 `asyncio_mode = auto`（使用 pytest-asyncio 必需）
- 缺少覆盖率配置
- 缺少 markers 定义

### 问题：pre-commit 配置弱

- Black 无行宽参数（默认 88，项目中很多代码使用 100+）
- Flake8 无配置
- 缺少 `mypy`、`isort/ruff`、`bandit`、`check-added-large-files`

**修复方案：** 已重写 `pytest.ini`、`.pre-commit-config.yaml`，新增 `pyproject.toml` 统一配置 Black/Ruff/mypy/pytest。

---

## 5. 代码质量（中等）

### 问题：asyncio.run() 反模式

`news_intel_engine.py:33` 和 `narrative_engine.py:49` 在同步方法中调用 `asyncio.run()`，这在 FastAPI 等异步环境中会崩溃（`RuntimeError: asyncio.run() cannot be called from a running event loop`）。

**修复方案：** 已将 `NewsIntelEngine.search_structured` 改为异步方法，移除 `asyncio.run()`。`NarrativeEngine.generate()` 已标记为废弃，调用方应直接使用 `generate_async()`。

### 问题：datetime.utcnow() 废弃警告

`schemas/real/__init__.py` 和 `schemas/test_adapter/__init__.py` 中大量使用 `datetime.utcnow()` 作为 Pydantic 默认值。Python 3.12 将废弃此方法。

**修复方案：** 建议统一替换为 `datetime.now(timezone.utc)`。

### 问题：egg-info 被 Git 跟踪

`fzq_ai_agent.egg-info/` 目录在 `.gitignore` 中已列入，但已被 git 跟踪，因此不会被忽略。

**修复方案：** 执行 `git rm -rf fzq_ai_agent.egg-info` 并从缓存中移除。

---

## 6. 已落实的具体修改清单

### 新增文件（放入 workspace）

| 文件 | 说明 |
|------|------|
| `pyproject.toml` | 统一配置：Black (100字符), Ruff, mypy, pytest |
| `AUDIT_REPORT.md` | 本报告 |

### 修改文件（已生成新版，见 workspace）

| 文件 | 修改内容 |
|------|----------|
| `requirements.txt` | 移除未使用包，添加缺失包，统一版本 |
| `setup.py` | 同步所有依赖，添加版本约束 |
| `pytest.ini` | 添加 asyncio_mode, coverage, markers, log_cli |
| `.pre-commit-config.yaml` | 添加 ruff, mypy, bandit, check-added-large-files, check-merge-conflict |
| `app.py` | 修复 CORS 为环境变量驱动，增加安全注释 |
| `api_server.py` | 修复错误处理为生产/开发模式区分，添加弃用注释 |
| `src/fzq_ai/config/__init__.py` | 修复 `json.load` → `yaml.safe_load`，移除 `load_dotenv()` |
| `src/fzq_ai/config.py` | 改为从 `config/__init__.py` 导入，避免重复加载 |
| `src/fzq_ai/intel/news_intel_engine.py` | 改为 `async def search_structured`，移除 `asyncio.run()` |
| `src/fzq_ai/intel/narrative_engine.py` | 废弃 `generate()` 同步方法，建议调用 `generate_async()` |

### 删除清单（建议执行）

```bash
# 死代码文件（根级）
git rm -f _fix_registry.py fix_utcnow.py cleanup_project.py nick_tui.py run_agent_demo.py

# 冲突的 FastAPI 应用
git rm -f api_server.py streamlit_app.py
# 注意：迁移 api_server.py 的独有端点 (/version, /pipelines) 到 app.py 后再删除

git rm -rf src/fzq_ai/api/app.py  # 重复初始化 FastAPI 的 bug

# 死代码目录（real/）
git rm -rf src/fzq_ai/schemas/real/
git rm -rf src/fzq_ai/pipelines/real/
git rm -rf src/fzq_ai/orchestrator/real/
git rm -rf src/fzq_ai/llm/real/
git rm -rf src/fzq_ai/task_registry/real/
git rm -rf src/fzq_ai/task_registry/test_adapter/
git rm -rf src/fzq_ai/task_registry/

# 被 git 跟踪但应忽略的目录
git rm -rf fzq_ai_agent.egg-info/
```

---

## 7. 后续建议（未在本次修改中落实）

### P1：测试补全
- 为 `NewsPipeline` 编写单元测试（mock `fetch_all_news` 和 `Router`）
- 为 `llm/real/llm_router.py` 编写熔断器、fallback 测试
- 为 `orchestrator/real/task_orchestrator.py` 编写编排测试
- 为 API 端点添加 FastAPI `TestClient` 测试

### P2：Schema 统一
- 将 `schemas/test_adapter/` 的 mock 逻辑改为 pytest fixtures
- 删除 `test_adapter/` 目录，所有测试直接使用根级 schemas

### P3：日志与监控
- 统一使用 `src/fzq_ai/logging/logger.py` 而非各模块自行 `import logging`
- 将全局异常处理器的错误日志写入文件/监控，而非仅返回客户端

### P4：CI/CD
- 在 `.github/workflows/python.yml` 中启用 ruff、mypy、pytest --cov
- 添加覆盖率阈值（如 60%）

### P5：文档同步
- `README.md` 中的项目结构与真实代码不一致（如 `fzq_ai/` 目录结构已变化）
- 更新 `README.md` 中提到的文件路径和模块名

---

## 附录：关键文件行号索引

| 问题 | 文件 | 行号 |
|------|------|------|
| json.load 读取 YAML | `src/fzq_ai/config/__init__.py` | 53 |
| asyncio.run 反模式 | `src/fzq_ai/intel/news_intel_engine.py` | 33 |
| asyncio.run 反模式 | `src/fzq_ai/intel/narrative_engine.py` | 49 |
| CORS 完全开放 | `api_server.py` | 55 |
| 错误信息泄露 | `api_server.py` | 101-114, 232-236 等 |
| 健康检查泄露配置 | `api_server.py` | 168-179 |
| 重复 load_dotenv | `src/fzq_ai/config.py` | 4 |
| 重复 load_dotenv | `src/fzq_ai/config/__init__.py` | 29 |
| 重复 load_dotenv | `src/fzq_ai/config/env.py` | 7 |
| 重复 load_dotenv | `api_server.py` | 23 |
| 重复 load_dotenv | `main.py` | 7 |
| 三处 FastAPI 初始化 | `app.py`, `api_server.py`, `src/fzq_ai/api/app.py` | 全局 |

---

*报告生成时间：2025-08-26*
*审计范围：代码架构、安全、依赖、测试、代码质量*
