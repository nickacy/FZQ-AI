# FZQ‑AI Pipeline 中心 & 版本共存设计方案（KIMI 输出）

> 版本：v7.0  
> 目标：构建 Pipeline 注册中心，支持版本共存，零破坏现有代码，预留插件化扩展

---

## 1. 总体设计思路

### 1.1 当前问题诊断

| 问题 | 现状 | 影响 |
|------|------|------|
| **硬编码导入** | Orchestrator 直接 `from fzq_ai.pipelines.real import NewsPipeline` | 新增/切换 Pipeline 必须改代码 |
| **无版本管理** | 新旧两套架构（`pipelines/` vs `pipelines/real/`）并行，无统一标识 | 无法 A/B 测试、灰度发布 |
| **字符串映射无法执行** | `SCENARIOS` 字典用 `"news"` 字符串指代 Pipeline，但无法实例化 | API 的 `/pipelines` 端点调用不存在的 `list_pipelines()` |
| **测试/生产切换繁琐** | 需手动改 import 路径切到 `test_adapter` | 容易遗漏，切换成本高 |
| **无动态发现** | 新增 Pipeline 必须改 Orchestrator 的 `__init__` | 违反开闭原则 |

### 1.2 设计原则

| 原则 | 说明 |
|------|------|
| **可选层（Opt-in）** | Registry 是附加层，不强制所有 Pipeline 必须注册。未注册的 Pipeline 行为完全不变。 |
| **零破坏兼容** | 现有 `BasePipeline` 子类、直接实例化、旧 Orchestrator 的 `self.news = NewsPipeline()` 全部继续可用。 |
| **命名即版本** | Pipeline 名称自带版本信息：`news_v1` / `news_v2` / `news_v3_exp`，无需额外版本表。 |
| **鸭子类型协议** | 不强制继承特定基类。任何有 `run()` 或 `run_async()` 的类都能注册。 |
| **轻量级** | 仅用标准库（`importlib.metadata` / `pkg_resources`）+ 纯 Python 字典，无外部依赖。 |
| **插件预留** | 设计 entry_points 接口，但不强制现在实现。外部包未来可通过 `pip install` 自动注册。 |

### 1.3 架构图

```
+-------------------------------------------------------------+
|                     API / CLI / Dashboard                   |
|  orchestrator.get_pipeline("news")  /  "news@v2"  /  "news@latest" |
+-------------------------+-----------------------------------+
                          |
+-------------------------v-----------------------------------+
|              PipelineRegistry（单例）                        |
|  +--------------+  +--------------+  +------------------+   |
|  |  _registry   |  |  _defaults   |  |  entry_points   |   |
|  |  name->Entry |  | family->name  |  | （预留加载）     |   |
|  +--------------+  +--------------+  +------------------+   |
|  - register() 装饰器                                          |
|  - get() 支持 @version 语法                                   |
|  - list_family() / list_by_tag()                             |
|  - snapshot() 供 Dashboard 展示                               |
+-------------------------+-----------------------------------+
                          |
        +-----------------+------------+
        |                              |
   +----v----+  +-----------------+  +----------------+
   | 旧架构   |  | 新架构           |  | 外部插件        |
   |BasePipeline| |  plain  class   |  | entry_points   |
   | 子类     |  +-----------------+  +----------------+
   +---------+
```

---

## 2. PipelineRegistry 设计

### 2.1 核心类定义

**文件：** `fzq_ai/pipelines/registry.py`

```python
class PipelineRegistry:
    """Pipeline 统一注册中心（单例，全局唯一）。"""

    # 全局注册表：注册名 -> PipelineEntry
    _registry: Dict[str, PipelineEntry] = {}
    # 家族默认版本：family -> 注册名
    _defaults: Dict[str, str] = {}
    # entry_points 是否已加载
    _entry_points_loaded: bool = False
```

### 2.2 PipelineEntry -- 注册条目（含元数据）

