from fzq_ai.agent.scheduler_agent import SchedulerAgent, ScheduledTask
from fzq_ai.agent.report_agent import ReportAgent


class TestSchedulerAgent:
    def test_run_pending(self):
        s = SchedulerAgent()
        s.register_job("test", "* * * * *", "test_scenario")
        result = s.run_pending()
        assert "test" in result


class TestReportAgent:
    def test_empty_report(self):
        r = ReportAgent()
        assert "无数据" in r.generate_markdown_report("topic")

    def test_save_report(self):
        r = ReportAgent()
        assert isinstance(r.generate_markdown_report("topic"), str)
