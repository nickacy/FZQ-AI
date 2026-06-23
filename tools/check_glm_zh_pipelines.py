# tools/check_glm_zh_pipelines.py
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import asyncio
import traceback


from fzq_ai.pipelines.zh_multisource_merge_pipeline import ZhMultiSourceMergePipeline
from fzq_ai.pipelines.zh_opinion_landscape_pipeline import ZhOpinionLandscapePipeline
from fzq_ai.pipelines.zh_policy_pipeline import ZhPolicyBriefPipeline
from fzq_ai.pipelines.zh_risk_scan_pipeline import ZhRiskScanPipeline


async def check_zh_multisource_merge():
    print("\n[CHECK] ZhMultiSourceMergePipeline + GLM-5.2")
    pipeline = ZhMultiSourceMergePipeline()
    result = await pipeline.run_async(
        event_topic="测试事件：中东局势",
        sources=[
            {
                "source": "test_news_1",
                "title": "测试新闻一",
                "content": "这是第一条测试新闻内容，用于验证多源合并。",
                "url": "https://example.com/1",
                "published_at": "2026-06-23T10:00:00",
            },
            {
                "source": "test_news_2",
                "title": "测试新闻二",
                "content": "这是第二条测试新闻内容，用于验证多源合并。",
                "url": "https://example.com/2",
                "published_at": "2026-06-23T11:00:00",
            },
        ],
    )
    print("  -> OK, type:", type(result))
    print("  -> status:", getattr(result, "status", "N/A"))


async def check_zh_opinion_landscape():
    print("\n[CHECK] ZhOpinionLandscapePipeline + GLM-5.2")
    pipeline = ZhOpinionLandscapePipeline()
    result = await pipeline.run_async(
        topic="测试话题：澳洲一国党",
        time_range="2026-06-01 ~ 2026-06-23",
        items=[
            {
                "platform": "Weibo",
                "author": "user_1",
                "content": "这是第一条测试舆论内容。",
                "url": "https://example.com/op1",
                "published_at": "2026-06-20T09:00:00",
            },
            {
                "platform": "Twitter",
                "author": "user_2",
                "content": "这是第二条测试舆论内容。",
                "url": "https://example.com/op2",
                "published_at": "2026-06-21T10:00:00",
            },
        ],
    )
    print("  -> OK, type:", type(result))
    print("  -> status:", getattr(result, "status", "N/A"))


async def check_zh_policy_brief():
    print("\n[CHECK] ZhPolicyBriefPipeline + GLM-5.2")
    pipeline = ZhPolicyBriefPipeline()
    result = await pipeline.run_async(
        doc_id="TEST-POLICY-001",
        source="test_source",
        publish_date="2026-06-23",
        title="关于促进人工智能产业发展的指导意见（测试版）",
        content="这是一个用于测试的政策文本内容，用于验证政策解读 Pipeline。",
        related_docs=[],
        user_focus=["对企业的支持政策", "数据安全与合规要求"],
    )
    print("  -> OK, type:", type(result))
    print("  -> status:", getattr(result, "status", "N/A"))


async def check_zh_risk_scan():
    print("\n[CHECK] ZhRiskScanPipeline + GLM-5.2")
    pipeline = ZhRiskScanPipeline()
    result = await pipeline.run_async(
        scan_window="2026-06-01 ~ 2026-06-23",
        scope=["geopolitics", "financial", "public_opinion"],
        items=[
            {
                "source": "news_site",
                "title": "测试风险新闻一",
                "content": "这是第一条测试风险新闻内容。",
                "url": "https://example.com/risk1",
                "published_at": "2026-06-20T08:00:00",
            },
            {
                "source": "social_media",
                "title": "测试风险舆情二",
                "content": "这是第二条测试风险舆情内容。",
                "url": "https://example.com/risk2",
                "published_at": "2026-06-21T12:00:00",
            },
        ],
        entity_watchlist=["澳洲一国党", "中东局势"],
    )
    print("  -> OK, type:", type(result))
    print("  -> status:", getattr(result, "status", "N/A"))


async def main():
    checks = [
        check_zh_multisource_merge,
        check_zh_opinion_landscape,
        check_zh_policy_brief,
        check_zh_risk_scan,
    ]

    for fn in checks:
        try:
            await fn()
        except Exception:
            print("  -> ERROR:")
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
