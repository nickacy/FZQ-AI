"""
FZQ-AI Pipeline Registry — v7.0 Pipeline 中心 & 版本共存

设计目标：
1. 统一 Pipeline 注册与发现机制
2. 支持版本共存（news_v1 / news_v2 / news_v3_exp）
3. 零破坏现有代码（可选层）
4. 预留插件化扩展（entry_points）
5. 轻量级：仅标准库 + importlib

使用示例：
    from fzq_ai.pipelines.registry import PipelineRegistry, PipelineEntry

    @PipelineRegistry.register("news_v2")
    class NewsPipeline:
        async def run(self, input): ...

    # 获取 Pipeline 类
    cls = PipelineRegistry.get("news_v2")
    # 获取默认版本
    cls = PipelineRegistry.get("news")
    # 获取元数据
    entry = PipelineRegistry.get_entry("news_v2")
"""
from __future__ import annotations

import re
import sys
import time
import inspect
import logging
from typing import Any, Dict, List, Optional, Type, Callable, Union, Set
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. Pipeline 协议（统一接口）
# ---------------------------------------------------------------------------

class PipelineProtocol:
    """Pipeline 统一协议（duck-typing，不强制继承）。

    约定方法：
    - run(self, input) -> output    同步或异步执行
    - 可选：run_async(self, input) -> output   异步入口

    任何实现了 run() 或 run_async() 的类都可以注册为 Pipeline。
    """
    pass


# ---------------------------------------------------------------------------
# 2. PipelineEntry — 注册条目（含元数据）
# ---------------------------------------------------------------------------

@dataclass
class PipelineEntry:
    """Pipeline 注册条目。包含类、元数据、版本信息。"""

    # 注册名（如 "news_v2", "risk_v1"）
    name: str
    # Pipeline 类
    pipeline_class: Type[Any]
    # 所属家族（如 "news", "risk"），从 name 自动推断
    family: str = field(default="")
    # 版本号（如 "v2", "v1"），从 name 自动推断
    version: str = field(default="")
    # 是否实验版本
    is_experimental: bool = False
    # 描述
    description: str = ""
    # 输入 schema 类型提示
    input_schema: Optional[str] = None
    # 输出 schema 类型提示
    output_schema: Optional[str] = None
    # 标签（用于分类和搜索）
    tags: List[str] = field(default_factory=list)
    # 依赖的其他 Pipeline 家族
    dependencies: List[str] = field(default_factory=list)
    # 注册时间戳
    registered_at: float = field(default_factory=time.time)
    # 额外元数据
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.family or not self.version:
            self.family, self.version = self._parse_name(self.name)
        if self.is_experimental is False and "_exp" in self.name.lower():
            self.is_experimental = True

    @staticmethod
    def _parse_name(name: str) -> tuple:
        """从注册名解析 family 和 version。

        解析规则：
        - "news_v2"     → family="news", version="v2"
        - "news_v3_exp" → family="news", version="v3_exp"
        - "risk_v1"     → family="risk", version="v1"
        - "daily_report" → family="daily_report", version=""
        - "daily_report_v2" → family="daily_report", version="v2"
        """
        # 匹配 "_v数字" 或 "_v数字_exp" 后缀
        match = re.match(r'^(.*?)(_v\d+(?:_exp)?)$', name, re.IGNORECASE)
        if match:
            return match.group(1), match.group(2).lower()
        return name, ""

    def create(self, *args, **kwargs) -> Any:
        """工厂方法：创建 Pipeline 实例。"""
        return self.pipeline_class(*args, **kwargs)

    def __repr__(self) -> str:
        return f"PipelineEntry(name={self.name!r}, family={self.family!r}, version={self.version!r})"


# ---------------------------------------------------------------------------
# 3. PipelineRegistry — 注册中心
# ---------------------------------------------------------------------------

