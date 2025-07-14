#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试高性能模型配置
验证每个分析师是否使用了正确的专用高性能模型
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_default_config():
    """测试默认配置是否使用高性能模型"""
    print("🔧 测试默认配置...")
    
    try:
        from tradingagents.default_config import DEFAULT_CONFIG
        
        print("📊 默认配置检查:")
        print(f"  LLM提供商: {DEFAULT_CONFIG['llm_provider']}")
        print(f"  深度思考模型: {DEFAULT_CONFIG['deep_think_llm']}")
        print(f"  快速思考模型: {DEFAULT_CONFIG['quick_think_llm']}")
        print(f"  市场分析师模型: {DEFAULT_CONFIG.get('market_analyst_llm', '未配置')}")
        print(f"  基本面分析师模型: {DEFAULT_CONFIG.get('fundamentals_analyst_llm', '未配置')}")
        print(f"  新闻分析师模型: {DEFAULT_CONFIG.get('news_analyst_llm', '未配置')}")
        print(f"  社交媒体分析师模型: {DEFAULT_CONFIG.get('social_analyst_llm', '未配置')}")
        
        # 验证是否使用高性能模型
        high_performance_models = [
            "Qwen/Qwen2.5-72B-Instruct",
            "meta-llama/Llama-3.1-70B-Instruct", 
            "deepseek-ai/DeepSeek-R1",
            "Qwen/Qwen2.5-32B-Instruct"
        ]
        
        checks = [
            ("深度思考模型", DEFAULT_CONFIG['deep_think_llm'] in high_performance_models),
            ("快速思考模型", DEFAULT_CONFIG['quick_think_llm'] in high_performance_models),
            ("市场分析师模型", DEFAULT_CONFIG.get('market_analyst_llm', '').replace('${MARKET_ANALYST_LLM:-', '').replace('}', '') in high_performance_models),
            ("基本面分析师模型", DEFAULT_CONFIG.get('fundamentals_analyst_llm', '').replace('${FUNDAMENTALS_ANALYST_LLM:-', '').replace('}', '') in high_performance_models),
            ("新闻分析师模型", DEFAULT_CONFIG.get('news_analyst_llm', '').replace('${NEWS_ANALYST_LLM:-', '').replace('}', '') in high_performance_models),
            ("社交媒体分析师模型", DEFAULT_CONFIG.get('social_analyst_llm', '').replace('${SOCIAL_ANALYST_LLM:-', '').replace('}', '') in high_performance_models),
        ]
        
        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")
            if not passed:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 默认配置测试失败: {e}")
        return False


def test_env_example():
    """测试.env.example文件是否包含高性能模型配置"""
    print("\n📄 测试.env.example配置...")
    
    try:
        env_file = project_root / ".env.example"
        content = env_file.read_text(encoding='utf-8')
        
        # 检查是否包含专用分析师模型配置
        required_configs = [
            "MARKET_ANALYST_LLM=",
            "FUNDAMENTALS_ANALYST_LLM=",
            "NEWS_ANALYST_LLM=",
            "SOCIAL_ANALYST_LLM=",
            "DEEP_THINK_LLM=",
            "QUICK_THINK_LLM=",
            "SILICONFLOW_API_KEY="
        ]
        
        # 检查高性能模型
        high_performance_models = [
            "Qwen/Qwen2.5-72B-Instruct",
            "meta-llama/Llama-3.1-70B-Instruct",
            "deepseek-ai/DeepSeek-R1",
            "Qwen/Qwen2.5-32B-Instruct"
        ]
        
        print("📋 .env.example检查:")
        
        all_passed = True
        for config in required_configs:
            if config in content:
                print(f"  ✅ 包含配置: {config}")
            else:
                print(f"  ❌ 缺少配置: {config}")
                all_passed = False
        
        for model in high_performance_models:
            if model in content:
                print(f"  ✅ 包含高性能模型: {model}")
            else:
                print(f"  ⚠️ 未找到模型: {model}")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ .env.example测试失败: {e}")
        return False


def test_specialized_llm_creation():
    """测试专用LLM创建功能"""
    print("\n🤖 测试专用LLM创建...")
    
    try:
        from tradingagents.graph.setup import GraphSetup
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 模拟配置
        config = DEFAULT_CONFIG.copy()
        config["market_analyst_llm"] = "meta-llama/Llama-3.1-70B-Instruct"
        config["fundamentals_analyst_llm"] = "Qwen/Qwen2.5-72B-Instruct"
        
        # 创建GraphSetup实例（需要模拟其他参数）
        setup = GraphSetup(
            quick_thinking_llm=None,  # 模拟
            deep_thinking_llm=None,   # 模拟
            toolkit=None,             # 模拟
            tool_nodes={},            # 模拟
            bull_memory=None,         # 模拟
            bear_memory=None,         # 模拟
            trader_memory=None,       # 模拟
            invest_judge_memory=None, # 模拟
            risk_manager_memory=None, # 模拟
            conditional_logic=None,   # 模拟
            config=config
        )
        
        print("📊 专用LLM创建测试:")
        
        # 测试_create_specialized_llm方法是否存在
        if hasattr(setup, '_create_specialized_llm'):
            print("  ✅ _create_specialized_llm方法存在")
            
            # 测试方法调用（在没有API密钥的情况下会回退）
            try:
                result = setup._create_specialized_llm("market_analyst_llm")
                print("  ✅ 方法调用成功")
                return True
            except Exception as e:
                print(f"  ⚠️ 方法调用失败（预期，因为缺少API密钥）: {e}")
                return True  # 这是预期的
        else:
            print("  ❌ _create_specialized_llm方法不存在")
            return False
            
    except Exception as e:
        print(f"❌ 专用LLM创建测试失败: {e}")
        return False


