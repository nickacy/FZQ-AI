from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ScheduledTask:
    """结构化的定时任务对象"""
    name: str
    cron: str
    scenario: str


class SchedulerAgent:
    """
    v3.0 Scheduler Agent
    - 注册任务
    - 保存任务
    - 返回任务列表
    """

    def __init__(self):
        self._jobs: Dict[str, ScheduledTask] = {}

    def register_job(self, name: str, cron: str, scenario: str):
        """注册一个定时任务"""
        self._jobs[name] = ScheduledTask(name=name, cron=cron, scenario=scenario)

    def list_jobs(self) -> List[ScheduledTask]:
        """返回所有任务（修复 DS GUI 破坏的列表推导式）"""
        return [
            ScheduledTask(name=t.name, cron=t.cron, scenario=t.scenario)
            for t in self._jobs.values()
        ]

    def run_pending(self):
        """占位：未来可扩展 cron 解析"""
        return {"status": "ok", "jobs": list(self._jobs.keys())}
