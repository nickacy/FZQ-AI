import json
from fzq_ai.pipelines.sentiment_pipeline import SentimentPipeline
from fzq_ai.domain.models import Article


class TestSentimentPipeline:
    def test_sentiment_pipeline_with_articles(self):
        pipeline = SentimentPipeline()
        articles = [
            Article(title_original="Growth surges", content_original="positive growth improvement"),
            Article(title_original="Crisis deepens", content_original="conflict war attack"),
        ]
        result = pipeline.run(articles=articles)

        # 旧模式：返回 str
        assert isinstance(result, str)
        data = json.loads(result)

        assert "distribution" in data
        assert data["total_articles"] == 2

    def test_sentiment_pipeline_empty_articles(self):
        pipeline = SentimentPipeline()
        result = pipeline.run(articles=[])

        # 空输入也返回 str
        assert isinstance(result, str)
        data = json.loads(result)
        assert data["total_articles"] == 0
