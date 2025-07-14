#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硅基流动简单测试
测试硅基流动API的基本功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_basic_chat():
    """测试基本对话功能"""
    print("🤖 硅基流动基本对话测试")
    print("=" * 50)
    
    # 检查API密钥
    api_key = os.getenv('SILICONFLOW_API_KEY')
    if not api_key:
        print("❌ 未找到 SILICONFLOW_API_KEY 环境变量")
        print("💡 请设置: export SILICONFLOW_API_KEY=your_api_key")
        return False
    
    print(f"✅ API密钥: {api_key[:10]}...")
    
    try:
        from tradingagents.llm_adapters.siliconflow_adapter import create_siliconflow_llm
        from langchain_core.messages import HumanMessage
        
        # 创建模型实例
        print("\n🔧 创建DeepSeek模型实例...")
        llm = create_siliconflow_llm(
            model="deepseek-chat",
            temperature=0.1,
            max_tokens=500
        )
        
        # 测试简单对话
        print("💬 测试简单对话...")
        response = llm.invoke([HumanMessage(content="你好，请简单介绍一下你自己。")])
        print(f"🤖 回复: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_financial_analysis():
    """测试金融分析功能"""
    print("\n📈 硅基流动金融分析测试")
    print("=" * 50)
    
    try:
        from tradingagents.llm_adapters.siliconflow_adapter import create_siliconflow_llm
        from langchain_core.messages import HumanMessage
        
        # 创建模型实例
        print("🔧 创建Qwen模型实例...")
        llm = create_siliconflow_llm(
            model="qwen-plus",
            temperature=0.1,
            max_tokens=1000
        )
        
        # 测试金融分析
        print("📊 测试金融分析...")
        financial_prompt = """
        请分析苹果公司(AAPL)的投资价值，从以下角度：
        1. 公司基本面
        2. 技术面分析
        3. 市场前景
        4. 风险因素
        5. 投资建议
        
        请简洁回答，每个方面2-3句话即可。
        """
        
        response = llm.invoke([HumanMessage(content=financial_prompt)])
        print(f"📈 分析结果:\n{response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ 金融分析测试失败: {e}")
        return False


def test_model_comparison():
    """测试不同模型的表现"""
    print("\n🔄 硅基流动模型对比测试")
    print("=" * 50)
    
    models_to_test = [
        ("deepseek-chat", "DeepSeek Chat"),
        ("qwen-turbo", "通义千问 Turbo"),
        ("gpt-4o-mini", "GPT-4o Mini")
    ]
    
    question = "请用一句话总结比特币的投资风险。"
    
    for model_id, model_name in models_to_test:
        try:
            print(f"\n🧠 测试 {model_name}...")
            
            from tradingagents.llm_adapters.siliconflow_adapter import create_siliconflow_llm
            from langchain_core.messages import HumanMessage
            
            llm = create_siliconflow_llm(
                model=model_id,
                temperature=0.1,
                max_tokens=200
            )
            
            response = llm.invoke([HumanMessage(content=question)])
            print(f"✅ {model_name}: {response.content}")
            
        except Exception as e:
            print(f"❌ {model_name} 测试失败: {e}")


def test_tool_calling():
    """测试工具调用功能"""
    print("\n🔧 硅基流动工具调用测试")
    print("=" * 50)
    
    try:
        from tradingagents.llm_adapters.siliconflow_adapter import create_siliconflow_llm
        from langchain_core.messages import HumanMessage
        from langchain_core.tools import tool
        
        # 定义一个简单的工具
        @tool
        def get_stock_price(symbol: str) -> str:
            """获取股票价格（模拟）"""
            prices = {
                "AAPL": "$150.25",
                "TSLA": "$245.67",
                "NVDA": "$890.12"
            }
            return f"{symbol}的当前价格是{prices.get(symbol, '未知')}"
        
        # 创建支持工具调用的模型
        print("🔧 创建支持工具调用的模型...")
        llm = create_siliconflow_llm(
            model="deepseek-chat",
            temperature=0.1,
            max_tokens=500
        )
        
        # 绑定工具
        llm_with_tools = llm.bind_tools([get_stock_price])
        
        # 测试工具调用
        print("🛠️ 测试工具调用...")
        response = llm_with_tools.invoke([
            HumanMessage(content="请帮我查询AAPL和TSLA的股票价格")
        ])
        
        print(f"🤖 回复: {response.content}")
        
        # 检查是否有工具调用
        if hasattr(response, 'tool_calls') and response.tool_calls:
            print("✅ 工具调用成功")
            for tool_call in response.tool_calls:
                print(f"🔧 调用工具: {tool_call['name']}")
                print(f"📝 参数: {tool_call['args']}")
        else:
            print("⚠️ 未检测到工具调用")
        
        return True
        
    except Exception as e:
        print(f"❌ 工具调用测试失败: {e}")
        return False


def main():
    """主函数"""
    print("🌟 硅基流动简单测试")
    print("=" * 60)
    print("测试硅基流动API的基本功能")
    print("=" * 60)
    
    tests = [
        ("基本对话", test_basic_chat),
        ("金融分析", test_financial_analysis),
        ("模型对比", test_model_comparison),
        ("工具调用", test_tool_calling),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} 出现异常: {e}")
            results[test_name] = False
    
    # 总结结果
    print(f"\n{'='*20} 测试结果总结 {'='*20}")
    
    passed = 0
    total = len(tests)
    
    for test_name, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{total} 测试通过")
    
    if passed > 0:
        print("\n🎉 硅基流动API集成成功！")
        print("\n💡 使用建议:")
        print("  1. DeepSeek Chat: 成本效益高，适合日常分析")
        print("  2. Qwen Plus: 中文优化，适合A股分析")
        print("  3. GPT-4o Mini: 快速响应，适合简单任务")
        print("  4. Claude 3 Sonnet: 安全性高，适合专业分析")
    else:
        print("❌ 所有测试失败，请检查API密钥和网络连接")


if __name__ == "__main__":
    main()