class PipelineRegistry:
    """Pipeline 统一注册中心。

    支持：
    - 按名称注册 / 获取 Pipeline
    - 版本共存（family@version 语法）
    - 家族默认版本
    - 自动发现（entry_points 预留）
    - 元数据查询（标签、描述、依赖）

    单例模式：全局唯一注册表。
    """

    # 全局注册表：name → PipelineEntry
    _registry: Dict[str, PipelineEntry] = {}
    # 家族默认版本：family → name
    _defaults: Dict[str, str] = {}
    # 是否已加载 entry_points
    _entry_points_loaded: bool = False

    # -----------------------------------------------------------------------
    # 注册
    # -----------------------------------------------------------------------
    @classmethod
    def register(
        cls,
        name: str,
        *,
        description: str = "",
        tags: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        input_schema: Optional[str] = None,
        output_schema: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        set_default: bool = False,
    ) -> Callable[[Type[Any]], Type[Any]]:
        """注册装饰器。用于标记 Pipeline 类。

        Args:
            name: 注册名，如 "news_v2", "risk_v1"
            description: Pipeline 描述
            tags: 标签列表
            dependencies: 依赖的 Pipeline family
            input_schema: 输入 schema 类型提示
            output_schema: 输出 schema 类型提示
            metadata: 额外元数据
            set_default: 是否设为该 family 的默认版本

        Returns:
            装饰器函数

        示例：
            @PipelineRegistry.register("news_v2", description="News analysis v2", set_default=True)
            class NewsPipeline:
                async def run(self, input): ...
        """
        def decorator(pipeline_class: Type[Any]) -> Type[Any]:
            if not cls._is_valid_pipeline(pipeline_class):
                logger.warning(
                    "Pipeline %s does not have a run() or run_async() method. "
                    "Registering anyway, but may fail at runtime.",
                    pipeline_class.__name__,
                )

            entry = PipelineEntry(
                name=name,
                pipeline_class=pipeline_class,
                description=description,
                tags=tags or [],
                dependencies=dependencies or [],
                input_schema=input_schema,
                output_schema=output_schema,
                metadata=metadata or {},
            )

            cls._registry[name] = entry
            logger.debug("Registered pipeline: %s (%s)", name, pipeline_class.__name__)

            # 设置家族默认版本
            family = entry.family
            if set_default or family not in cls._defaults:
                # 如果已有默认版本且当前不是显式设置默认，则保留旧的
                if set_default or family not in cls._defaults:
                    cls._defaults[family] = name
                    logger.debug("Set default for family %s → %s", family, name)

            # 将注册信息附加到类上（方便自省）
            pipeline_class._pipeline_entry = entry  # type: ignore

            return pipeline_class

        return decorator

    # -----------------------------------------------------------------------
    # 获取
    # -----------------------------------------------------------------------
    @classmethod
    def get(cls, name: str) -> Type[Any]:
        """获取 Pipeline 类。

        支持语法：
        - "news_v2"        → 精确匹配
        - "news"           → 返回 family 默认版本
        - "news@v2"        → 指定版本（@version 语法）
        - "news@latest"    → 返回该 family 最新版本
        - "news@default"   → 返回该 family 默认版本

        Args:
            name: Pipeline 名称（支持 @version 语法）

        Returns:
            Pipeline 类

        Raises:
            KeyError: 如果找不到对应的 Pipeline
        """
        # 解析 @version 语法
        family, version = cls._parse_version_spec(name)

        if version:
            # 有版本号
            if version == "latest":
                return cls.get_latest(family)
            if version == "default":
                return cls.get_default(family)
            # "news@v2" → "news_v2"
            full_name = f"{family}_{version}"
            if full_name in cls._registry:
                return cls._registry[full_name].pipeline_class
            raise KeyError(
                f"Pipeline '{full_name}' not found. "
                f"Available: {cls.list_family(family)}"
            )

        # 无版本号：先精确匹配，再 fallback 到 family 默认
        if name in cls._registry:
            return cls._registry[name].pipeline_class

        # name 作为 family 查找默认版本
        if name in cls._defaults:
            default_name = cls._defaults[name]
            return cls._registry[default_name].pipeline_class

        raise KeyError(
            f"Pipeline '{name}' not found. "
            f"Registered: {list(cls._registry.keys())}"
        )

    @classmethod
    def get_entry(cls, name: str) -> PipelineEntry:
        """获取 PipelineEntry（含完整元数据）。"""
        family, version = cls._parse_version_spec(name)

        if version:
            if version == "latest":
                return cls._get_latest_entry(family)
            if version == "default":
                return cls._registry[cls._defaults[family]]
            full_name = f"{family}_{version}"
            if full_name in cls._registry:
                return cls._registry[full_name]
            raise KeyError(f"Pipeline '{full_name}' not found")

        if name in cls._registry:
            return cls._registry[name]
        if name in cls._defaults:
            return cls._registry[cls._defaults[name]]

        raise KeyError(f"Pipeline '{name}' not found")

    @classmethod
    def get_default(cls, family: str) -> Type[Any]:
        """获取 family 的默认版本。"""
        if family not in cls._defaults:
            raise KeyError(f"No default pipeline for family '{family}'")
        return cls._registry[cls._defaults[family]].pipeline_class

    @classmethod
    def get_latest(cls, family: str) -> Type[Any]:
        """获取 family 的最新版本（按版本号排序）。"""
        entry = cls._get_latest_entry(family)
        return entry.pipeline_class

    @classmethod
    def _get_latest_entry(cls, family: str) -> PipelineEntry:
        """获取 family 的最新版本条目。"""
        candidates = cls.list_family(family)
        if not candidates:
            raise KeyError(f"No pipelines registered for family '{family}'")
        # 按版本号排序（v10 > v9 > ... > v1）
        # 实验版本排在稳定版本之后
        def _version_key(entry_name: str) -> tuple:
            entry = cls._registry[entry_name]
            v = entry.version
            # 提取数字部分
            m = re.search(r'v(\d+)', v)
            num = int(m.group(1)) if m else 0
            is_exp = 1 if "_exp" in v else 0
            return (num, is_exp)

        latest_name = max(candidates, key=_version_key)
        return cls._registry[latest_name]

    # -----------------------------------------------------------------------
    # 列表查询
    # -----------------------------------------------------------------------
    @classmethod
    def list_all(cls) -> List[str]:
        """列出所有已注册的 Pipeline 名称。"""
        return list(cls._registry.keys())

    @classmethod
    def list_family(cls, family: str) -> List[str]:
        """列出某 family 下的所有版本。"""
        return [
            name for name, entry in cls._registry.items()
            if entry.family == family
        ]

    @classmethod
    def list_families(cls) -> List[str]:
        """列出所有 family。"""
        return sorted({entry.family for entry in cls._registry.values()})

    @classmethod
    def list_by_tag(cls, tag: str) -> List[str]:
        """按标签列出 Pipeline。"""
        return [
            name for name, entry in cls._registry.items()
            if tag in entry.tags
        ]

    @classmethod
    def get_family_info(cls, family: str) -> Dict[str, Any]:
        """获取 family 的完整信息。"""
        versions = cls.list_family(family)
        default = cls._defaults.get(family)
        return {
            "family": family,
            "versions": versions,
            "default": default,
            "count": len(versions),
            "entries": {v: cls._registry[v].__dict__ for v in versions},
        }

    # -----------------------------------------------------------------------
    # 默认版本管理
    # -----------------------------------------------------------------------
    @classmethod
    def set_default(cls, family: str, name: str) -> None:
        """显式设置 family 的默认版本。"""
        if name not in cls._registry:
            raise KeyError(f"Pipeline '{name}' not registered")
        entry = cls._registry[name]
        if entry.family != family:
            raise ValueError(
                f"Pipeline '{name}' belongs to family '{entry.family}', "
                f"not '{family}'"
            )
        cls._defaults[family] = name
        logger.info("Set default for family %s → %s", family, name)

    @classmethod
    def get_default_name(cls, family: str) -> Optional[str]:
        """获取 family 默认版本的注册名。"""
        return cls._defaults.get(family)

    # -----------------------------------------------------------------------
    # 动态注册 / 注销
    # -----------------------------------------------------------------------
    @classmethod
    def unregister(cls, name: str) -> Optional[PipelineEntry]:
        """注销 Pipeline（支持动态卸载）。"""
        entry = cls._registry.pop(name, None)
        if entry:
            family = entry.family
            # 如果注销的是默认版本，需要重新选择默认
            if cls._defaults.get(family) == name:
                remaining = cls.list_family(family)
                if remaining:
                    cls._defaults[family] = remaining[0]
                else:
                    cls._defaults.pop(family, None)
        return entry

    @classmethod
    def register_instance(
        cls,
        name: str,
        pipeline_class: Type[Any],
        **metadata: Any,
    ) -> PipelineEntry:
        """程序化注册（非装饰器方式）。"""
        entry = PipelineEntry(name=name, pipeline_class=pipeline_class, **metadata)
        cls._registry[name] = entry
        family = entry.family
        if family not in cls._defaults:
            cls._defaults[family] = name
        return entry

    # -----------------------------------------------------------------------
    # 状态 & 调试
    # -----------------------------------------------------------------------
    @classmethod
    def clear(cls) -> None:
        """清空注册表（测试用）。"""
        cls._registry.clear()
        cls._defaults.clear()
        cls._entry_points_loaded = False

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """检查是否已注册。"""
        try:
            cls.get(name)
            return True
        except KeyError:
            return False

    @classmethod
    def snapshot(cls) -> Dict[str, Any]:
        """获取注册表快照（用于调试 / Dashboard）。"""
        return {
            "registered_pipelines": {
                name: {
                    "family": entry.family,
                    "version": entry.version,
                    "class": entry.pipeline_class.__name__,
                    "module": entry.pipeline_class.__module__,
                    "description": entry.description,
                    "tags": entry.tags,
                    "is_experimental": entry.is_experimental,
                }
                for name, entry in cls._registry.items()
            },
            "defaults": dict(cls._defaults),
            "families": cls.list_families(),
            "total_count": len(cls._registry),
        }

    # -----------------------------------------------------------------------
    # 插件化预留：entry_points 加载
    # -----------------------------------------------------------------------
    @classmethod
    def load_entry_points(cls, group: str = "fzq_ai.pipelines") -> int:
        """从 pkg_resources / importlib.metadata 加载外部插件。

        预留接口：未来可通过 pip install 外部包，
        在 setup.py/setup.cfg/pyproject.toml 中声明：

            [project.entry-points."fzq_ai.pipelines"]
            news_v4 = external_pkg.news:NewsV4Pipeline

        然后调用 PipelineRegistry.load_entry_points() 自动加载。

        Args:
            group: entry_points 组名，默认 "fzq_ai.pipelines"

        Returns:
            加载的 Pipeline 数量
        """
        if cls._entry_points_loaded:
            logger.debug("Entry points already loaded, skipping")
            return 0

        loaded = 0
        try:
            # Python 3.10+ 使用 importlib.metadata
            if sys.version_info >= (3, 10):
                from importlib.metadata import entry_points
                eps = entry_points(group=group)
            else:
                # Python 3.8/3.9 fallback
                try:
                    from importlib.metadata import entry_points
                    all_eps = entry_points()
                    eps = all_eps.get(group, [])
                except ImportError:
                    # 更旧版本使用 pkg_resources
                    import pkg_resources
                    eps = pkg_resources.iter_entry_points(group)

            for ep in eps:
                try:
                    pipeline_class = ep.load()
                    name = ep.name
                    cls.register_instance(name, pipeline_class)
                    loaded += 1
                    logger.info(
                        "Loaded pipeline from entry_point: %s = %s:%s",
                        name, ep.module, pipeline_class.__name__
                    )
                except Exception as exc:
                    logger.warning(
                        "Failed to load entry_point %s: %s", ep.name, exc
                    )

        except Exception as exc:
            logger.warning("Failed to load entry_points: %s", exc)

        cls._entry_points_loaded = True
        return loaded

    # -----------------------------------------------------------------------
    # 内部工具
    # -----------------------------------------------------------------------
    @staticmethod
    def _parse_version_spec(name: str) -> tuple:
        """解析 @version 语法。

        "news@v2"     → ("news", "v2")
        "news@latest" → ("news", "latest")
        "news"        → ("news", "")
        """
        if "@" in name:
            family, version = name.split("@", 1)
            return family.strip(), version.strip()
        return name, ""

    @staticmethod
    def _is_valid_pipeline(pipeline_class: Type[Any]) -> bool:
        """检查类是否实现了 Pipeline 接口。"""
        has_run = hasattr(pipeline_class, "run") and callable(getattr(pipeline_class, "run"))
        has_run_async = hasattr(pipeline_class, "run_async") and callable(getattr(pipeline_class, "run_async"))
        return has_run or has_run_async


