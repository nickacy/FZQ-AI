# FZQ-AI 项目审计报告 v1.0

> 审计日期：2024-06-21  
> 审计范围：完整代码库（`C:\Users\nicka\FZQ-AI-WORKSPACE\FZQ-AI`）  
> 审计目标：识别结构、代码、一致性、测试、文档层面的问题，给出可执行的修复清单

---

## 一、执行摘要（Executive Summary）

| 维度 | 状态 | 严重程度 |
|------|------|----------|
| 项目结构 | 存在命名冲突和空文件 | 🔴 高 |
| 代码质量 | Pydantic V1 弃用、重复类 | 🔴 高 |
| Schema-Prompt 对齐 | 4 个 Pipeline 中有 3 个不一致 | 🔴 高 |
| 测试覆盖 | 88 测试通过，但 warning 未清理 | 🟡 中 |
| 文档 | 术语表和对齐报告已生成 | 🟢 低（已修复） |

**核心发现：**
1. 根目录存在 `fzq_ai/` 与 `src/fzq_ai/` 同名包冲突，会导致导入歧义
2. 4 个 `zh_tasks` Schema 使用 Pydantic V1 `@validator`（已弃用，V3 将移除）
3. `zh_opinion_landscape` 的 Prompt 与 Schema 字段名大面积不一致（30.8% 对齐率）
4. 存在两个不同版本的 `IntelStore`（JSON 文件版 vs SQLite 版）
5. 34 个空文件、多个大型无用文本文件（tree.txt 等）

---

## 二、问题详情（Issue Details）

### 2.1 🔴 结构问题（P0 — 阻塞生产）

#### 2.1.1 根目录 `fzq_ai/` 与 `src/fzq_ai/` 包名冲突

**问题：** 根目录存在 `fzq_ai/` 子目录，与 `src/fzq_ai/` 同名。Python 的模块导入机制会优先找到第一个匹配的包名，导致行为不可预测。

**影响：** 运行 `python -c "import fzq_ai"` 时，取决于当前工作目录和 `PYTHONPATH`，可能导入根目录的 `fzq_ai`（几乎为空）而非 `src/fzq_ai/`（完整代码）。

**当前状态：**
```
fzq_ai/
  └── quality/
      ├── deepseek_struct_opt.py       ← 18 KB（与 src/fzq_ai/quality/ 版本不同）
      └── deepseek_struct_opt_v92.py   ← 与 deepseek_struct_opt.py 内容完全相同
```

**建议：** 删除根目录 `fzq_ai/`，将内容合并到 `src/fzq_ai/`。

---

#### 2.1.2 根目录遗留文件和目录

**遗留目录：**

| 目录 | 内容 | 状态 |
|------|------|------|
| `prompts/` | 5 个 Jinja2 模板 | 旧版 Prompt，未使用 |
| `schemas/` | `pipeline_outputs.py`（旧版 Schema） | 旧版，未使用 |
| `ui/` | `dashboard.py`, `dashboard_stub.py`, `ui_app.py` | 旧版 UI，未使用 |
| `tui/` | `dashboard.py`, `news_view.py` | 旧版 TUI，未使用 |
| `build_engine/` | 7 个文件 | 项目构建工具，已过时 |
| `tools/` | `__init__.py`, `_convert_to_utf8.py`, `_encoding_check.py` | 工具脚本 |
| `agent/` | 空 `__init__.py` + 空子目录 | 完全未使用 |
| `data/` | 空 `__init__.py` + 缓存数据 | 运行时数据，非源码 |
| `logs/` | 空 `__init__.py` | 未使用 |
| `tests_old/` | 13 个旧测试文件 | 已过时 |

**大型无用文件：**

| 文件 | 大小 | 说明 |
|------|------|------|
| `tree.txt` | 3.6 MB | 旧 `tree` 命令输出 |
| `project_structure.txt` | 2.9 MB | 旧结构文档 |
| `project_structure_raw.txt` | 2.9 MB | 旧结构文档 |
| `structure.txt` | 2.6 MB | 旧结构文档 |
| `tmp_fix_and_test.py` | 17 KB | 临时脚本 |
| `tmp_test_import.py` | 14 KB | 临时脚本 |

