"""
FZQ-AI Intelligence System
Life Assistant Agent (日常生活助手)
Author: Nick + Copilot
"""

from typing import Dict, Any, List
import json


class LifeAssistantAgent:
    """
    统一的生活助手 Agent：
    - DeepSeek 做意图识别 + 工具规划
    - 工具层执行（metro / route / walking / cost_of_living / attractions / weather）
    - DeepSeek 做最终回答整合
    """

    def __init__(self, llm_router, tools: Dict[str, Any]):
        """
        tools = {
            "metro": metro_tool,
            "route": route_tool,
            "walking": walking_tool,
            "attractions": attractions_tool,
            "cost": cost_tool,
            "weather": weather_tool,
            ...
        }
        """
        self.llm = llm_router
        self.tools = tools

    # ---------------------------------------------------------
    # 主入口：用户问一句话 → 返回结构化结果
    # ---------------------------------------------------------
    def answer(
        self, user_query: str, user_profile: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """
        1. DeepSeek 做意图识别 + 工具规划
        2. 调用对应工具
        3. DeepSeek 做最终回答整合
        """
        plan = self.plan_tools(user_query, user_profile)
        tool_results = self.execute_tools(plan)
        final_answer = self.compose_answer(user_query, plan, tool_results)

        return {
            "query": user_query,
            "plan": plan,
            "tool_results": tool_results,
            "final_answer": final_answer,
        }

    # ---------------------------------------------------------
    # Step 1：DeepSeek 生成工具规划
    # ---------------------------------------------------------
    def plan_tools(
        self, user_query: str, user_profile: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        prompt = self.build_planning_prompt(user_query, user_profile)
        response = self.llm.run("life_planning", prompt)
        return self.parse_json_safe(response, default={"tools": [], "params": {}})

    def build_planning_prompt(
        self, user_query: str, user_profile: Dict[str, Any] | None
    ) -> str:
        profile_text = (
            json.dumps(user_profile, ensure_ascii=False) if user_profile else "{}"
        )

        return f"""
你是一个生活助手 Agent，负责根据用户需求选择合适的工具。

用户资料：
{profile_text}

用户问题：
{user_query}

可用工具列表（tool_name: 功能说明）：
- metro: 地铁路线查询
- route: 综合路线规划（公交/地铁/步行）
- walking: 步行时间估算
- attractions: 景点推荐 / Daytrip
- cost: 生活成本估算
- weather: 天气查询

请输出 JSON：
{{
  "tools": ["metro", "route"],
  "params": {{
      "origin": "...",
      "destination": "...",
      "time": "..."
  }}
}}
"""

    # ---------------------------------------------------------
    # Step 2：执行工具
    # ---------------------------------------------------------
    def execute_tools(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        results = {}
        tools = plan.get("tools", [])
        params = plan.get("params", {})

        for tool_name in tools:
            tool = self.tools.get(tool_name)
            if not tool:
                results[tool_name] = {"error": "tool not found"}
                continue

            try:
                results[tool_name] = tool.run(params)
            except Exception as e:
                results[tool_name] = {"error": str(e)}

        return results

    # ---------------------------------------------------------
    # Step 3：DeepSeek 整合最终回答
    # ---------------------------------------------------------
    def compose_answer(
        self, user_query: str, plan: Dict[str, Any], tool_results: Dict[str, Any]
    ) -> str:
        prompt = self.build_answer_prompt(user_query, plan, tool_results)
        return self.llm.run("life_answer", prompt)

    def build_answer_prompt(
        self, user_query: str, plan: Dict[str, Any], tool_results: Dict[str, Any]
    ) -> str:
        return f"""
你是一个生活助手 Agent，请根据工具执行结果给用户一个自然语言回答。

用户问题：
{user_query}

工具规划：
{json.dumps(plan, ensure_ascii=False, indent=2)}

工具执行结果：
{json.dumps(tool_results, ensure_ascii=False, indent=2)}

请输出自然语言回答，包含：
- 直接回答用户问题
- 简短解释你是如何得出答案的
- 如果有路线/地铁/景点/天气等信息，请整合成可执行建议
"""

    # ---------------------------------------------------------
    # 工具函数：安全解析 JSON
    # ---------------------------------------------------------
    def parse_json_safe(self, text: str, default: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except:
            try:
                start = text.index("{")
                end = text.rindex("}") + 1
                return json.loads(text[start:end])
            except:
                return default