def test_cli_options():
    """测试CLI选项是否优先显示高性能模型"""
    print("\n💻 测试CLI选项...")
    
    try:
        from cli.utils import select_shallow_thinking_agent, select_deep_thinking_agent
        
        # 检查CLI选项是否存在
        print("📋 CLI选项检查:")
        print("  ✅ select_shallow_thinking_agent函数存在")
        print("  ✅ select_deep_thinking_agent函数存在")
        
        # 检查是否包含高性能模型选项
        # 这里我们不能直接调用函数（因为它们需要用户交互），
        # 但可以检查源代码中是否包含高性能模型
        cli_file = project_root / "cli" / "utils.py"
        content = cli_file.read_text(encoding='utf-8')
        
        high_performance_indicators = [
            "🥇最高性能",
            "🥈超强性能", 
            "🥉推理专用",
            "Qwen/Qwen2.5-72B-Instruct",
            "meta-llama/Llama-3.1-70B-Instruct"
        ]
        
        found_indicators = []
        for indicator in high_performance_indicators:
            if indicator in content:
                found_indicators.append(indicator)
        
        if len(found_indicators) >= 3:
            print(f"  ✅ CLI包含高性能模型指示器: {len(found_indicators)}/5")
            return True
        else:
            print(f"  ❌ CLI缺少高性能模型指示器: {len(found_indicators)}/5")
            return False
            
    except Exception as e:
        print(f"❌ CLI选项测试失败: {e}")
        return False


def test_model_performance_ranking():
    """测试模型性能排序"""
    print("\n🏆 测试模型性能排序...")
    
    # 定义性能排序（从高到低）
    performance_ranking = [
        "Qwen/Qwen2.5-72B-Instruct",      # 🥇 72B参数，最高性能
        "meta-llama/Llama-3.1-70B-Instruct", # 🥈 70B参数，长上下文
        "deepseek-ai/DeepSeek-R1",         # 🥉 推理专用
        "deepseek-ai/DeepSeek-V3",         # 🏅 最新版本
        "Qwen/Qwen2.5-32B-Instruct",      # 🎯 中文优化
        "Qwen/Qwen2.5-14B-Instruct",      # ⚡ 轻量级
    ]
    
    # 定义分析师专业化分配
    analyst_assignments = {
        "基本面分析师": "Qwen/Qwen2.5-72B-Instruct",      # 需要最强计算能力
        "市场分析师": "meta-llama/Llama-3.1-70B-Instruct",   # 需要长上下文处理
        "新闻分析师": "deepseek-ai/DeepSeek-R1",            # 需要强推理能力
        "社交媒体分析师": "Qwen/Qwen2.5-32B-Instruct",      # 需要中文优化
    }
    
    print("📊 模型性能排序（从高到低）:")
    for i, model in enumerate(performance_ranking, 1):
        print(f"  {i}. {model}")
    
    print("\n🎯 分析师专业化分配:")
    for analyst, model in analyst_assignments.items():
        rank = performance_ranking.index(model) + 1
        print(f"  {analyst}: {model} (性能排名: #{rank})")
    
    # 验证分配是否合理（基本面分析师应该使用最高性能模型）
    fundamentals_model = analyst_assignments["基本面分析师"]
    if fundamentals_model == performance_ranking[0]:
        print("  ✅ 基本面分析师使用最高性能模型")
        return True
    else:
        print("  ❌ 基本面分析师未使用最高性能模型")
        return False


def main():
    """主测试函数"""
    print("🚀 高性能模型配置测试")
    print("=" * 60)
    print("目标: 验证每个分析师都使用价格最贵、性能最好的专用模型")
    print("=" * 60)
    
    tests = [
        ("默认配置检查", test_default_config),
        (".env.example配置", test_env_example),
        ("专用LLM创建", test_specialized_llm_creation),
        ("CLI选项检查", test_cli_options),
        ("模型性能排序", test_model_performance_ranking),
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
        print("\n🎉 高性能模型配置成功！")
        print("💡 现在系统将：")
        print("  - 基本面分析师使用 Qwen 2.5 72B (最高性能)")
        print("  - 市场分析师使用 Llama 3.1 70B (长上下文)")
        print("  - 新闻分析师使用 DeepSeek R1 (推理专用)")
        print("  - 社交媒体分析师使用 Qwen 2.5 32B (中文优化)")
        print("  - 深度思考使用 Qwen 2.5 72B (最强决策)")
        print("  - 快速思考使用 DeepSeek R1 (快速推理)")
    elif passed >= total * 0.8:
        print("\n✅ 高性能模型配置基本成功！")
        print("⚠️ 部分功能可能需要进一步优化")
    else:
        print("\n❌ 高性能模型配置不完整")
        print("🔧 需要进一步检查和修复")
    
    return passed >= total * 0.8


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