```python
@dataclass
class PipelineEntry:
    """Pipeline 注册条目。包含类、元数据、版本信息。"""

    name: str                # 注册名，如 "news_v2"
    pipeline_class: Type[Any]  # Pipeline 类
    family: str = ""        # 所属家族，如 "news"（从 name 自动推断）
    version: str = ""       # 版本号，如 "v2"（从 name 自动推断）
    is_experimental: bool = False  # 是否实验版本
    description: str = ""   # 描述
    input_schema: Optional[str] = None   # 输入 schema 类型
    output_schema: Optional[str] = None    # 输出 schema 类型
    tags: List[str] = field(default_factory=list)  # 标签
    dependencies: List[str] = field(default_factory=list)  # 依赖
    registered_at: float = field(default_factory=time.time)  # 注册时间
    metadata: Dict[str, Any] = field(default_factory=dict)    # 额外元数据
```

**自动解析 family/version：**

| 注册名 | family | version | 说明 |
|--------|--------|---------|------|
| `news_v2` | `news` | `v2` | 标准版本 |
| `news_v3_exp` | `news` | `v3_exp` | 实验版本 |
| `risk_v1` | `risk` | `v1` | 标准版本 |
| `daily_report` | `daily_report` | `""` | 无版本号（视为 v0） |
| `daily_report_v2` | `daily_report` | `v2` | 标准版本 |

### 2.3 register 装饰器

```python
@PipelineRegistry.register(
    "news_v2",
    description="News analysis pipeline v2 with multi-source fetching",
    tags=["news", "analysis", "realtime"],
    dependencies=["news_fetcher"],  # 依赖外部工具
    set_default=True,               # 设为 news family 的默认版本
)
class NewsPipeline:
    async def run(self, pipeline_input: PipelineInput) -> PipelineOutput:
        ...
```

**装饰器特性：**

1. **验证警告**：注册时检查类是否有 `run()` 或 `run_async()`，无则警告但不阻止。
2. **自动设置默认**：若 `set_default=True`，或该 family 尚无默认版本，自动设为默认。
3. **元数据附加**：将 `PipelineEntry` 附加到类属性 `_pipeline_entry`，方便自省。
4. **不破坏类**：装饰器返回原类，不影响继承链和 MRO。

### 2.4 get 方法（含版本解析）

```python
# 精确获取
PipelineRegistry.get("news_v2")           # -> NewsPipeline 类

# 获取默认版本
PipelineRegistry.get("news")              # -> news family 的默认版本

# @version 语法
PipelineRegistry.get("news@v2")           # -> 等价于 "news_v2"
PipelineRegistry.get("news@latest")       # -> 该 family 最新版本（按版本号排序）
PipelineRegistry.get("news@default")      # -> 该 family 默认版本

# 获取完整元数据
entry = PipelineRegistry.get_entry("news_v2")
print(entry.family)        # "news"
print(entry.version)       # "v2"
print(entry.is_experimental)  # False
print(entry.description)   # "News analysis pipeline v2..."
```

**版本号排序规则：**

```python
# "latest" 解析逻辑：
# v10 > v9 > v2 > v1
# 实验版本排在同号稳定版本之后：v2 > v2_exp
candidates = ["news_v1", "news_v2", "news_v2_exp", "news_v10"]
# latest -> "news_v10"（数字最大）
```

### 2.5 工厂函数

```python
from fzq_ai.pipelines.registry import create_pipeline

# 按名称创建实例（自动解析版本）
pipeline = create_pipeline("news_v2", llm_router=router)
pipeline = create_pipeline("news@latest", llm_router=router)
pipeline = create_pipeline("news", llm_router=router)  # 默认版本
```

---

## 3. 版本共存机制

### 3.1 命名规范

```
{family}_{version}
```

- **family**：Pipeline 功能家族，如 `news`, `risk`, `sentiment`, `scenario`, `daily_report`
- **version**：版本标识，格式为 `v数字` 或 `v数字_exp`

**推荐命名：**

| 场景 | 命名示例 | 说明 |
|------|----------|------|
| 稳定版 | `news_v1` | 生产环境使用 |
| 当前主力 | `news_v2` | 默认版本 |
| 实验版 | `news_v3_exp` | 新功能验证，不自动设为默认 |
| 无版本 | `daily_report` | 向后兼容，family 即名 |

### 3.2 默认版本解析规则

