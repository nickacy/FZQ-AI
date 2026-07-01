# src/fzq_ai/ui/ui_schema.py
# V24 — UI Schema（声明式渲染器）
# 完全新增，不破坏现有功能。

from __future__ import annotations
from typing import Any, Dict, List


class UISchema:
    """
    声明式 UI Schema：
    - APP / 前端根据 schema 自动渲染界面
    - 后端只描述结构，不负责渲染
    """

    @staticmethod
    def text_block(title: str, content: str) -> Dict[str, Any]:
        return {
            "type": "text",
            "title": title,
            "content": content,
        }

    @staticmethod
    def card(title: str, items: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "card",
            "title": title,
            "items": items,
        }

    @staticmethod
    def list_block(title: str, items: List[str]) -> Dict[str, Any]:
        return {
            "type": "list",
            "title": title,
            "items": items,
        }

    @staticmethod
    def timeline_block(title: str, timeline: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "type": "timeline",
            "title": title,
            "items": timeline,
        }

    @staticmethod
    def state_machine(title: str, states: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "state_machine",
            "title": title,
            "states": states,
        }

    @staticmethod
    def layout(blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "type": "layout",
            "blocks": blocks,
        }