**建议：** 删除 `agent/`、`logs/`、`tools/`（根目录）、`tests_old/`、`tree.txt`、`project_structure*.txt`、`structure.txt`、`tmp_*.py`。

---

#### 2.1.3 空文件清单

**根目录（0 字节）：**
```
./__init__.py
./agent.py
./memory.py
./tools.py
./allfiles.txt
```

**`src/fzq_ai/` 中（0 字节）：**
```
src/__init__.py
src/fzq_ai/api/__init__.py
src/fzq_ai/cache/__init__.py
src/fzq_ai/cli/__init__.py
src/fzq_ai/domain/__init__.py
src/fzq_ai/intel/__init__.py
src/fzq_ai/logging/__init__.py
src/fzq_ai/metrics/__init__.py
src/fzq_ai/orchestrator/__init__.py
src/fzq_ai/prompts/__init__.py    ← 之前写入但可能已丢失
```

**注意：** 空 `__init__.py` 在 Python 3.3+ 中不再是必需的（PEP 420），但为了保持向后兼容，建议保留并添加基础导出内容。纯空的 `__init__.py` 是浪费但不致命。但 `src/__init__.py` 必须保留，因为 `src/` 是 `sys.path` 的搜索根。

---

#### 2.1.4 空 Agent 任务文件

```
src/fzq_ai/agents/tasks/multisource_merge_agent.py  ← 0 字节
src/fzq_ai/agents/tasks/opinion_agent.py             ← 0 字节
src/fzq_ai/agents/tasks/risk_scan_agent.py           ← 0 字节
```

---

### 2.2 🔴 代码质量问题（P0 — 技术债）

#### 2.2.1 Pydantic V1 `@validator` 已弃用（4 个文件）

**影响文件：**
```
src/fzq_ai/schemas/zh_tasks/zh_policy_brief.py
src/fzq_ai/schemas/zh_tasks/zh_risk_scan.py
src/fzq_ai/schemas/zh_tasks/zh_opinion_landscape.py
src/fzq_ai/schemas/zh_tasks/zh_multisource_merge.py
```

**错误模式：**
```python
from pydantic import BaseModel, Field, validator  # V1 风格
...
@validator("evidence_span")
def evidence_must_not_be_empty(cls, v):
    ...
```

**应改为 Pydantic V2 风格：**
```python
from pydantic import BaseModel, Field, field_validator  # V2 风格
...
@field_validator("evidence_span")
def evidence_must_not_be_empty(cls, v):
    ...
```

**影响：** 在 Pydantic V3 中，`@validator` 将被移除。当前每次运行测试都会输出 7 条 `PydanticDeprecatedSince20` warning。

---

#### 2.2.2 `IntelStore` 重复实现

**两个不同版本：**
- `src/fzq_ai/storage/intel_store.py` — 46 行，JSON 文件存储，简单版
- `src/fzq_ai/store/intel_store.py` — 132 行，SQLite 存储，完整版（v2.7）

**问题：** 两个类同名 `IntelStore` 但实现完全不同。如果两个模块同时被导入，后导入的会覆盖先导入的，导致行为不可预测。

**建议：** 保留 `src/fzq_ai/store/intel_store.py`（功能更完整，有 SQLite 支持），将 `src/fzq_ai/storage/intel_store.py` 标记为弃用或删除。统一导入路径为 `from fzq_ai.store.intel_store import IntelStore`。

---

#### 2.2.3 重复文件：`deepseek_struct_opt.py` 与 `deepseek_struct_opt_v92.py`

**位置：** `fzq_ai/quality/`

**问题：** 两个文件内容完全相同（MD5 一致），浪费空间且增加维护负担。