# ---------------------------------------------------------------------------
# 4. 便捷别名
# ---------------------------------------------------------------------------

register_pipeline = PipelineRegistry.register
get_pipeline = PipelineRegistry.get
list_pipelines = PipelineRegistry.list_all


# ---------------------------------------------------------------------------
# 5. 版本共存工具函数
# ---------------------------------------------------------------------------

def create_pipeline(
    name: str,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """工厂函数：按名称创建 Pipeline 实例。

    示例：
        pipeline = create_pipeline("news_v2", llm_router=router)
        pipeline = create_pipeline("news@latest", llm_router=router)
        pipeline = create_pipeline("news", llm_router=router)  # 默认版本
    """
    entry = PipelineRegistry.get_entry(name)
    return entry.create(*args, **kwargs)


def get_pipeline_info(name: str) -> Dict[str, Any]:
    """获取 Pipeline 的完整信息。"""
    entry = PipelineRegistry.get_entry(name)
    return {
        "name": entry.name,
        "family": entry.family,
        "version": entry.version,
        "description": entry.description,
        "class": entry.pipeline_class.__name__,
        "module": entry.pipeline_class.__module__,
        "tags": entry.tags,
        "dependencies": entry.dependencies,
        "is_experimental": entry.is_experimental,
        "registered_at": entry.registered_at,
    }


# ---------------------------------------------------------------------------
# 6. 向后兼容：保留旧的 register_pipeline 接口
# ---------------------------------------------------------------------------

# 如果未来有其他模块定义了 register_pipeline，这里不会冲突
# 因为 Python 的模块导入机制允许同名函数存在不同模块中
# 推荐使用 from fzq_ai.pipelines.registry import PipelineRegistry, register_pipeline
