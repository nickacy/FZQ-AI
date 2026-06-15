"""v3.0 Agent tests."""
from fzq_ai.agent.scheduler_agent import SchedulerAgent, ScheduledTask
from fzq_ai.agent.watchlist_agent import WatchlistAgent
from fzq_ai.agent.report_agent import ReportAgent
from fzq_ai.agent.alert_agent import AlertAgent


class TestSchedulerAgent:
    def test_register_job(self):
        s = SchedulerAgent()
        s.register_job("daily", "0 8 * * *", "daily_global_risk")
        assert len(s.list_jobs()) == 1

    def test_run_pending(self):
        s = SchedulerAgent()
        s.register_job("test", "* * * * *", "test_scenario")
        assert "test" in s.run_pending()

    def test_scheduled_task(self):
        t = ScheduledTask("n", "0 8 * * *", "s")
        assert t.name == "n"


class TestWatchlistAgent:
    def test_topics(self):
        w = WatchlistAgent(watchlist_path="_test_wl.json")
        assert len(w.list_topics()) >= 2

    def test_add_remove(self):
        w = WatchlistAgent(watchlist_path="_test_wl.json")
        w.add_topic("cyber")
        assert "cyber" in w.list_topics()
        w.remove_topic("cyber")

    def test_run_once(self):
        w = WatchlistAgent(watchlist_path="_test_wl.json")
        assert isinstance(w.run_once(), dict)


class TestReportAgent:
    def test_empty_report(self):
        r = ReportAgent()
        report = r.generate_markdown_report("nonexistent-topic")
        assert "FZQ-AI" in report
        assert "No data" in report

    def test_save_report(self):
        import os
        r = ReportAgent()
        p = r.save_report("# test", filename="_tr.md")
        assert os.path.exists(p)
        os.remove(p)


class TestAlertAgent:
    def test_scan_empty(self):
        assert isinstance(AlertAgent().scan_for_alerts(), list)

    def test_threshold(self):
        assert AlertAgent(risk_threshold=4)._threshold == 4
