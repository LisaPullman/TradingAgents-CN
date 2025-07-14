#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硅基流动 API 演示
展示如何使用硅基流动进行股票分析
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG


def check_api_keys():
    """检查必需的API密钥"""
    print("🔑 检查API密钥配置")
    print("=" * 50)
    
    # 检查硅基流动API密钥
    siliconflow_key = os.getenv('SILICONFLOW_API_KEY')
    if not siliconflow_key:
        print("❌ 错误: 未找到 SILICONFLOW_API_KEY 环境变量")
        print("💡 获取方式:")
        print("   1. 访问 https://siliconflow.cn")
        print("   2. 注册账号并获取API密钥")
        print("   3. 设置环境变量: export SILICONFLOW_API_KEY=your_api_key")
        return False
    
    # 检查FinnHub API密钥（用于获取美股数据）
    finnhub_key = os.getenv('FINNHUB_API_KEY')
    if not finnhub_key:
        print("⚠️ 警告: 未找到 FINNHUB_API_KEY，美股数据功能可能受限")
        print("💡 获取方式:")
        print("   1. 访问 https://finnhub.io")
        print("   2. 注册免费账号获取API密钥")
        print("   3. 设置环境变量: export FINNHUB_API_KEY=your_api_key")
    else:
        print(f"✅ FinnHub API 密钥: {finnhub_key[:10]}...")
    
    print(f"✅ 硅基流动 API 密钥: {siliconflow_key[:10]}...")
    print()
    return True


def demo_siliconflow_models():
    """演示不同的硅基流动模型"""
    print("🤖 硅基流动模型演示")
    print("=" * 50)
    
    # 测试不同模型的配置
    model_configs = [
        {
            "name": "DeepSeek Chat",
            "deep_model": "deepseek-chat",
            "quick_model": "deepseek-chat",
            "description": "DeepSeek 通用对话模型 - 成本效益高"
        },
        {
            "name": "通义千问 Plus",
            "deep_model": "qwen-plus",
            "quick_model": "qwen-turbo",
            "description": "阿里通义千问 - 中文优化"
        },
        {
            "name": "Claude 3 Sonnet",
            "deep_model": "claude-3-sonnet",
            "quick_model": "claude-3-haiku",
            "description": "Anthropic Claude - 安全性高"
        },
        {
            "name": "GPT-4o",
            "deep_model": "gpt-4o",
            "quick_model": "gpt-4o-mini",
            "description": "OpenAI GPT-4o - 多模态能力"
        }
    ]
    
    for i, model_config in enumerate(model_configs, 1):
        print(f"{i}. {model_config['name']}")
        print(f"   深度思考: {model_config['deep_model']}")
        print(f"   快速任务: {model_config['quick_model']}")
        print(f"   特点: {model_config['description']}")
        print()
    
    # 让用户选择模型
    while True:
        try:
            choice = input(f"请选择模型配置 (1-{len(model_configs)}) [默认: 1]: ").strip()
            if not choice:
                choice = "1"
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(model_configs):
                selected_config = model_configs[choice_idx]
                break
            else:
                print(f"❌ 请输入 1-{len(model_configs)} 之间的数字")
        except ValueError:
            print("❌ 请输入有效的数字")
    
    return selected_config


def run_siliconflow_analysis():
    """运行硅基流动股票分析"""
    print("🚀 硅基流动股票分析演示")
    print("=" * 60)
    
    # 检查API密钥
    if not check_api_keys():
        return
    
    # 选择模型配置
    model_config = demo_siliconflow_models()
    
    print(f"📊 选择的配置: {model_config['name']}")
    print(f"   深度思考模型: {model_config['deep_model']}")
    print(f"   快速思考模型: {model_config['quick_model']}")
    print()
    
    # 创建硅基流动配置
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "siliconflow"
    config["deep_think_llm"] = model_config["deep_model"]
    config["quick_think_llm"] = model_config["quick_model"]
    config["max_debate_rounds"] = 1  # 减少辩论轮次以降低成本
    config["online_tools"] = True
    
    print("📊 配置信息:")
    print(f"  LLM 提供商: {config['llm_provider']}")
    print(f"  深度思考模型: {config['deep_think_llm']}")
    print(f"  快速思考模型: {config['quick_think_llm']}")
    print(f"  最大辩论轮次: {config['max_debate_rounds']}")
    print(f"  在线工具: {config['online_tools']}")
    print()
    
    # 选择股票
    stock_options = [
        ("AAPL", "苹果公司 - 美股科技股"),
        ("TSLA", "特斯拉 - 美股电动车"),
        ("NVDA", "英伟达 - 美股AI芯片"),
        ("000001", "平安银行 - A股银行"),
        ("600036", "招商银行 - A股银行"),
        ("000858", "五粮液 - A股白酒")
    ]
    
    print("📈 可选股票:")
    for i, (symbol, name) in enumerate(stock_options, 1):
        print(f"  {i}. {symbol} - {name}")
    
    while True:
        try:
            choice = input(f"请选择股票 (1-{len(stock_options)}) [默认: 1]: ").strip()
            if not choice:
                choice = "1"
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(stock_options):
                selected_stock, stock_name = stock_options[choice_idx]
                break
            else:
                print(f"❌ 请输入 1-{len(stock_options)} 之间的数字")
        except ValueError:
            print("❌ 请输入有效的数字")
    
    print(f"\n🎯 选择的股票: {selected_stock} - {stock_name}")
    print()
    
    try:
        # 初始化TradingAgents
        print("🔄 初始化TradingAgents...")
        ta = TradingAgentsGraph(
            selected_analysts=["market", "fundamentals"],  # 减少分析师数量以降低成本
            debug=True,
            config=config
        )
        print("✅ TradingAgents初始化成功")
        print()
        
        # 运行分析
        print(f"🔍 开始分析 {selected_stock}...")
        print("⏳ 这可能需要几分钟时间，请耐心等待...")
        print()
        
        state, decision = ta.propagate(selected_stock, "2024-12-20")
        
        print("🎉 分析完成!")
        print("=" * 60)
        print(decision)
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
        print("💡 建议:")
        print("  1. 检查网络连接")
        print("  2. 确认API密钥有效")
        print("  3. 检查API配额是否充足")


def test_siliconflow_connection():
    """测试硅基流动连接"""
    print("🧪 硅基流动连接测试")
    print("=" * 50)
    
    try:
        from tradingagents.llm_adapters.siliconflow_adapter import test_siliconflow_connection
        
        if test_siliconflow_connection():
            print("✅ 硅基流动连接测试成功")
            return True
        else:
            print("❌ 硅基流动连接测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 连接测试出错: {e}")
        return False


def main():
    """主函数"""
    print("🌟 TradingAgents-CN 硅基流动集成演示")
    print("=" * 60)
    print("硅基流动提供多种顶级AI模型的统一API接口")
    print("支持 DeepSeek、Qwen、Claude、GPT 等多种模型")
    print("=" * 60)
    print()
    
    # 测试连接
    if not test_siliconflow_connection():
        print("❌ 硅基流动连接失败，请检查配置")
        return
    
    print()
    
    # 运行分析演示
    run_siliconflow_analysis()


if __name__ == "__main__":
    main()