```python
# 1. 显式指定版本（最高优先级）
PipelineRegistry.get("news@v2")      # -> news_v2

# 2. 精确名称匹配
PipelineRegistry.get("news_v2")      # -> news_v2

# 3. family 默认版本
PipelineRegistry.get("news")         # -> 该 family 默认版本（如 news_v2）

# 4. 最新版本
PipelineRegistry.get("news@latest")  # -> 该 family 版本号最大的
```

**默认版本设置策略：**

```python
# 装饰器注册时显式设置
@PipelineRegistry.register("news_v2", set_default=True)
class NewsPipeline: ...

# 或程序化设置
PipelineRegistry.set_default("news", "news_v2")

# 查看当前默认
print(PipelineRegistry.get_default_name("news"))  # "news_v2"
```

### 3.3 版本共存示例

```python
# 三个版本共存
@PipelineRegistry.register("news_v1")
class NewsPipelineV1: ...

@PipelineRegistry.register("news_v2", set_default=True)
class NewsPipelineV2: ...

@PipelineRegistry.register("news_v3_exp")
class NewsPipelineV3Exp: ...

# 不同场景使用不同版本
stable = create_pipeline("news_v1")           # 稳定版
current = create_pipeline("news")             # 默认版（v2）
experimental = create_pipeline("news@v3")      # 实验版
latest = create_pipeline("news@latest")       # 最新版（v3_exp）

# Dashboard 展示所有版本
for family in PipelineRegistry.list_families():
    info = PipelineRegistry.get_family_info(family)
    print(f"Family: {family}")
    print(f"  Default: {info['default']}")
    print(f"  Versions: {info['versions']}")
    print(f"  Count: {info['count']}")
```

### 3.4 版本切换（A/B 测试场景）

```python
# 配置文件（如 config.yaml）控制版本
PIPELINE_VERSIONS = {
    "news": "news_v2",      # 当前主力
    # "news": "news_v3_exp", # 灰度测试时切到实验版
}

# Orchestrator 动态切换
class TaskOrchestrator:
    def __init__(self, config=None):
        self._config = config or {}

    def get_pipeline(self, family: str):
        version = self._config.get(family)  # 如 "news_v2"
        return create_pipeline(version or family)
```

---

## 4. 与 Orchestrator 集成方案

### 4.1 当前 Orchestrator（修改前）

```python
# fzq_ai/orchestrator/real/task_orchestrator.py
from fzq_ai.pipelines.real import (
    NewsPipeline, NarrativePipeline, RiskPipeline,
    SentimentPipeline, ScenarioPipeline, DailyReportPipeline,
)

class TaskOrchestrator:
    def __init__(self):
        self.news_pipeline = NewsPipeline()
        self.narrative_pipeline = NarrativePipeline()
        self.risk_pipeline = RiskPipeline()
        self.sentiment_pipeline = SentimentPipeline()
        self.scenario_pipeline = ScenarioPipeline()
        self.daily_report_pipeline = DailyReportPipeline()
```

### 4.2 集成后 Orchestrator（修改后）

```python
# fzq_ai/orchestrator/real/task_orchestrator.py
from fzq_ai.pipelines.registry import PipelineRegistry, create_pipeline

class TaskOrchestrator:
    """v7.0: 通过 Registry 获取 Pipeline，支持版本切换。"""

    def __init__(self, llm_router=None, pipeline_versions: dict = None):
        self._llm_router = llm_router
        self._versions = pipeline_versions or {}  # 如 {"news": "news_v3_exp"}

        # 通过 Registry 获取（支持版本覆盖）
        self.news_pipeline = self._get_pipeline_instance("news")
        self.narrative_pipeline = self._get_pipeline_instance("narrative")
        self.risk_pipeline = self._get_pipeline_instance("risk")
        self.sentiment_pipeline = self._get_pipeline_instance("sentiment")
        self.scenario_pipeline = self._get_pipeline_instance("scenario")
        self.daily_report_pipeline = self._get_pipeline_instance("daily_report")

    def _get_pipeline_instance(self, family: str):
        """按 family 获取 Pipeline 实例，支持版本覆盖。"""
        # 1. 检查是否有显式版本配置
        version = self._versions.get(family)
        name = f"{family}@{version}" if version else family
        # 2. 通过 Registry 获取并实例化
        return create_pipeline(name, llm_router=self._llm_router)

    # 新增：动态切换版本（运行时）
    def set_pipeline_version(self, family: str, version: str):
        """运行时切换 Pipeline 版本。"""
        self._versions[family] = version
        # 重新实例化
        attr_name = f"{family}_pipeline"
        if hasattr(self, attr_name):
            setattr(self, attr_name, self._get_pipeline_instance(family))
```

