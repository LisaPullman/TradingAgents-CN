#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高性能模型配置示例
演示如何为每个分析师配置价格最贵、性能最好的专用模型
"""

import os
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph


def create_high_performance_config():
    """创建高性能模型配置"""
    
    # 基于默认配置创建高性能配置
    config = DEFAULT_CONFIG.copy()
    
    # 确保使用硅基流动作为提供商
    config["llm_provider"] = "siliconflow"
    
    # 🥇 最高性能配置 - 优先选择价格最贵、性能最好的模型
    config.update({
        # 深度思考层 - 最终决策使用最强模型
        "deep_think_llm": "Qwen/Qwen2.5-72B-Instruct",      # 72B参数，最高性能
        "quick_think_llm": "deepseek-ai/DeepSeek-R1",       # 推理专用，快速响应
        
        # 专业化分析师配置 - 每个分析师使用最适合的高端模型
        "market_analyst_llm": "meta-llama/Llama-3.1-70B-Instruct",      # 技术分析：70B参数，128K上下文
        "fundamentals_analyst_llm": "Qwen/Qwen2.5-72B-Instruct",        # 基本面分析：72B参数，最强计算
        "news_analyst_llm": "deepseek-ai/DeepSeek-R1",                  # 新闻分析：推理专用，逻辑分析
        "social_analyst_llm": "Qwen/Qwen2.5-32B-Instruct",             # 社交媒体：32B参数，中文优化
        
        # 增强性能设置
        "max_debate_rounds": 2,          # 增加辩论轮次，充分利用高性能模型
        "max_risk_discuss_rounds": 2,    # 增加风险讨论轮次
        "online_tools": True,            # 启用在线工具
    })
    
    return config


def demo_high_performance_analysis():
    """演示高性能模型分析"""
    
    print("🚀 高性能模型配置演示")
    print("=" * 60)
    
    # 检查API密钥
    api_key = os.getenv('SILICONFLOW_API_KEY')
    if not api_key:
        print("❌ 请先设置 SILICONFLOW_API_KEY 环境变量")
        print("💡 获取地址: https://siliconflow.cn/")
        return False
    
    print(f"✅ 硅基流动 API 密钥: {api_key[:10]}...")
    
    # 创建高性能配置
    config = create_high_performance_config()
    
    print("\n📊 高性能模型配置:")
    print(f"  🧠 深度思考模型: {config['deep_think_llm']}")
    print(f"  ⚡ 快速思考模型: {config['quick_think_llm']}")
    print(f"  📈 市场分析师: {config['market_analyst_llm']}")
    print(f"  💰 基本面分析师: {config['fundamentals_analyst_llm']}")
    print(f"  📰 新闻分析师: {config['news_analyst_llm']}")
    print(f"  💭 社交媒体分析师: {config['social_analyst_llm']}")
    
    print("\n🎯 模型性能特点:")
    print("  🥇 Qwen 2.5 72B - 最高性能，72B参数，复杂推理")
    print("  🥈 Llama 3.1 70B - 超强性能，128K上下文，长文本处理")
    print("  🥉 DeepSeek R1 - 推理专用，逻辑分析能力最强")
    print("  🎯 Qwen 2.5 32B - 中文优化，情绪理解能力强")
    
    try:
        # 创建交易分析图
        print("\n🔧 初始化高性能交易分析图...")
        ta = TradingAgentsGraph(
            selected_analysts=["market", "fundamentals", "news", "social"],
            debug=True,
            config=config
        )
        
        print("✅ 高性能交易分析图初始化成功")
        
        # 演示分析（可选）
        demo_analysis = input("\n是否运行演示分析？(y/N): ").strip().lower()
        if demo_analysis == 'y':
            print("\n🎯 运行高性能股票分析...")
            
            # 选择股票
            ticker = input("请输入股票代码 (默认: AAPL): ").strip() or "AAPL"
            date = input("请输入分析日期 (默认: 2024-12-20): ").strip() or "2024-12-20"
            
            print(f"\n📊 开始分析 {ticker} ({date})...")
            print("⏳ 使用高性能模型进行深度分析，请稍候...")
            
            try:
                state, decision = ta.propagate(ticker, date)
                
                print("\n🎉 高性能分析完成！")
                print("=" * 60)
                print(decision)
                
            except Exception as e:
                print(f"❌ 分析过程出错: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False


def show_model_comparison():
    """显示模型性能对比"""
    
    print("\n📊 硅基流动模型性能对比")
    print("=" * 80)
    
    models = [
        {
            "name": "Qwen/Qwen2.5-72B-Instruct",
            "params": "72B",
            "context": "32K",
            "performance": "🥇 最高",
            "price": "💰💰💰💰💰",
            "best_for": "复杂推理、基本面分析、最终决策"
        },
        {
            "name": "meta-llama/Llama-3.1-70B-Instruct", 
            "params": "70B",
            "context": "128K",
            "performance": "🥈 超强",
            "price": "💰💰💰💰",
            "best_for": "长文本处理、技术分析、数据处理"
        },
        {
            "name": "deepseek-ai/DeepSeek-R1",
            "params": "未知",
            "context": "64K", 
            "performance": "🥉 推理专用",
            "price": "💰💰💰",
            "best_for": "逻辑推理、新闻分析、快速思考"
        },
        {
            "name": "Qwen/Qwen2.5-32B-Instruct",
            "params": "32B",
            "context": "32K",
            "performance": "🎯 中文优化",
            "price": "💰💰",
            "best_for": "中文理解、情绪分析、社交媒体"
        }
    ]
    
    for model in models:
        print(f"\n🤖 {model['name']}")
        print(f"   参数规模: {model['params']}")
        print(f"   上下文长度: {model['context']}")
        print(f"   性能等级: {model['performance']}")
        print(f"   价格等级: {model['price']}")
        print(f"   最适合: {model['best_for']}")


def main():
    """主函数"""
    
    print("🚀 TradingAgents-CN 高性能模型配置")
    print("=" * 60)
    print("🎯 目标: 为每个分析师配置价格最贵、性能最好的专用模型")
    print("=" * 60)
    
    # 显示模型对比
    show_model_comparison()
    
    # 演示配置
    print("\n" + "=" * 60)
    success = demo_high_performance_analysis()
    
    if success:
        print("\n🎉 高性能模型配置演示完成！")
        print("\n💡 使用建议:")
        print("  1. 确保有足够的API配额（高性能模型消耗较大）")
        print("  2. 监控API使用成本")
        print("  3. 根据实际需求调整分析师组合")
        print("  4. 可以通过环境变量自定义模型选择")
        
        print("\n🔧 环境变量配置:")
        print("  export SILICONFLOW_API_KEY=your_api_key")
        print("  export MARKET_ANALYST_LLM=meta-llama/Llama-3.1-70B-Instruct")
        print("  export FUNDAMENTALS_ANALYST_LLM=Qwen/Qwen2.5-72B-Instruct")
        print("  export NEWS_ANALYST_LLM=deepseek-ai/DeepSeek-R1")
        print("  export SOCIAL_ANALYST_LLM=Qwen/Qwen2.5-32B-Instruct")
    else:
        print("\n❌ 演示失败，请检查配置和API密钥")


if __name__ == "__main__":
    main()
