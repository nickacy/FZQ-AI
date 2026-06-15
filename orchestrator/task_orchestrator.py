SCENARIOS = {
    "daily_global_risk": {
        "name": "Daily Global Risk Scan",
        "description": "每日全球风险扫描：新闻 + 风险 + 叙事 + 情绪",
        "pipelines": ["news", "risk", "narrative", "sentiment"],
    },

    "taiwan_watch": {
        "name": "Taiwan Strait Watch",
        "description": "台海局势监控：区域新闻 + 风险扫描",
        "pipelines": ["news", "risk"],
    },

    "energy_market": {
        "name": "Energy Market Monitor",
        "description": "能源市场监控：油气、制裁、供应链风险",
        "pipelines": ["news", "risk"],
    },

    # —— v4.5 Autonomous Agent 新增 5 个 scenario ——

    "gaza_narrative": {
        "name": "Gaza Narrative Watch",
        "description": "监控 Gaza 地区叙事变化、媒体立场差异与风险动态",
        "pipelines": ["news", "narrative", "risk"],
    },

    "us_election": {
        "name": "US Election Monitor",
        "description": "监控美国大选相关新闻、叙事变化与风险信号",
        "pipelines": ["news", "narrative", "risk"],
    },

    "china_property": {
        "name": "China Property Monitor",
        "description": "监控中国房地产政策、市场信号与经济风险",
        "pipelines": ["news", "risk"],
    },

    "global_macro": {
        "name": "Global Macro Monitor",
        "description": "全球宏观经济、央行政策、市场风险扫描",
        "pipelines": ["news", "risk"],
    },

    "tech_regulation": {
        "name": "Tech Regulation Monitor",
        "description": "AI / 科技监管趋势、政策变化与行业风险",
        "pipelines": ["news", "risk"],
    },
}