### 4.3 兼容性说明

| 调用方式 | 修改前 | 修改后 | 兼容性 |
|----------|--------|--------|--------|
| 直接实例化 | `NewsPipeline()` | `NewsPipeline()` | 不变 |
| Orchestrator 属性 | `orch.news_pipeline` | `orch.news_pipeline` | 不变 |
| 旧 Orchestrator | `TaskOrchestrator()` | `TaskOrchestrator()` | 行为不变（无版本参数时） |
| 版本指定 | 不支持 | `TaskOrchestrator(pipeline_versions={"news": "v2"})` | 新增，不破坏旧调用 |
| Registry 获取 | 不支持 | `PipelineRegistry.get("news")()` | 新增 |
| 字符串转实例 | 不支持 | `create_pipeline("news@v2")` | 新增 |

**关键保证：**

1. 旧 `TaskOrchestrator()` 无参数调用 -> 走 Registry 默认版本 -> 行为与现在一致
2. 未注册的 Pipeline 仍可正常使用 -> 直接实例化不受任何影响
3. `BasePipeline` 子类无需修改 -> 可选择性添加 `_pipeline_name` 属性

### 4.4 旧架构 Orchestrator 的兼容

```python
# fzq_ai/orchestrator/task_orchestrator.py（旧架构）
from fzq_ai.pipelines.registry import PipelineRegistry, create_pipeline

class TaskOrchestrator:
    def __init__(self):
        # 方式1：保持硬编码（完全兼容，不改一行）
        self.news = NewsPipeline()
        self.risk = RiskPipeline()
        self.sentiment = SentimentPipeline()

        # 方式2：通过 Registry（可选升级）
        # self.news = create_pipeline("news")
        # self.risk = create_pipeline("risk")
        # self.sentiment = create_pipeline("sentiment")
```

---

## 5. 插件化预留设计（entry_points）

### 5.1 设计思路

**现在不实现，但预留接口。** 未来外部包可以通过 `pip install` 安装后自动注册 Pipeline。

**实现时机：** v8.0+ 当需要支持第三方插件时再启用 `load_entry_points()`。

### 5.2 外部包的配置示例

**pyproject.toml（外部插件包）：**

```toml
[project]
name = "fzq-ai-plugin-news"
version = "1.0.0"

[project.entry-points."fzq_ai.pipelines"]
# 注册名 = 模块路径:类名
news_v4 = "fzq_ai_plugin_news.news_v4:NewsV4Pipeline"
news_v4_beta = "fzq_ai_plugin_news.news_v4:NewsV4BetaPipeline"
```

**setup.cfg（兼容写法）：**

```ini
[options.entry_points]
fzq_ai.pipelines =
    news_v4 = fzq_ai_plugin_news.news_v4:NewsV4Pipeline
```

### 5.3 加载代码（预留接口）

```python
# 在应用启动时调用一次（可选）
from fzq_ai.pipelines.registry import PipelineRegistry

# 自动扫描所有安装了 fzq_ai.pipelines entry_point 的包
loaded_count = PipelineRegistry.load_entry_points()
print(f"Loaded {loaded_count} external pipelines")

# 加载后与普通 Pipeline 无区别
PipelineRegistry.list_all()  # 包含外部插件
PipelineRegistry.get("news_v4")  # 外部插件的 Pipeline
```

### 5.4 加载逻辑（内部实现）

