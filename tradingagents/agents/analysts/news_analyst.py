from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_news_analyst(llm, toolkit):
    def news_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        # 智能选择新闻工具：根据股票代码类型选择合适的新闻源
        def is_china_stock(ticker_code):
            """判断是否为中国股票代码"""
            return ticker_code.isdigit() and len(ticker_code) == 6

        if toolkit.config["online_tools"]:
            # 在线模式：根据股票类型选择新闻源
            if is_china_stock(ticker):
                tools = [
                    toolkit.get_china_stock_news_enhanced,  # 中国股票专用新闻
                    toolkit.get_chinese_social_sentiment,   # 中国社交媒体
                    toolkit.get_google_news,                # Google新闻（备用）
                ]
            else:
                tools = [
                    toolkit.get_realtime_stock_news,  # 实时新闻
                    toolkit.get_google_news,          # Google新闻
                    toolkit.get_finnhub_news,         # FinnHub新闻
                ]
        else:
            # 离线模式：使用缓存数据和搜索
            tools = [
                toolkit.get_realtime_stock_news,  # 尝试实时新闻
                toolkit.get_finnhub_news,
                toolkit.get_reddit_news,
                toolkit.get_google_news,
            ]

        system_message = (
            """您是一位专业的财经新闻分析师，负责分析最新的市场新闻和事件对股票价格的潜在影响。

🚫 **严格禁止**：
- 绝对不允许编造、模拟或虚构任何新闻内容
- 不允许生成"模拟案例"或"演示分析"
- 不允许使用"假设"或"模拟"等字样
- 必须基于工具获取的真实数据进行分析

✅ **必须遵循**：
- 只能使用工具获取的真实新闻数据
- 如果无法获取真实数据，必须明确说明数据缺失
- 所有分析必须基于实际获取的新闻内容
- 明确标注数据来源和获取时间

您的主要职责包括：
1. 获取和分析最新的实时新闻（优先15-30分钟内的新闻）
2. 评估新闻事件的紧急程度和市场影响
3. 识别可能影响股价的关键信息
4. 分析新闻的时效性和可靠性
5. 提供基于新闻的交易建议和价格影响评估

重点关注的新闻类型：
- 财报发布和业绩指导
- 重大合作和并购消息
- 政策变化和监管动态
- 突发事件和危机管理
- 行业趋势和技术突破
- 管理层变动和战略调整

分析要点：
- 新闻的时效性（发布时间距离现在多久）
- 新闻的可信度（来源权威性）
- 市场影响程度（对股价的潜在影响）
- 投资者情绪变化（正面/负面/中性）
- 与历史类似事件的对比

📊 价格影响分析要求：
- 评估新闻对股价的短期影响（1-3天）
- 分析可能的价格波动幅度（百分比）
- 提供基于新闻的价格调整建议
- 识别关键价格支撑位和阻力位
- 评估新闻对长期投资价值的影响

⚠️ **数据处理规则**：
- 如果新闻数据存在滞后（超过2小时），请在分析中明确说明时效性限制
- 如果无法获取新闻数据，明确说明"真实新闻数据暂时不可用"
- 优先分析最新的、高相关性的新闻事件
- 提供新闻对股价影响的量化评估和具体价格预期
- 必须包含基于新闻的价格影响分析和调整建议

请撰写详细的中文分析报告，并在报告末尾附上Markdown表格总结关键发现。"""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "您是一位有用的AI助手，与其他助手协作。"
                    " 使用提供的工具来推进回答问题。"
                    " 如果您无法完全回答，没关系；具有不同工具的其他助手"
                    " 将从您停下的地方继续帮助。执行您能做的以取得进展。"
                    " 如果您或任何其他助手有最终交易提案：**买入/持有/卖出**或可交付成果，"
                    " 请在您的回应前加上最终交易提案：**买入/持有/卖出**，以便团队知道停止。"
                    " 您可以访问以下工具：{tool_names}。\n{system_message}"
                    "供您参考，当前日期是{current_date}。我们正在查看公司{ticker}。请用中文撰写所有分析内容。",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "news_report": report,
        }

    return news_analyst_node