**建议：** 删除 `deepseek_struct_opt_v92.py`，保留 `deepseek_struct_opt.py`。若需要版本控制，使用 Git 版本历史而非文件复制。

---

### 2.3 🔴 Schema-Prompt 一致性问题（P0 — 功能失效）

详见 `docs/minimax_alignment_report.md` 和 `docs/actionable_suggestions.md`。

#### 2.3.1 `zh_opinion_landscape` — 30.8% 对齐率（最严重）

| Prompt 字段名 | Schema 字段名 | 状态 |
|-------------|--------------|------|
| `camps` | `clusters` | ❌ 不一致 |
| `camp_id` | `cluster_id` | ❌ 不一致 |
| `share` | `size` | ❌ 不一致 |
| `core_claim` | `key_arguments` | ❌ 不一致 |
| `frame_analysis` | `key_frames` | ❌ 不一致 |
| `used_by` | `description` | ❌ 不一致 |
| `effect` | `evidence_span` | ❌ 不一致 |
| `key_nodes` | `influencers` | ❌ 不一致 |
| `author` | `name` | ❌ 不一致 |
| `camp` | `stance` | ❌ 不一致 |
| `heat` | `heat_trend` | ❌ 不一致（类型变化） |

**枚举值不一致：**
- `stance`: Prompt 用 "复杂"，Schema 用 "分裂" → 建议统一为 "复杂"
- `sentiment`: Prompt 用 "混合"，Schema 用 "分化" → 建议统一为 "混合"

---

#### 2.3.2 `zh_risk_scan` — 75% 对齐率

**Prompt 中缺失的 Schema 字段：**
- `overall_risk_level`（整体风险等级）
- `suggested_actions`（全局行动建议）
- `confidence`（全局置信度）

---

#### 2.3.3 `zh_multisource_merge` — 66.7% 对齐率

**Prompt 中缺失的 Schema 字段：**
- `missing_sources`（缺失视角）
- `conflict_sources`（冲突视角）
- `evidence_map`（全局证据映射）

**枚举值不一致：**
- `dimension`: Prompt 包含 "其他"，Schema 不包含 → 建议 Schema 增加 "其他"

---

### 2.4 🟡 测试覆盖问题（P1）

#### 2.4.1 测试文件分布

| 测试文件 | 行数 | 测试内容 |
|----------|------|----------|
| `tests/test_api.py` | 124 | API 层测试 |
| `tests/test_formatter.py` | 71 | 格式化测试 |
| `tests/test_llm_router.py` | 95 | LLM 路由测试 |
| `tests/test_orchestrator.py` | 67 | Orchestrator 测试 |
| `tests/test_pipelines.py` | 146 | Pipeline 测试 |
| `tests/test_schemas.py` | 167 | Schema 测试 |
| `tests/conftest.py` | 5 | 路径配置（新增） |

**总测试数：** 88 个，全部通过。

**问题：**
1. 没有针对 `zh_policy_brief`, `zh_risk_scan`, `zh_opinion_landscape`, `zh_multisource_merge` 的 Schema 测试
2. 没有针对 `KimiInterpreter` 的测试
3. 没有针对 `SchemaValidator` 的测试
4. `tests_old/` 目录中有 13 个旧测试，未清理

#### 2.4.2 Pydantic Deprecation Warnings

每次运行测试输出 7 条 `PydanticDeprecatedSince20` warning：
```
PydanticDeprecatedSince20: Pydantic V1 style @validator validators are deprecated.
You should migrate to Pydantic V2 style @field_validator validators
```

---

### 2.5 🟡 导入路径问题（P1）

#### 2.5.1 `tests/conftest.py` 路径修复

**问题：** 之前因为包结构问题，我创建了 `tests/conftest.py`：
```python
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
```

**这是临时修复，不是正确做法。** 正确的做法应该是：
1. 使用 `pip install -e .`（editable install）安装包
2. 确保 `setup.py` 正确指向 `src/` 目录

