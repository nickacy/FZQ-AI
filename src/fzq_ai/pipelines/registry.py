"""
FZQ-AI Pipeline Registry — v7.0（修复版）
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
    """Pipeline 统一协议（duck-typing，不强制继承）。"""
    pass


# ---------------------------------------------------------------------------
# 2. PipelineEntry — 注册条目（含元数据）
# ---------------------------------------------------------------------------

@dataclass
class PipelineEntry:
    name: str
    pipeline_class: Type[Any]
    family: str = field(default="")
    version: str = field(default="")
    is_experimental: bool = False
    description: str = ""
    input_schema: Optional[str] = None
    output_schema: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    registered_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.family or not self.version:
            self.family, self.version = self._parse_name(self.name)
        if self.is_experimental is False and "_exp" in self.name.lower():
            self.is_experimental = True

    @staticmethod
    def _parse_name(name: str) -> tuple:
        if "@" in name:
            family, version = name.rsplit("@", 1)
            return family, version.lower()
        match = re.match(r'^(.*?)(_v\d+(?:_exp)?)$', name, re.IGNORECASE)
        if match:
            return match.group(1), match.group(2).lower()
        return name, ""

    def create(self, *args, **kwargs) -> Any:
        return self.pipeline_class(*args, **kwargs)

    def __repr__(self) -> str:
        return f"PipelineEntry(name={self.name!r}, family={self.family!r}, version={self.version!r})"


# ---------------------------------------------------------------------------
# 3. PipelineRegistry — 注册中心
# ---------------------------------------------------------------------------

class PipelineRegistry:
    _registry: Dict[str, PipelineEntry] = {}
    _defaults: Dict[str, str] = {}
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

        def decorator(pipeline_class: Type[Any]) -> Type[Any]:
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

            PipelineRegistry._registry[name] = entry

            family = entry.family
            if set_default or family not in PipelineRegistry._defaults:
                PipelineRegistry._defaults[family] = name

            pipeline_class._pipeline_entry = entry  # type: ignore
            return pipeline_class

        return decorator

    # -----------------------------------------------------------------------
    # 获取（修复：返回实例，而不是类）
    # -----------------------------------------------------------------------
    @classmethod
    def get(cls, name: str) -> Any:
        family, version = cls._parse_version_spec(name)

        # version 语法
        if version:
            if version == "latest":
                entry = cls._get_latest_entry(family)
                return entry.create()
            if version == "default":
                default_name = cls._defaults[family]
                return cls._registry[default_name].create()

            full_name = f"{family}@{version}"
            if full_name not in cls._registry:
                full_name = f"{family}_{version}"

            if full_name in cls._registry:
                return cls._registry[full_name].create()

            raise KeyError(f"Pipeline '{full_name}' not found. Available: {cls.list_family(family)}")

        # 无版本号：精确匹配
        if name in cls._registry:
            return cls._registry[name].create()

        # family 默认版本
        if name in cls._defaults:
            default_name = cls._defaults[name]
            return cls._registry[default_name].create()

        raise KeyError(f"Pipeline '{name}' not found. Registered: {list(cls._registry.keys())}")

    @classmethod
    def get_entry(cls, name: str) -> PipelineEntry:
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
    def get_default(cls, family: str) -> Any:
        if family not in cls._defaults:
            raise KeyError(f"No default pipeline for family '{family}'")
        return cls._registry[cls._defaults[family]].create()

    @classmethod
    def get_latest(cls, family: str) -> Any:
        entry = cls._get_latest_entry(family)
        return entry.create()

    @classmethod
    def _get_latest_entry(cls, family: str) -> PipelineEntry:
        candidates = cls.list_family(family)
        if not candidates:
            raise KeyError(f"No pipelines registered for family '{family}'")

        def _version_key(entry_name: str) -> tuple:
            entry = cls._registry[entry_name]
            v = entry.version
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
        return list(cls._registry.keys())

    @classmethod
    def list_family(cls, family: str) -> List[str]:
        return [name for name, entry in cls._registry.items() if entry.family == family]

    @classmethod
    def list_families(cls) -> List[str]:
        return sorted({entry.family for entry in cls._registry.values()})

    @classmethod
    def list_by_tag(cls, tag: str) -> List[str]:
        return [name for name, entry in cls._registry.items() if tag in entry.tags]

    @classmethod
    def get_family_info(cls, family: str) -> Dict[str, Any]:
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
        if name not in cls._registry:
            raise KeyError(f"Pipeline '{name}' not registered")
        entry = cls._registry[name]
        if entry.family != family:
            raise ValueError(f"Pipeline '{name}' belongs to family '{entry.family}', not '{family}'")
        cls._defaults[family] = name

    @classmethod
    def get_default_name(cls, family: str) -> Optional[str]:
        return cls._defaults.get(family)

    # -----------------------------------------------------------------------
    # 动态注册 / 注销
    # -----------------------------------------------------------------------
    @classmethod
    def unregister(cls, name: str) -> Optional[PipelineEntry]:
        entry = cls._registry.pop(name, None)
        if entry:
            family = entry.family
            if cls._defaults.get(family) == name:
                remaining = cls.list_family(family)
                if remaining:
                    cls._defaults[family] = remaining[0]
                else:
                    cls._defaults.pop(family, None)
        return entry

    @classmethod
    def register_instance(cls, name: str, pipeline_class: Type[Any], **metadata: Any) -> PipelineEntry:
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
        cls._registry.clear()
        cls._defaults.clear()
        cls._entry_points_loaded = False

    @classmethod
    def is_registered(cls, name: str) -> bool:
        try:
            cls.get(name)
            return True
        except KeyError:
            return False

    @classmethod
    def snapshot(cls) -> Dict[str, Any]:
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
    # entry_points（保留）
    # -----------------------------------------------------------------------
    @classmethod
    def load_entry_points(cls, group: str = "fzq_ai.pipelines") -> int:
        if cls._entry_points_loaded:
            return 0

        loaded = 0
        try:
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
                try:
                    pipeline_class = ep.load()
                    name = ep.name
                    cls.register_instance(name, pipeline_class)
                    loaded += 1
                except Exception:
                    pass

        except Exception:
            pass

        cls._entry_points_loaded = True
        return loaded

    # -----------------------------------------------------------------------
    # 内部工具
    # -----------------------------------------------------------------------
    @staticmethod
    def _parse_version_spec(name: str) -> tuple:
        if "@" in name:
            family, version = name.split("@", 1)
            return family.strip(), version.strip()
        return name, ""

    @staticmethod
    def _is_valid_pipeline(pipeline_class: Type[Any]) -> bool:
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
# 5. 工厂函数
# ---------------------------------------------------------------------------

def create_pipeline(name: str, *args: Any, **kwargs: Any) -> Any:
    entry = PipelineRegistry.get_entry(name)
    return entry.create(*args, **kwargs)


def get_pipeline_info(name: str) -> Dict[str, Any]:
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