```python
@classmethod
def load_entry_points(cls, group: str = "fzq_ai.pipelines") -> int:
    """从 importlib.metadata / pkg_resources 加载外部插件。

    支持 Python 3.8+（自动降级）：
    - Python 3.10+: importlib.metadata.entry_points(group=...)
    - Python 3.8/3.9: importlib.metadata.entry_points().get(...)
    - Python <3.8: pkg_resources.iter_entry_points(...)
    """
    if sys.version_info >= (3, 10):
        from importlib.metadata import entry_points
        eps = entry_points(group=group)
    else:
        try:
            from importlib.metadata import entry_points
            all_eps = entry_points()
            eps = all_eps.get(group, [])
        except ImportError:
            import pkg_resources
            eps = pkg_resources.iter_entry_points(group)

    for ep in eps:
        pipeline_class = ep.load()  # 动态加载类
        cls.register_instance(ep.name, pipeline_class)
```

### 5.5 安全隔离（未来扩展）

```python
# 未来可扩展：加载时检查安全策略
@classmethod
def load_entry_points(cls, group="fzq_ai.pipelines", allowed_families=None):
    for ep in eps:
        pipeline_class = ep.load()
        entry = cls.register_instance(ep.name, pipeline_class)
        # 安全：只允许特定 family 的插件
        if allowed_families and entry.family not in allowed_families:
            cls.unregister(ep.name)
            logger.warning("Blocked external pipeline %s (family not allowed)", ep.name)
```

---

## 6. 迁移步骤建议（Step-by-step）

### Step 1: 新增 Registry 模块（已完成）

**新增文件：**

```
fzq_ai/pipelines/registry.py      # 注册中心 + 装饰器 + 工厂函数
fzq_ai/pipelines/protocol.py      # 统一协议（duck-typing）
```

**修改文件：**

```
fzq_ai/pipelines/base.py          # BasePipeline 增加可选注册属性
fzq_ai/pipelines/__init__.py      # 导出 Registry 接口
```

**验证：**

```bash
python -m pytest  # 确保 88/88 测试全部通过
```

### Step 2: 为现有 Pipeline 添加注册（可选、逐步）

**新架构 Pipeline（`pipelines/real/`）：**

```python
# fzq_ai/pipelines/real/news_pipeline.py
from fzq_ai.pipelines.registry import PipelineRegistry

@PipelineRegistry.register(
    "news_v2",
    description="Multi-source news analysis with translation and multi-dimension analysis",
    tags=["news", "intake", "translation", "analysis"],
    set_default=True,
)
class NewsPipeline:
    ...  # 现有代码不变
```

**对旧架构 Pipeline（`pipelines/`）：**

```python
# fzq_ai/pipelines/news_pipeline.py
from fzq_ai.pipelines.base import BasePipeline

class NewsPipeline(BasePipeline):
    _pipeline_name = "news_v1"  # 可选：自动注册
    _pipeline_description = "Legacy news pipeline"
    ...

# 模块末尾显式注册（可选）
NewsPipeline.register()
```

**test_adapter Pipeline：**

```python
# fzq_ai/pipelines/test_adapter/news_pipeline.py
from fzq_ai.pipelines.registry import PipelineRegistry

@PipelineRegistry.register("news_v2_test", tags=["test", "mock"])
class MockNewsPipeline:
    ...
```

### Step 3: 修改 Orchestrator（可选升级）

**渐进式升级：先保持硬编码，再逐步切换。**

```python
# fzq_ai/orchestrator/real/task_orchestrator.py

# 方式A：最小改动（保留硬编码，但增加 Registry 获取路径）
class TaskOrchestrator:
    def __init__(self, llm_router=None, use_registry=False):
        if use_registry:
            # 新方式：通过 Registry
            self.news_pipeline = create_pipeline("news", llm_router=llm_router)
            ...
        else:
            # 旧方式：硬编码（默认，零破坏）
            from fzq_ai.pipelines.real import NewsPipeline, ...
            self.news_pipeline = NewsPipeline()
            ...

# 方式B：完全升级（推荐在确认稳定后）
class TaskOrchestrator:
    def __init__(self, llm_router=None, pipeline_versions=None):
        self._llm_router = llm_router
        self._versions = pipeline_versions or {}
        self.news_pipeline = self._get_pipeline("news")
        self.narrative_pipeline = self._get_pipeline("narrative")
        ...
```

### Step 4: 回归测试建议

**测试清单：**

