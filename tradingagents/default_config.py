import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_dir": os.path.join(os.path.expanduser("~"), "Documents", "TradingAgents", "data"),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings - 优先使用最高性能模型
    "llm_provider": "siliconflow",
    "deep_think_llm": "Qwen/Qwen2.5-72B-Instruct",      # 最高性能：72B参数
    "quick_think_llm": "deepseek-ai/DeepSeek-R1",       # 推理专用：最强推理能力
    "backend_url": "https://api.siliconflow.cn/v1",

    # 🔄 默认回退模型配置
    "default_model": os.getenv("DEFAULT_MODEL", "deepseek-ai/DeepSeek-V3"),  # 专用模型失败时的回退选择

    # 专业化分析师模型配置 - 每个分析师使用最适合的高性能模型
    "market_analyst_llm": os.getenv("MARKET_ANALYST_LLM", "meta-llama/Llama-3.1-70B-Instruct"),      # 技术分析：长上下文，数据处理能力强
    "fundamentals_analyst_llm": os.getenv("FUNDAMENTALS_ANALYST_LLM", "Qwen/Qwen2.5-72B-Instruct"), # 基本面分析：最高性能，复杂计算
    "news_analyst_llm": os.getenv("NEWS_ANALYST_LLM", "deepseek-ai/DeepSeek-R1"),                    # 新闻分析：推理能力强，逻辑分析
    "social_analyst_llm": os.getenv("SOCIAL_ANALYST_LLM", "Qwen/Qwen2.5-32B-Instruct"),             # 社交媒体：中文优化，情绪理解

    # Debate and discussion settings
    "max_debate_rounds": 2,  # 增加辩论轮次，充分利用高性能模型
    "max_risk_discuss_rounds": 2,
    "max_recur_limit": 100,
    # Tool settings
    "online_tools": True,

    # Note: Database and cache configuration is now managed by .env file and config.database_manager
    # No database/cache settings in default config to avoid configuration conflicts
}