**当前 `setup.py`：**
```python
from setuptools import setup, find_packages
setup(name="fzq_ai_agent", version="0.1", packages=find_packages())
```

**问题：** `find_packages()` 默认从当前目录查找，不会自动找到 `src/` 下的包。需要改为 `find_packages(where="src")`。

---

## 三、修复清单（Action Items）

### 3.1 🔴 P0 修复（立即执行，阻塞生产）

| # | 任务 | 文件 | 操作 |
|---|------|------|------|
| 1 | **删除根目录 `fzq_ai/`** | `fzq_ai/` | 将 `quality/deepseek_struct_opt.py` 移动到 `src/fzq_ai/quality/`，然后删除整个 `fzq_ai/` 目录 |
| 2 | **修复 Pydantic V1→V2** | `zh_tasks/*.py`（4 个文件） | 将 `from pydantic import ... validator` 改为 `field_validator`，更新装饰器语法 |
| 3 | **统一 `zh_opinion_landscape` 字段** | `prompts/zh/zh_opinion_landscape.txt` | 重写输出格式，字段名与 Schema 对齐（camps→clusters, frame_analysis→key_frames 等） |
| 4 | **统一枚举值** | `schemas/zh_tasks/zh_opinion_landscape.py` | 将 `stance` 的 "分裂" 改为 "复杂"，`sentiment` 的 "分化" 改为 "混合" |
| 5 | **统一 `zh_risk_scan` 字段** | `prompts/zh/zh_risk_scan.txt` | 在输出格式中增加 `overall_risk_level`, `suggested_actions`, `confidence` |
| 6 | **统一 `zh_multisource_merge` 字段** | `prompts/zh/zh_multisource_merge.txt` | 在输出格式中增加 `missing_sources`, `conflict_sources`, `evidence_map` |
| 7 | **统一 `dimension` 枚举** | `schemas/zh_tasks/zh_multisource_merge.py` | 在 `dimension` 的 `Literal` 中增加 "其他" |
| 8 | **合并 `IntelStore`** | `storage/intel_store.py`, `store/intel_store.py` | 删除 `storage/intel_store.py`，保留 `store/intel_store.py`，更新所有导入 |

### 3.2 🟡 P1 修复（本周执行）

| # | 任务 | 文件 | 操作 |
|---|------|------|------|
| 9 | **清理空文件** | 根目录 `*.py`（agent.py, memory.py, tools.py 等） | 删除空文件 |
| 10 | **清理遗留目录** | `agent/`, `logs/`, `tools/`（根目录）, `tests_old/` | 删除完全未使用的目录 |
| 11 | **清理大型无用文件** | `tree.txt`, `project_structure*.txt`, `structure.txt`, `tmp_*.py` | 删除 |
| 12 | **清理重复文件** | `fzq_ai/quality/deepseek_struct_opt_v92.py` | 删除（与另一个文件内容相同） |
| 13 | **修复 `setup.py`** | `setup.py` | 改为 `find_packages(where="src")` 或 `packages=find_packages("src")` |
| 14 | **修复 `tests/conftest.py`** | `tests/conftest.py` | 使用 `pip install -e .` 替代 `sys.path.insert` |
| 15 | **填充空 `__init__.py`** | `src/fzq_ai/api/__init__.py` 等（9 个） | 添加基础导出或删除（如果目录不需要被导入） |
| 16 | **删除/填充空 Agent 文件** | `agents/tasks/*_agent.py`（3 个） | 删除或填充为 stub |

### 3.3 🟢 P2 修复（下周执行）

