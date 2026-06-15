"""v2.7 IntelStore tests (spec-compliant)."""
from datetime import datetime, timedelta
import pytest
from fzq_ai.domain.models import Article, IntelBundle, IntelMeta
from fzq_ai.store.intel_store import IntelStore, IntelRecord

class TestIntelStore:
    @pytest.fixture
    def store(self):
        import tempfile, os
        yield s
        try:
        except OSError:
            pass

    def test_init_creates_table(self, store):
        rows = store._get_conn().execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        names = [r[0] for r in rows]
        assert "intel_runs" in names

    def test_save_and_load_bundle(self, store):
        bundle = IntelBundle(
            meta=IntelMeta(topics=["test"], regions=["western"], depth="normal"),
            articles=[
        assert len(records) == 1
        assert records[0].topic == "test-topic"
        assert len(records[0].bundle.articles) == 1

    def test_load_trend(self, store):
        for i in range(3):
            bundle = IntelBundle(
                meta=IntelMeta(topics=["trend"], regions=[], depth="normal"),
                articles=[
        assert len(records) == 3

    def test_load_trend_since(self, store):
        now = datetime.utcnow()
        for i in range(5):
            bundle = IntelBundle(
                meta=IntelMeta(topics=["since-test"], regions=[], depth="normal"),
                articles=[Article(title_original=f"S{i}", url=f"http://s.com/{i}")],
                events=[]
        assert len(recent) >= 2

    def test_intel_record_dataclass(self):
        bundle = IntelBundle(meta=IntelMeta(), articles=[], events=[])
        r = IntelRecord(
            run_id="r1", topic="t", created_at=datetime.utcnow(),
            provider_snapshot={}, bundle=bundle
        assert r.run_id == "r1"
        assert r.topic == "t"

    def test_empty_load(self, store):
        assert store.load_latest("nonexistent") == []
        assert store.load_trend("nonexistent") == []
