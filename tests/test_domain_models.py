"""R3: Domain model Pydantic serialization tests.

Verifies Article, IntelMeta, IntelBundle serialize/deserialize correctly.
"""
from __future__ import annotations
import pytest
from datetime import datetime, timezone
from fzq_ai.domain.models import Article, IntelMeta, IntelBundle


class TestArticle:
    def test_article_defaults(self):
        a = Article()
        assert a.title_original == ""
        assert a.credibility == 0.0
        assert isinstance(a.fetched_at, datetime)

    def test_article_serialization(self):
        a = Article(title_original="Test Title", region="CN", source_name="Reuters")
        d = a.model_dump()
        assert d["title_original"] == "Test Title"
        assert d["region"] == "CN"
        assert d["source_name"] == "Reuters"
        # Pydantic serialization preserves types
        assert isinstance(d["credibility"], float)
        assert isinstance(d["propaganda_tags"], list)

    def test_article_deserialization(self):
        a = Article(title_original="Title", region="US", credibility=0.8)
        d = a.model_dump()
        b = Article(**d)
        assert b.title_original == a.title_original
        assert b.credibility == a.credibility


class TestIntelMeta:
    def test_meta_defaults(self):
        m = IntelMeta()
        assert m.topics == []
        assert m.depth == "normal"

    def test_meta_roundtrip(self):
        m = IntelMeta(topics=["AI", "defense"], regions=["CN", "US"], depth="deep")
        d = m.model_dump()
        m2 = IntelMeta(**d)
        assert m2.topics == m.topics
        assert m2.regions == m.regions
        assert m2.depth == m.depth


class TestIntelBundle:
    def test_bundle_structure(self):
        b = IntelBundle()
        assert isinstance(b.meta, IntelMeta)
        assert b.articles == []
        assert b.summary == ""

    def test_bundle_roundtrip(self):
        a1 = Article(title_original="News 1", source_name="Src", region="CN")
        meta = IntelMeta(topics=["tech"], depth="normal")
        b = IntelBundle(meta=meta, articles=[a1], summary="Test summary")
        d = b.model_dump()
        b2 = IntelBundle(**d)
        assert b2.summary == "Test summary"
        assert len(b2.articles) == 1
        assert b2.articles[0].title_original == "News 1"