| # | 任务 | 文件 | 操作 |
|---|------|------|------|
| 17 | **添加 Schema 测试** | `tests/test_zh_schemas.py` | 为 4 个 zh_tasks Schema 编写测试 |
| 18 | **添加 Interpreter 测试** | `tests/test_interpreter.py` | 为 `KimiInterpreter` 和 `SchemaValidator` 编写测试 |
| 19 | **统一时间戳格式** | 所有 Prompt | 将所有时间戳要求统一为 `YYYY-MM-DD` 或 ISO 8601 |
| 20 | **统一 confidence 分级** | 所有 Prompt | 在 `docs/glossary.md` 定义统一标准，在所有 Prompt 中引用 |
| 21 | **统一降级处理格式** | 所有 Prompt | 定义统一降级 JSON 结构 |
| 22 | **清理 `__pycache__`** | 所有目录 | 删除编译缓存（已在 `.gitignore` 中） |
| 23 | **移除 `build_engine/`** | `build_engine/` | 项目构建工具已过时，移至存档或删除 |
| 24 | **移除旧版 `prompts/`（根目录）** | `prompts/*.jinja2` | 旧版 Jinja2 模板，未使用 |
| 25 | **移除旧版 `schemas/`（根目录）** | `schemas/pipeline_outputs.py` | 旧版 Schema，未使用 |
| 26 | **移除旧版 `ui/` 和 `tui/`** | `ui/`, `tui/` | 旧版 UI，未使用（如果将来需要，从历史恢复） |
| 27 | **Git 清理** | `.git/` | 运行 `git gc` 清理历史（.git 67MB，占 78% 仓库大小） |
| 28 | **Commit Message 规范** | 未来 | 使用描述性提交消息，避免所有提交都叫 "git pull" |

---

## 四、附录：修复命令速查

### 4.1 删除命令（执行前请确认已备份）

```bash
# 根目录空文件
rm -f __init__.py agent.py memory.py tools.py allfiles.txt

# 根目录遗留目录
rm -rf agent/ logs/ tools/ tests_old/ build_engine/

# 根目录旧版 prompts/schemas/ui/tui
rm -rf prompts/ schemas/ ui/ tui/

# 根目录 fzq_ai/（先移动文件）
cp fzq_ai/quality/deepseek_struct_opt.py src/fzq_ai/quality/
rm -rf fzq_ai/

# 大型无用文件
rm -f tree.txt project_structure.txt project_structure_raw.txt structure.txt
rm -f tmp_fix_and_test.py tmp_test_import.py

# 空 Agent 文件
rm -f src/fzq_ai/agents/tasks/multisource_merge_agent.py
rm -f src/fzq_ai/agents/tasks/opinion_agent.py
rm -f src/fzq_ai/agents/tasks/risk_scan_agent.py

# 重复 IntelStore（保留 store/ 版本）
rm -f src/fzq_ai/storage/intel_store.py
# 如果 storage/ 目录变空，删除目录
rmdir src/fzq_ai/storage/ 2>/dev/null || true

# Git 清理
git gc --aggressive --prune=now
```

### 4.2 Pydantic V2 迁移模板

对每个 `zh_tasks/*.py` 文件执行：

```python
# 修改前
from pydantic import BaseModel, Field, validator

@validator("field_name")
def validate(cls, v):
    ...

# 修改后
from pydantic import BaseModel, Field, field_validator

@field_validator("field_name")
def validate(cls, v):
    ...
```

### 4.3 `setup.py` 修复

```python
from setuptools import setup, find_packages

setup(
    name="fzq_ai_agent",
    version="0.1",
    packages=find_packages(where="src"),  # 关键修改
    package_dir={"": "src"},              # 关键修改
    install_requires=[
        # 添加依赖项
        "pydantic>=2.0",
        "fastapi",
        "uvicorn",
        "requests",
        "aiohttp",
        "feedparser",
        "pyyaml",
        "python-dotenv",
    ],
)
```

### 4.4 `tests/conftest.py` 正确写法

```python
# 如果使用 pip install -e .，不需要修改 sys.path
# 只需确保 pytest 能找到包
```

或保留当前写法（如果尚未安装包）：

```python
import sys
from pathlib import Path

# 将 src/ 添加到路径
src_dir = Path(__file__).resolve().parents[1] / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
```

---

> 文档版本：v1.0  
> 审计者：KIMI（文档与提示词优化专家）  
> 生成时间：2024-06-21
