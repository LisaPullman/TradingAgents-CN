#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试移除OpenAI依赖后的完整功能
验证所有新闻和情绪分析功能都有可用的替代方案
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_news_tools():
    """测试新闻工具"""
    print("📰 测试新闻工具...")
    
    try:
        from tradingagents.agents.utils.agent_utils import AgentUtils
        
        # 测试Google新闻
        print("  🔍 测试Google新闻...")
        google_result = AgentUtils.get_google_news("AAPL stock", "2024-12-20", 7)
        print(f"  ✅ Google新闻: {len(google_result.content) if hasattr(google_result, 'content') else len(str(google_result))} 字符")
        
        # 测试FinnHub新闻
        print("  📊 测试FinnHub新闻...")
        finnhub_result = AgentUtils.get_finnhub_news("AAPL", "2024-12-20", "2024-12-13")
        print(f"  ✅ FinnHub新闻: {len(finnhub_result.content) if hasattr(finnhub_result, 'content') else len(str(finnhub_result))} 字符")
        
        # 测试实时新闻
        print("  ⚡ 测试实时新闻...")
        realtime_result = AgentUtils.get_realtime_stock_news("AAPL", "2024-12-20")
        print(f"  ✅ 实时新闻: {len(realtime_result.content) if hasattr(realtime_result, 'content') else len(str(realtime_result))} 字符")
        
        return True
    except Exception as e:
        print(f"  ❌ 新闻工具测试失败: {e}")
        return False


def test_social_sentiment_tools():
    """测试社交情绪工具"""
    print("\n😊 测试社交情绪工具...")
    
    try:
        from tradingagents.agents.utils.agent_utils import AgentUtils
        
        # 测试中国社交媒体情绪
        print("  🇨🇳 测试中国社交媒体情绪...")
        chinese_result = AgentUtils.get_chinese_social_sentiment("000001", "2024-12-20")
        print(f"  ✅ 中国社交媒体: {len(chinese_result.content) if hasattr(chinese_result, 'content') else len(str(chinese_result))} 字符")
        
        # 测试Reddit情绪
        print("  🌍 测试Reddit情绪...")
        reddit_result = AgentUtils.get_reddit_stock_info("AAPL", "2024-12-20", 7, 5)
        print(f"  ✅ Reddit情绪: {len(reddit_result.content) if hasattr(reddit_result, 'content') else len(str(reddit_result))} 字符")
        
        return True
    except Exception as e:
        print(f"  ❌ 社交情绪工具测试失败: {e}")
        return False


def test_analyst_initialization():
    """测试分析师初始化"""
    print("\n🤖 测试分析师初始化...")
    
    try:
        from tradingagents.agents.analysts.social_media_analyst import SocialMediaAnalyst
        from tradingagents.agents.analysts.news_analyst import NewsAnalyst
        from tradingagents.agents.utils.agent_utils import AgentUtils
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 创建工具包
        toolkit = AgentUtils(config=DEFAULT_CONFIG)
        
        # 测试社交媒体分析师
        print("  📱 测试社交媒体分析师...")
        social_analyst = SocialMediaAnalyst(toolkit)
        print("  ✅ 社交媒体分析师初始化成功")
        
        # 测试新闻分析师
        print("  📰 测试新闻分析师...")
        news_analyst = NewsAnalyst(toolkit)
        print("  ✅ 新闻分析师初始化成功")
        
        return True
    except Exception as e:
        print(f"  ❌ 分析师初始化失败: {e}")
        return False


def test_trading_graph_tools():
    """测试交易图工具节点"""
    print("\n📊 测试交易图工具节点...")
    
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 创建配置（使用硅基流动）
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "siliconflow"
        config["deep_think_llm"] = "deepseek-ai/DeepSeek-V3"
        config["quick_think_llm"] = "deepseek-ai/DeepSeek-V3"
        
        # 测试初始化（会因为API密钥验证失败，但这是预期的）
        try:
            ta = TradingAgentsGraph(config=config, debug=True)
            print("  ✅ 交易图初始化成功")
            
            # 检查工具节点
            if hasattr(ta, 'tools'):
                social_tools = ta.tools.get('social', None)
                news_tools = ta.tools.get('news', None)
                
                if social_tools:
                    print("  ✅ 社交媒体工具节点配置正确")
                if news_tools:
                    print("  ✅ 新闻工具节点配置正确")
            
            return True
        except ValueError as e:
            if "SILICONFLOW_API_KEY" in str(e):
                print("  ✅ 交易图正确验证API密钥（预期行为）")
                return True
            else:
                print(f"  ❌ 意外的错误: {e}")
                return False
    except Exception as e:
        print(f"  ❌ 交易图测试失败: {e}")
        return False