| 测试项 | 验证内容 | 期望结果 |
|--------|----------|----------|
| 现有测试 | `pytest` 全部通过 | 88/88 passed |
| 硬编码实例化 | `NewsPipeline()` 正常 | 不报错 |
| 旧 Orchestrator | `TaskOrchestrator()` 正常 | 行为不变 |
| Registry 注册 | `@PipelineRegistry.register("test_v1")` | 成功注册 |
| Registry 获取 | `PipelineRegistry.get("test_v1")` | 返回正确类 |
| 默认版本 | `PipelineRegistry.get("test")` | 返回默认版本 |
| @version 语法 | `PipelineRegistry.get("test@v1")` | 返回正确类 |
| 工厂函数 | `create_pipeline("test_v1")` | 返回实例 |
| 快照 | `PipelineRegistry.snapshot()` | 返回完整信息 |
| 注销 | `PipelineRegistry.unregister("test_v1")` | 成功移除 |
| 清理 | `PipelineRegistry.clear()` | 清空注册表 |

**新增测试文件建议：** `tests/test_pipeline_registry.py`

```python
import pytest
from fzq_ai.pipelines.registry import PipelineRegistry, PipelineEntry, create_pipeline

class TestPipelineRegistry:
    def setup_method(self):
        PipelineRegistry.clear()

    def test_register_and_get(self):
        @PipelineRegistry.register("test_v1")
        class TestPipeline:
            def run(self, x): return x

        cls = PipelineRegistry.get("test_v1")
        assert cls is TestPipeline

    def test_default_version(self):
        @PipelineRegistry.register("test_v1")
        class TestPipelineV1: ...

        @PipelineRegistry.register("test_v2", set_default=True)
        class TestPipelineV2: ...

        assert PipelineRegistry.get("test") is TestPipelineV2
        assert PipelineRegistry.get("test@v1") is TestPipelineV1

    def test_version_syntax(self):
        @PipelineRegistry.register("test_v1")
        class TestPipelineV1: ...

        @PipelineRegistry.register("test_v2")
        class TestPipelineV2: ...

        assert PipelineRegistry.get("test@latest") is TestPipelineV2

    def test_factory(self):
        @PipelineRegistry.register("test_v1")
        class TestPipeline:
            def __init__(self, value):
                self.value = value

        instance = create_pipeline("test_v1", value=42)
        assert instance.value == 42

    def test_not_found(self):
        with pytest.raises(KeyError):
            PipelineRegistry.get("nonexistent")
```

---

## 7. 风险与注意事项

### 7.1 兼容性风险

| 风险 | 等级 | 说明 | 缓解措施 |
|------|------|------|----------|
| **BasePipeline 修改** | 低 | 增加了可选属性（`_pipeline_name` 等），不影响现有子类 | 属性默认值均为 `None`，不强制覆盖 |
| `__init__.py` 导出 | 低 | 新增导出可能命名冲突 | 使用显式导入：`from fzq_ai.pipelines.registry import ...` |
| 注册表全局状态 | 中 | 单例模式，测试间可能相互影响 | 提供 `PipelineRegistry.clear()`，测试用 `setup_method` 清理 |
| 旧 API 端点 | 高 | `api_server.py` 调用不存在的 `list_pipelines()` | 新增 `PipelineRegistry.list_all()` 供 API 使用 |

### 7.2 命名冲突风险

```python
# 问题：两个不同模块注册了同名 Pipeline
# module_a.py
@PipelineRegistry.register("news_v2")
class NewsPipeline: ...

# module_b.py
@PipelineRegistry.register("news_v2")
class NewsPipeline: ...  # 覆盖 module_a 的注册！
```

**缓解措施：**

1. 注册时日志警告：`logger.warning("Overwriting existing pipeline: news_v2")`
2. 命名规范：团队约定注册名唯一性
3. 提供 `is_registered()` 检查：`if not PipelineRegistry.is_registered("news_v2"):`

### 7.3 版本膨胀风险

| 风险 | 说明 | 缓解措施 |
|------|------|----------|
| 版本过多 | 长期运行后注册表膨胀 | 提供 `snapshot()` 监控，Dashboard 展示版本数 |
| 实验版本残留 | `_exp` 版本长期不清理 | 约定实验版本生命周期，定期 review |
| 默认版本漂移 | 频繁切换默认版本导致行为不稳定 | `set_default()` 需要显式调用，记录变更日志 |

