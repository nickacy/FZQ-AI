"""
FZQ-AI Schema 验证器 v9.2 — Minimax 结构检查与字段补全专家

职责：
1. 检查 JSON 结构是否完整（Schema 对齐）
2. 补全缺失字段（默认值填充）
3. 修正非法枚举值（映射到最近合法值）
4. 删除 Schema 未定义字段（严格过滤）
5. 清理空字符串字段（替换为 null 或默认值）

质量标准：
- 100% Schema 对齐
- 无非法枚举
- 无空字段
- 无冗余字段

使用示例：
    from fzq_ai.schemas.validator import SchemaValidator

    validator = SchemaValidator()
    result = validator.validate(json_data, "zh_policy_brief")
    # result.ok: bool
    # result.data: dict (修正后的 JSON)
    # result.errors: list[str] (发现的问题)
    # result.warnings: list[str] (自动修复的问题)
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional, Type, Union, get_type_hints, get_origin, get_args
from dataclasses import dataclass, field
from enum import Enum

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. 验证结果数据结构
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    """Schema 验证结果。"""
    ok: bool = False                    # 是否通过验证（无错误）
    data: Dict[str, Any] = field(default_factory=dict)   # 修正后的数据
    errors: List[str] = field(default_factory=list)      # 错误列表（无法自动修复）
    warnings: List[str] = field(default_factory=list)    # 警告列表（已自动修复）
    schema_name: str = ""               # 使用的 Schema 名称

    def __repr__(self) -> str:
        status = "✅ PASS" if self.ok else "❌ FAIL"
        return (
            f"ValidationResult({status}, schema={self.schema_name}, "
            f"errors={len(self.errors)}, warnings={len(self.warnings)})"
        )


# ---------------------------------------------------------------------------
# 2. Schema 注册表（映射 pipeline 名称到 Pydantic 模型）
# ---------------------------------------------------------------------------

class SchemaRegistry:
    """Schema 注册表：pipeline 名称 -> Pydantic Model。"""

    _schemas: Dict[str, Type[BaseModel]] = {}

    @classmethod
    def register(cls, name: str, model: Type[BaseModel]) -> None:
        cls._schemas[name] = model

    @classmethod
    def get(cls, name: str) -> Optional[Type[BaseModel]]:
        return cls._schemas.get(name)

    @classmethod
    def list_schemas(cls) -> List[str]:
        return list(cls._schemas.keys())

    @classmethod
    def get_schema_info(cls, name: str) -> Dict[str, Any]:
        """获取 Schema 的字段信息摘要。"""
        model = cls.get(name)
        if not model:
            return {}

        info = {
            "name": name,
            "model": model.__name__,
            "fields": {},
            "required": [],
            "optional": [],
            "enums": {},
        }

        for field_name, field_info in model.model_fields.items():
            annotation = field_info.annotation
            info["fields"][field_name] = {
                "annotation": str(annotation),
                "description": field_info.description,
                "default": field_info.default,
            }
            if field_info.is_required():
                info["required"].append(field_name)
            else:
                info["optional"].append(field_name)

            # 提取枚举值
            enum_values = cls._extract_enum_values(annotation)
            if enum_values:
                info["enums"][field_name] = enum_values

        return info

    @staticmethod
    def _extract_enum_values(annotation: Any) -> Optional[List[str]]:
        """从类型注解中提取 Literal 枚举值。"""
        origin = get_origin(annotation)
        if origin is None:
            return None

        # 处理 Optional[X] = Union[X, None]
        if origin is Union:
            args = get_args(annotation)
            for arg in args:
                if arg is not type(None):
                    return SchemaRegistry._extract_literal_values(arg)
            return None

        return SchemaRegistry._extract_literal_values(annotation)

    @staticmethod
    def _extract_literal_values(annotation: Any) -> Optional[List[str]]:
        """提取 Literal 的具体值。"""
        origin = get_origin(annotation)
        if origin is not None and hasattr(origin, '__name__'):
            if origin.__name__ == 'Literal':
                return list(get_args(annotation))
        # 处理嵌套泛型
        args = get_args(annotation)
        if args and hasattr(args[0], '__origin__'):
            if args[0].__origin__.__name__ == 'Literal':
                return list(args[0].__args__)
        return None


# ---------------------------------------------------------------------------
# 3. 自动注册所有中文任务 Schema
# ---------------------------------------------------------------------------

def _auto_register_schemas():
    """自动注册所有已导入的中文任务 Schema。"""
    try:
        from fzq_ai.schemas.zh_tasks.zh_policy_brief import ZhPolicyBriefOutput
        SchemaRegistry.register("zh_policy_brief", ZhPolicyBriefOutput)
    except ImportError as e:
        logger.warning("Failed to register zh_policy_brief: %s", e)

    try:
        from fzq_ai.schemas.zh_tasks.zh_risk_scan import ZhRiskScanOutput
        SchemaRegistry.register("zh_risk_scan", ZhRiskScanOutput)
    except ImportError as e:
        logger.warning("Failed to register zh_risk_scan: %s", e)

    try:
        from fzq_ai.schemas.zh_tasks.zh_opinion_landscape import ZhOpinionLandscapeOutput
        SchemaRegistry.register("zh_opinion_landscape", ZhOpinionLandscapeOutput)
    except ImportError as e:
        logger.warning("Failed to register zh_opinion_landscape: %s", e)

    try:
        from fzq_ai.schemas.zh_tasks.zh_multisource_merge import ZhMultiSourceMergeOutput
        SchemaRegistry.register("zh_multisource_merge", ZhMultiSourceMergeOutput)
    except ImportError as e:
        logger.warning("Failed to register zh_multisource_merge: %s", e)


_auto_register_schemas()


# ---------------------------------------------------------------------------
# 4. Minimax 验证器核心
# ---------------------------------------------------------------------------

class SchemaValidator:
    """Schema 验证器：检查、补全、修正、清理 JSON 数据。

    符合 Minimax 质量标准：
    - 100% Schema 对齐
    - 无非法枚举
    - 无空字段
    - 无冗余字段
    """

    def __init__(self, strict: bool = True):
        """
        Args:
            strict: 严格模式。True = 删除未定义字段；False = 保留未定义字段但警告
        """
        self.strict = strict

    # -----------------------------------------------------------------------
    # 主入口
    # -----------------------------------------------------------------------
    def validate(self, data: Dict[str, Any], schema_name: str) -> ValidationResult:
        """验证并修正 JSON 数据。

        Args:
            data: 待验证的 JSON 数据
            schema_name: Schema 名称（如 "zh_policy_brief"）

        Returns:
            ValidationResult: 包含修正后的数据、错误和警告
        """
        result = ValidationResult(schema_name=schema_name)
        model_class = SchemaRegistry.get(schema_name)

        if not model_class:
            result.errors.append(f"Schema '{schema_name}' not registered")
            return result

        # 步骤 1: 删除未定义字段（严格模式）
        cleaned = self._remove_undefined_fields(data, model_class)
        if cleaned != data:
            removed = set(data.keys()) - set(cleaned.keys())
            if removed:
                result.warnings.append(f"Removed undefined fields: {removed}")

        # 步骤 2: 清理空字符串
        cleaned = self._clean_empty_strings(cleaned)

        # 步骤 3: 修正非法枚举值
        cleaned, enum_warnings = self._fix_enum_values(cleaned, model_class)
        result.warnings.extend(enum_warnings)

        # 步骤 4: 补全缺失字段
        cleaned, missing_warnings = self._fill_missing_fields(cleaned, model_class)
        result.warnings.extend(missing_warnings)

        # 步骤 5: Pydantic 验证
        try:
            validated = model_class(**cleaned)
            result.data = validated.model_dump()
            result.ok = True
        except ValidationError as e:
            result.errors.extend(self._parse_pydantic_errors(e))
            result.data = cleaned  # 返回已清理的数据，即使验证失败
        except Exception as e:
            result.errors.append(f"Unexpected validation error: {str(e)}")
            result.data = cleaned

        return result

    # -----------------------------------------------------------------------
    # 步骤 1: 删除未定义字段
    # -----------------------------------------------------------------------
    def _remove_undefined_fields(
        self, data: Dict[str, Any], model_class: Type[BaseModel]
    ) -> Dict[str, Any]:
        """删除 Schema 未定义的顶层字段。"""
        if not self.strict:
            return data

        allowed_fields = set(model_class.model_fields.keys())
        return {k: v for k, v in data.items() if k in allowed_fields}

    # -----------------------------------------------------------------------
    # 步骤 2: 清理空字符串
    # -----------------------------------------------------------------------
    def _clean_empty_strings(self, obj: Any) -> Any:
        """递归清理空字符串，替换为 None。"""
        if isinstance(obj, str) and obj.strip() == "":
            return None
        elif isinstance(obj, dict):
            return {k: self._clean_empty_strings(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._clean_empty_strings(item) for item in obj]
        return obj

    # -----------------------------------------------------------------------
    # 步骤 3: 修正非法枚举值
    # -----------------------------------------------------------------------
    def _fix_enum_values(
        self, data: Dict[str, Any], model_class: Type[BaseModel]
    ) -> tuple:
        """修正非法枚举值，返回修正后的数据和警告列表。"""
        warnings = []
        corrected = data.copy()

        for field_name, field_info in model_class.model_fields.items():
            if field_name not in corrected:
                continue

            enum_values = SchemaRegistry._extract_enum_values(field_info.annotation)
            if not enum_values:
                continue

            value = corrected[field_name]
            if value is None:
                continue

            # 处理列表中的枚举值
            if isinstance(value, list):
                new_list = []
                for item in value:
                    if isinstance(item, dict):
                        # 递归处理嵌套模型
                        item_model = self._get_nested_model(field_info.annotation)
                        if item_model:
                            fixed_item, item_warnings = self._fix_enum_values(item, item_model)
                            new_list.append(fixed_item)
                            warnings.extend(item_warnings)
                        else:
                            new_list.append(item)
                    elif isinstance(item, str) and item not in enum_values:
                        fixed = self._find_nearest_enum(item, enum_values)
                        warnings.append(
                            f"Field '{field_name}[].{item}' invalid enum '{item}', "
                            f"corrected to '{fixed}'"
                        )
                        new_list.append(fixed)
                    else:
                        new_list.append(item)
                corrected[field_name] = new_list
            elif isinstance(value, str) and value not in enum_values:
                fixed = self._find_nearest_enum(value, enum_values)
                warnings.append(
                    f"Field '{field_name}' invalid enum '{value}', corrected to '{fixed}'"
                )
                corrected[field_name] = fixed

        return corrected, warnings

    def _find_nearest_enum(self, value: str, enum_values: List[str]) -> str:
        """找到最近的合法枚举值。"""
        # 精确匹配（忽略大小写和空格）
        for ev in enum_values:
            if ev.lower().replace(" ", "") == value.lower().replace(" ", ""):
                return ev

        # 包含匹配
        for ev in enum_values:
            if value.lower() in ev.lower() or ev.lower() in value.lower():
                return ev

        # 默认返回第一个
        return enum_values[0]

    def _get_nested_model(self, annotation: Any) -> Optional[Type[BaseModel]]:
        """从列表类型注解中提取嵌套的 Pydantic 模型。"""
        origin = get_origin(annotation)
        if origin is list or (hasattr(origin, '__name__') and origin.__name__ == 'List'):
            args = get_args(annotation)
            if args:
                item_type = args[0]
                if isinstance(item_type, type) and issubclass(item_type, BaseModel):
                    return item_type
        return None

    # -----------------------------------------------------------------------
    # 步骤 4: 补全缺失字段
    # -----------------------------------------------------------------------
    def _fill_missing_fields(
        self, data: Dict[str, Any], model_class: Type[BaseModel]
    ) -> tuple:
        """补全缺失字段，返回补全后的数据和警告列表。"""
        warnings = []
        filled = data.copy()

        for field_name, field_info in model_class.model_fields.items():
            if field_name in filled and filled[field_name] is not None:
                continue

            # 获取默认值
            default = field_info.default
            if default is not None and default != ...:
                filled[field_name] = default
                warnings.append(f"Field '{field_name}' missing, filled with default: {default}")
            elif field_info.is_required():
                # 必填字段缺失，根据类型推断填充
                inferred = self._infer_default_value(field_info.annotation)
                filled[field_name] = inferred
                warnings.append(f"Field '{field_name}' required but missing, filled with: {inferred}")
            else:
                # 可选字段，填充 None
                filled[field_name] = None

        return filled, warnings

    def _infer_default_value(self, annotation: Any) -> Any:
        """根据类型注解推断默认值。"""
        origin = get_origin(annotation)

        if origin is list or (hasattr(origin, '__name__') and origin.__name__ == 'List'):
            return []
        elif origin is dict or (hasattr(origin, '__name__') and origin.__name__ == 'Dict'):
            return {}
        elif origin is str or annotation is str:
            return ""
        elif origin is int or annotation is int:
            return 0
        elif origin is float or annotation is float:
            return 0.0
        elif origin is bool or annotation is bool:
            return False

        # 处理 Optional[X]
        if origin is Union:
            args = get_args(annotation)
            for arg in args:
                if arg is not type(None):
                    return self._infer_default_value(arg)
            return None

        return None

    # -----------------------------------------------------------------------
    # 步骤 5: 解析 Pydantic 错误
    # -----------------------------------------------------------------------
    def _parse_pydantic_errors(self, e: ValidationError) -> List[str]:
        """将 Pydantic ValidationError 解析为可读的错误列表。"""
        errors = []
        for err in e.errors():
            loc = " -> ".join(str(x) for x in err["loc"])
            msg = err["msg"]
            errors.append(f"Field '{loc}': {msg}")
        return errors

    # -----------------------------------------------------------------------
    # 便捷方法：批量验证
    # -----------------------------------------------------------------------
    def validate_batch(
        self, items: List[Dict[str, Any]], schema_name: str
    ) -> List[ValidationResult]:
        """批量验证多个 JSON 对象。"""
        return [self.validate(item, schema_name) for item in items]

    # -----------------------------------------------------------------------
    # 便捷方法：生成验证报告
    # -----------------------------------------------------------------------
    def generate_report(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """生成批量验证报告。"""
        total = len(results)
        passed = sum(1 for r in results if r.ok)
        failed = total - passed
        total_errors = sum(len(r.errors) for r in results)
        total_warnings = sum(len(r.warnings) for r in results)

        return {
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": f"{passed / total * 100:.1f}%" if total > 0 else "0%",
                "total_errors": total_errors,
                "total_warnings": total_warnings,
            },
            "details": [
                {
                    "schema": r.schema_name,
                    "ok": r.ok,
                    "errors": r.errors,
                    "warnings": r.warnings,
                }
                for r in results
            ],
        }


# ---------------------------------------------------------------------------
# 5. 便捷函数
# ---------------------------------------------------------------------------

def validate_json(data: Dict[str, Any], schema_name: str, strict: bool = True) -> ValidationResult:
    """便捷函数：验证 JSON 数据。"""
    validator = SchemaValidator(strict=strict)
    return validator.validate(data, schema_name)


def quick_check(data: Dict[str, Any], schema_name: str) -> bool:
    """便捷函数：快速检查是否通过验证。"""
    result = validate_json(data, schema_name, strict=True)
    return result.ok


# ---------------------------------------------------------------------------
# 6. 对齐检查工具（Prompt ↔ Schema 一致性检查）
# ---------------------------------------------------------------------------

class SchemaAlignmentChecker:
    """Prompt ↔ Schema 对齐检查工具。

    检查 Prompt 中提到的字段是否与 Schema 定义一致。
    """

    def check(self, schema_name: str, prompt_text: str) -> Dict[str, Any]:
        """检查 Prompt 文本与 Schema 的对齐情况。

        Args:
            schema_name: Schema 名称
            prompt_text: Prompt 文本内容

        Returns:
            对齐检查报告
        """
        schema_info = SchemaRegistry.get_schema_info(schema_name)
        if not schema_info:
            return {"error": f"Schema '{schema_name}' not found"}

        fields = schema_info["fields"]
        enums = schema_info["enums"]

        report = {
            "schema_name": schema_name,
            "schema_fields": list(fields.keys()),
            "prompt_mentioned_fields": [],
            "missing_in_prompt": [],
            "extra_in_prompt": [],
            "enum_check": {},
            "overall_alignment": 0.0,
        }

        # 检查 Prompt 中是否提到了 Schema 字段
        for field_name in fields:
            # 支持多种匹配模式：字段名、带引号的字段名、JSON 路径中的字段名
            patterns = [
                f'"{field_name}"',
                f"'{field_name}'",
                f"{field_name}:",
                f'{field_name}":',
            ]
            mentioned = any(p in prompt_text for p in patterns)
            if mentioned:
                report["prompt_mentioned_fields"].append(field_name)
            else:
                report["missing_in_prompt"].append(field_name)

        # 检查枚举值一致性
        for field_name, enum_values in enums.items():
            prompt_enums = [v for v in enum_values if v in prompt_text]
            missing_enums = [v for v in enum_values if v not in prompt_text]
            report["enum_check"][field_name] = {
                "schema_values": enum_values,
                "prompt_mentioned": prompt_enums,
                "missing_in_prompt": missing_enums,
                "alignment_rate": len(prompt_enums) / len(enum_values) if enum_values else 1.0,
            }

        # 计算总体对齐率
        total_fields = len(fields)
        mentioned_fields = len(report["prompt_mentioned_fields"])
        report["overall_alignment"] = mentioned_fields / total_fields if total_fields > 0 else 0.0

        return report

    def check_all(
        self, prompts: Dict[str, str]
    ) -> Dict[str, Any]:
        """批量检查所有 Pipeline 的 Prompt ↔ Schema 对齐情况。

        Args:
            prompts: {schema_name: prompt_text} 字典

        Returns:
            批量对齐检查报告
        """
        reports = {}
        for schema_name, prompt_text in prompts.items():
            reports[schema_name] = self.check(schema_name, prompt_text)

        # 计算总体统计
        total_schemas = len(reports)
        avg_alignment = sum(r["overall_alignment"] for r in reports.values()) / total_schemas if total_schemas > 0 else 0

        return {
            "summary": {
                "total_schemas": total_schemas,
                "average_alignment": f"{avg_alignment * 100:.1f}%",
                "lowest_alignment": min((r["overall_alignment"], name) for name, r in reports.items()) if reports else (0, ""),
            },
            "reports": reports,
        }


# ---------------------------------------------------------------------------
# 7. 导出便捷函数
# ---------------------------------------------------------------------------

__all__ = [
    "SchemaValidator",
    "ValidationResult",
    "SchemaRegistry",
    "SchemaAlignmentChecker",
    "validate_json",
    "quick_check",
]
