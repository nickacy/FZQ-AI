"""
fzq_ai.domain.enums

领域枚举定义：
- 风险等级（RiskLevel）
- 情绪（Sentiment）
- 工具类型（ToolType，可扩展）
- 叙事类型（NarrativeType，可扩展）
"""

from __future__ import annotations
from enum import Enum

class RiskLevel(str, Enum):
    """风险等级枚举"""

class Sentiment(str, Enum):
    """情绪枚举"""

class ToolType(str, Enum):
    """工具类型（预留扩展位）"""

class NarrativeType(str, Enum):
    """叙事类型（预留扩展位）"""