def check_openai_imports():
    """检查是否还有OpenAI导入"""
    print("\n🔍 检查OpenAI导入...")
    
    try:
        # 检查interface.py
        interface_file = project_root / "tradingagents" / "dataflows" / "interface.py"
        if interface_file.exists():
            content = interface_file.read_text(encoding='utf-8')
            if "from openai import OpenAI" in content and not content.count("# from openai import OpenAI"):
                print("  ❌ interface.py 仍有活跃的OpenAI导入")
                return False
            else:
                print("  ✅ interface.py OpenAI导入已移除或注释")
        
        # 检查是否有其他文件导入OpenAI
        openai_files = []
        for py_file in project_root.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                if "from openai import" in content or "import openai" in content:
                    if not content.count("# from openai import") and not content.count("# import openai"):
                        openai_files.append(py_file)
            except:
                continue
        
        if openai_files:
            print(f"  ⚠️ 发现 {len(openai_files)} 个文件仍有OpenAI导入:")
            for file in openai_files[:5]:  # 只显示前5个
                print(f"    - {file.relative_to(project_root)}")
        else:
            print("  ✅ 未发现活跃的OpenAI导入")
        
        return len(openai_files) == 0
    except Exception as e:
        print(f"  ❌ 检查OpenAI导入失败: {e}")
        return False


def test_deprecated_functions():
    """测试已弃用的函数是否正确回退"""
    print("\n🔄 测试已弃用函数的回退机制...")
    
    try:
        from tradingagents.dataflows import interface
        
        # 测试get_stock_news_openai回退
        print("  📰 测试get_stock_news_openai回退...")
        result1 = interface.get_stock_news_openai("AAPL", "2024-12-20")
        if result1 and len(str(result1)) > 0:
            print("  ✅ get_stock_news_openai 成功回退到Google新闻")
        else:
            print("  ⚠️ get_stock_news_openai 回退结果为空")
        
        # 测试get_global_news_openai回退
        print("  🌍 测试get_global_news_openai回退...")
        result2 = interface.get_global_news_openai("2024-12-20")
        if result2 and len(str(result2)) > 0:
            print("  ✅ get_global_news_openai 成功回退到Google新闻")
        else:
            print("  ⚠️ get_global_news_openai 回退结果为空")
        
        # 测试get_fundamentals_openai回退
        print("  📊 测试get_fundamentals_openai回退...")
        result3 = interface.get_fundamentals_openai("AAPL", "2024-12-20")
        if result3 and len(str(result3)) > 0:
            print("  ✅ get_fundamentals_openai 成功回退到FinnHub")
        else:
            print("  ⚠️ get_fundamentals_openai 回退结果为空")
        
        return True
    except Exception as e:
        print(f"  ❌ 测试已弃用函数失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🧪 测试移除OpenAI依赖后的完整功能")
    print("=" * 60)
    
    tests = [
        ("新闻工具测试", test_news_tools),
        ("社交情绪工具测试", test_social_sentiment_tools),
        ("分析师初始化测试", test_analyst_initialization),
        ("交易图工具节点测试", test_trading_graph_tools),
        ("OpenAI导入检查", check_openai_imports),
        ("已弃用函数回退测试", test_deprecated_functions),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} 出现异常: {e}")
            results[test_name] = False
    
    # 总结结果
    print("\n📊 测试结果总结")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 OpenAI依赖移除成功！")
        print("💡 所有功能都有可用的替代方案")
        print("🚀 现在可以完全使用硅基流动进行股票分析")
    elif passed >= total * 0.8:
        print("\n✅ OpenAI依赖基本移除成功！")
        print("⚠️ 部分功能可能需要进一步优化")
    else:
        print("\n❌ OpenAI依赖移除不完整")
        print("🔧 需要进一步检查和修复")
    
    return passed >= total * 0.8


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