### 7.4 运行时切换风险

```python
# 风险：运行时切换 Pipeline 版本可能导致状态不一致
orch.set_pipeline_version("news", "v3_exp")
# 如果旧 Pipeline 已持有资源（如 DB 连接），可能泄漏
```

**缓解措施：**

1. 切换前调用旧实例的清理方法（如果实现了）
2. 推荐在初始化时确定版本，避免运行时切换
3. 文档明确说明：运行时切换主要用于测试，生产环境建议重启应用

### 7.5 entry_points 安全风险（未来）

| 风险 | 说明 | 缓解措施 |
|------|------|----------|
| 恶意插件 | 外部包通过 entry_points 注入恶意 Pipeline | 加载前校验来源、签名、或白名单 family |
| 依赖冲突 | 外部插件依赖不同版本的库 | 隔离运行环境（容器化） |
| 性能问题 | 外部插件加载慢 | `load_entry_points()` 在启动时一次性执行，异步加载 |

---

## 附录 A：完整 API 速查表

```python
from fzq_ai.pipelines.registry import (
    PipelineRegistry,      # 注册中心类
    PipelineEntry,         # 注册条目
    register_pipeline,     # 装饰器别名
    get_pipeline,          # 获取别名
    list_pipelines,        # 列表别名
    create_pipeline,       # 工厂函数
    get_pipeline_info,     # 信息查询
)
from fzq_ai.pipelines.protocol import PipelineProtocol, PipelineContext
from fzq_ai.pipelines.base import BasePipeline

# --- 注册 ---
@PipelineRegistry.register("news_v2", description="...", set_default=True)
class MyPipeline: ...

# 程序化注册
PipelineRegistry.register_instance("news_v2", MyPipeline)

# --- 获取 ---
PipelineRegistry.get("news_v2")        # 精确
PipelineRegistry.get("news")           # 默认
PipelineRegistry.get("news@v2")        # @version
PipelineRegistry.get("news@latest")    # 最新
PipelineRegistry.get("news@default")   # 默认

# --- 查询 ---
PipelineRegistry.list_all()            # 所有名称
PipelineRegistry.list_family("news")   # 某 family 所有版本
PipelineRegistry.list_families()       # 所有 family
PipelineRegistry.list_by_tag("realtime")  # 按标签
PipelineRegistry.get_family_info("news")  # 完整信息
PipelineRegistry.snapshot()            # 完整快照（Dashboard 用）

# --- 默认版本管理 ---
PipelineRegistry.set_default("news", "news_v2")
PipelineRegistry.get_default_name("news")

# --- 工厂 ---
create_pipeline("news_v2", llm_router=router)
get_pipeline_info("news_v2")

# --- 生命周期 ---
PipelineRegistry.unregister("news_v2")  # 注销
PipelineRegistry.clear()                # 清空（测试用）
PipelineRegistry.is_registered("news_v2")

# --- 插件预留 ---
PipelineRegistry.load_entry_points()    # 加载外部插件
```

## 附录 B：文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `fzq_ai/pipelines/registry.py` | 新增 | 注册中心核心代码 |
| `fzq_ai/pipelines/protocol.py` | 新增 | 统一协议 + PipelineContext |
| `fzq_ai/pipelines/base.py` | 修改 | BasePipeline 增加可选注册属性 |
| `fzq_ai/pipelines/__init__.py` | 修改 | 导出 Registry 接口 |
| `fzq_ai/pipelines/real/*.py` | 可选修改 | 添加 `@PipelineRegistry.register` 装饰器 |
| `fzq_ai/pipelines/test_adapter/*.py` | 可选修改 | 添加 test 标签注册 |
| `fzq_ai/orchestrator/real/task_orchestrator.py` | 可选修改 | 通过 Registry 获取 Pipeline |
| `tests/test_pipeline_registry.py` | 新增 | 注册中心单元测试 |
| `api_server.py` | 可选修改 | 修复 `list_pipelines()` 调用 |
