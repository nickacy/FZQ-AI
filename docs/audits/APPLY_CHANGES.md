# 如何应用审计修改

本目录包含 FZQ-AI 项目的审计修复文件。以下是应用这些修改的步骤。

## 修改文件清单

### 新增文件（建议直接复制到项目根目录）

| 文件 | 说明 |
|------|------|
| `pyproject.toml` | 统一工具配置：Black (100字符), Ruff, mypy, pytest, coverage, bandit |
| `AUDIT_REPORT.md` | 完整审计报告 |
| `DELETION_GUIDE.md` | 死代码删除指南 |

### 修改文件（替换原文件）

| 文件 | 修改内容 |
|------|----------|
| `requirements.txt` | 移除 7 个未使用包，添加 4 个缺失包，同步 setup.py |
| `setup.py` | 同步所有依赖，添加 extras_require[dev] |
| `pytest.ini` | 添加 asyncio_mode, strict-markers, markers, filterwarnings |
| `.pre-commit-config.yaml` | 添加 ruff, mypy, bandit, check-added-large-files, check-merge-conflict |
| `app.py` | CORS 改为环境变量驱动，移除 `allow_origins=["*"]` |
| `api_server.py` | 错误处理改为生产/开发模式区分；添加 DEPRECATED 注释；修复 CORS |
| `src/fzq_ai/config/__init__.py` | 修复 `json.load` → `yaml.safe_load`；移除 `load_dotenv()`；添加 `yaml` 导入 |
| `src/fzq_ai/config.py` | 改为从 `config/__init__.py` 导入，避免重复加载 |
| `src/fzq_ai/intel/news_intel_engine.py` | `search_structured` 改为 `async`；移除 `asyncio.run()`；添加废弃同步方法 |
| `src/fzq_ai/intel/narrative_engine.py` | `generate()` 标记为废弃；添加 DeprecationWarning；建议调用 `generate_async()` |

## 应用步骤

### 步骤 1：备份原项目

```bash
cd C:\Users\nicka\FZQ-AI-WORKSPACE
cp -r FZQ-AI FZQ-AI-backup-$(date +%Y%m%d)
```

### 步骤 2：复制新增文件

```bash
cd C:\Users\nicka\FZQ-AI-WORKSPACE\FZQ-AI
cp "C:\Users\nicka\Documents\kimi\workspace\FZQ-AI-audit\pyproject.toml" .
cp "C:\Users\nicka\Documents\kimi\workspace\FZQ-AI-audit\AUDIT_REPORT.md" .
cp "C:\Users\nicka\Documents\kimi\workspace\FZQ-AI-audit\DELETION_GUIDE.md" .
```

### 步骤 3：替换修改文件

```bash
cd C:\Users\nicka\FZQ-AI-WORKSPACE\FZQ-AI

cp "C:\Users\nicka\Documents\kimi\workspace\FZQ-AI-audit\requirements.txt" .
cp "C:\Users\nicka\Documents\kimi\workspace\FZQ-AI-audit\setup.py" .
cp "C:\Users\nicka\Documents\kimi\workspace\FZQ-AI-audit\pytest.ini" .
cp "C:\Users\nicka\Documents\kimi\workspace\FZQ-AI-audit\.pre-commit-config.yaml" .

cp "C:\Users\nicka\Documents\kimi\workspace\FZQ-AI-audit\app.py" .
cp "C:\Users\nicka\Documents\kimi\workspace\FZQ-AI-audit\api_server.py" .

cp "C:\Users\nicka\Documents\kimi\workspace\FZQ-AI-audit\src\fzq_ai\config.py" src\fzq_ai\
cp "C:\Users\nicka\Documents\kimi\workspace\FZQ-AI-audit\src\fzq_ai\config\__init__.py" src\fzq_ai\config\
cp "C:\Users\nicka\Documents\kimi\workspace\FZQ-AI-audit\src\fzq_ai\intel\news_intel_engine.py" src\fzq_ai\intel\
cp "C:\Users\nicka\Documents\kimi\workspace\FZQ-AI-audit\src\fzq_ai\intel\narrative_engine.py" src\fzq_ai\intel\
```

### 步骤 4：安装新依赖

```bash
cd C:\Users\nicka\FZQ-AI-WORKSPACE\FZQ-AI
pip install -r requirements.txt
# 或安装开发依赖
pip install -e ".[dev]"
```

### 步骤 5：重新安装 pre-commit hooks

```bash
cd C:\Users\nicka\FZQ-AI-WORKSPACE\FZQ-AI
pre-commit uninstall
pre-commit install
```

### 步骤 6：运行测试验证

```bash
cd C:\Users\nicka\FZQ-AI-WORKSPACE\FZQ-AI
python -m pytest tests/ -v --tb=short
```

### 步骤 7：按 DELETION_GUIDE.md 清理死代码

阅读 `DELETION_GUIDE.md` 并执行删除操作。

---

## 环境变量更新建议

`.env` 文件建议添加以下变量：

```bash
# CORS 白名单（逗号分隔）
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8501

# 运行环境（影响错误信息详细程度）
ENV=development
```

---

*如有疑问，请查阅 `AUDIT_REPORT.md` 获取详细的问题分析和修复原理。*
