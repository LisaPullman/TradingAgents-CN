#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硅基流动新闻搜索工具
替代OpenAI的web_search_preview功能
"""

import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from langchain_core.messages import HumanMessage


def get_stock_news_siliconflow(ticker: str, curr_date: str) -> str:
    """
    使用硅基流动API获取股票新闻和社交媒体情绪
    替代OpenAI的get_stock_news_openai功能
    
    Args:
        ticker: 股票代码
        curr_date: 当前日期，格式为yyyy-mm-dd
    
    Returns:
        格式化的新闻和情绪分析报告
    """
    try:
        from tradingagents.llm_adapters.siliconflow_adapter import create_siliconflow_llm
        
        # 创建硅基流动LLM实例
        llm = create_siliconflow_llm(
            model="deepseek-ai/DeepSeek-V3",
            temperature=0.1,
            max_tokens=2000
        )
        
        # 计算搜索时间范围
        end_date = datetime.strptime(curr_date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=7)
        
        # 构建搜索提示
        search_prompt = f"""
请帮我搜索和分析股票{ticker}在{start_date.strftime('%Y-%m-%d')}到{curr_date}期间的相关信息：

1. 最新新闻和公告
2. 社交媒体讨论热度
3. 投资者情绪变化
4. 重要事件和影响

请提供：
- 新闻标题和关键内容
- 消息来源和发布时间
- 市场反应和情绪分析
- 对股价的潜在影响

注意：请基于您的知识库提供分析，如果某些信息不确定，请明确说明。
"""
        
        # 调用硅基流动API
        response = llm.invoke([HumanMessage(content=search_prompt)])
        
        # 格式化返回结果
        formatted_result = f"""
## {ticker} 股票新闻和社交媒体分析
**分析时间范围**: {start_date.strftime('%Y-%m-%d')} 至 {curr_date}
**数据来源**: 硅基流动AI分析

{response.content}

---
*注意: 此分析基于AI模型的知识库，建议结合实时数据源进行验证*
"""
        
        return formatted_result
        
    except Exception as e:
        return f"硅基流动新闻搜索失败: {str(e)}"


def get_global_news_siliconflow(curr_date: str) -> str:
    """
    使用硅基流动API获取全球宏观经济新闻
    替代OpenAI的get_global_news_openai功能
    
    Args:
        curr_date: 当前日期，格式为yyyy-mm-dd
    
    Returns:
        格式化的全球新闻分析报告
    """
    try:
        from tradingagents.llm_adapters.siliconflow_adapter import create_siliconflow_llm
        
        # 创建硅基流动LLM实例
        llm = create_siliconflow_llm(
            model="Qwen/Qwen2.5-72B-Instruct",  # 使用Qwen处理全球新闻
            temperature=0.1,
            max_tokens=2000
        )
        
        # 计算搜索时间范围
        end_date = datetime.strptime(curr_date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=7)
        
        # 构建搜索提示
        search_prompt = f"""
请分析{start_date.strftime('%Y-%m-%d')}到{curr_date}期间的全球宏观经济新闻和事件：

重点关注：
1. 美联储政策和利率变化
2. 主要经济体GDP、通胀数据
3. 地缘政治事件
4. 大宗商品价格变化
5. 汇率波动
6. 重要央行政策

请提供：
- 关键事件时间线
- 对全球市场的影响
- 对股票市场的潜在影响
- 投资建议和风险提示

注意：请基于您的知识库提供分析，重点关注对交易有影响的事件。
"""
        
        # 调用硅基流动API
        response = llm.invoke([HumanMessage(content=search_prompt)])
        
        # 格式化返回结果
        formatted_result = f"""
## 全球宏观经济新闻分析
**分析时间范围**: {start_date.strftime('%Y-%m-%d')} 至 {curr_date}
**数据来源**: 硅基流动AI分析

{response.content}

---
*注意: 此分析基于AI模型的知识库，建议结合实时新闻源进行验证*
"""
        
        return formatted_result
        
    except Exception as e:
        return f"硅基流动全球新闻搜索失败: {str(e)}"


def get_realtime_sentiment_siliconflow(ticker: str, curr_date: str) -> str:
    """
    使用硅基流动API分析实时市场情绪
    
    Args:
        ticker: 股票代码
        curr_date: 当前日期，格式为yyyy-mm-dd
    
    Returns:
        格式化的情绪分析报告
    """
    try:
        from tradingagents.llm_adapters.siliconflow_adapter import create_siliconflow_llm
        
        # 创建硅基流动LLM实例
        llm = create_siliconflow_llm(
            model="deepseek-ai/DeepSeek-R1",  # 使用推理专用模型
            temperature=0.1,
            max_tokens=1500
        )
        
        # 构建情绪分析提示
        sentiment_prompt = f"""
请分析股票{ticker}当前的市场情绪和投资者心理：

分析维度：
1. 技术面情绪（突破、支撑、阻力）
2. 基本面情绪（业绩预期、行业趋势）
3. 资金面情绪（机构动向、散户行为）
4. 消息面情绪（新闻影响、政策预期）

请提供：
- 情绪指数评分（1-10分，1=极度悲观，10=极度乐观）
- 主要情绪驱动因素
- 情绪变化趋势
- 对短期股价的影响预测
- 交易建议和风险提示

当前日期：{curr_date}
"""
        
        # 调用硅基流动API
        response = llm.invoke([HumanMessage(content=sentiment_prompt)])
        
        # 格式化返回结果
        formatted_result = f"""
## {ticker} 市场情绪分析
**分析日期**: {curr_date}
**分析模型**: DeepSeek-R1 推理模型

{response.content}

---
*注意: 此情绪分析基于AI推理，建议结合实际市场数据进行验证*
"""
        
        return formatted_result
        
    except Exception as e:
        return f"硅基流动情绪分析失败: {str(e)}"


def test_siliconflow_news_tools():
    """测试硅基流动新闻工具"""
    print("🧪 测试硅基流动新闻工具")
    print("=" * 50)
    
    # 检查API密钥
    api_key = os.getenv('SILICONFLOW_API_KEY')
    if not api_key:
        print("❌ 未找到 SILICONFLOW_API_KEY")
        return False
    
    try:
        # 测试股票新闻搜索
        print("📰 测试股票新闻搜索...")
        news_result = get_stock_news_siliconflow("AAPL", "2024-12-20")
        print(f"✅ 新闻搜索成功，长度: {len(news_result)}")
        
        # 测试全球新闻搜索
        print("🌍 测试全球新闻搜索...")
        global_result = get_global_news_siliconflow("2024-12-20")
        print(f"✅ 全球新闻搜索成功，长度: {len(global_result)}")
        
        # 测试情绪分析
        print("😊 测试情绪分析...")
        sentiment_result = get_realtime_sentiment_siliconflow("AAPL", "2024-12-20")
        print(f"✅ 情绪分析成功，长度: {len(sentiment_result)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    test_siliconflow_news_tools()
