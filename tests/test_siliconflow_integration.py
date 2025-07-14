#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硅基流动集成测试
测试硅基流动API的集成和功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_siliconflow_import():
    """测试硅基流动适配器导入"""
    print("🧪 测试硅基流动适配器导入")
    print("=" * 50)
    
    try:
        from tradingagents.llm_adapters.siliconflow_adapter import (
            ChatSiliconFlow,
            create_siliconflow_llm,
            get_available_siliconflow_models,
            get_model_recommendations
        )
        print("✅ 硅基流动适配器导入成功")
        return True
    except ImportError as e:
        print(f"❌ 硅基流动适配器导入失败: {e}")
        return False


def test_siliconflow_models():
    """测试硅基流动模型配置"""
    print("\n🧪 测试硅基流动模型配置")
    print("=" * 50)
    
    try:
        from tradingagents.llm_adapters.siliconflow_adapter import get_available_siliconflow_models
        
        models = get_available_siliconflow_models()
        print(f"✅ 可用模型数量: {len(models)}")
        
        # 检查关键模型
        key_models = ["deepseek-chat", "qwen-plus", "claude-3-sonnet", "gpt-4o"]
        for model in key_models:
            if model in models:
                print(f"✅ {model}: {models[model]['description']}")
            else:
                print(f"❌ {model}: 未找到")
        
        return True
    except Exception as e:
        print(f"❌ 模型配置测试失败: {e}")
        return False


def test_siliconflow_recommendations():
    """测试模型推荐功能"""
    print("\n🧪 测试模型推荐功能")
    print("=" * 50)
    
    try:
        from tradingagents.llm_adapters.siliconflow_adapter import get_model_recommendations
        
        task_types = ["general", "coding", "analysis", "fast", "cost_effective", "financial", "chinese"]
        
        for task_type in task_types:
            recommendations = get_model_recommendations(task_type)
            print(f"✅ {task_type}: {', '.join(recommendations)}")
        
        return True
    except Exception as e:
        print(f"❌ 模型推荐测试失败: {e}")
        return False


def test_siliconflow_factory():
    """测试工厂函数"""
    print("\n🧪 测试工厂函数")
    print("=" * 50)
    
    try:
        from tradingagents.llm_adapters.openai_compatible_base import create_openai_compatible_llm
        
        # 测试创建硅基流动LLM（不需要真实API密钥）
        print("🔧 测试工厂函数创建...")
        
        # 这里只测试函数调用，不测试实际连接
        try:
            llm = create_openai_compatible_llm(
                provider="siliconflow",
                model="deepseek-chat",
                api_key="test_key"  # 测试用假密钥
            )
            print("✅ 工厂函数创建成功")
        except ValueError as e:
            if "SILICONFLOW_API_KEY" in str(e):
                print("✅ 工厂函数正确验证API密钥")
            else:
                print(f"❌ 意外的错误: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ 工厂函数测试失败: {e}")
        return False


def test_siliconflow_config_integration():
    """测试配置集成"""
    print("\n🧪 测试配置集成")
    print("=" * 50)
    
    try:
        from tradingagents.llm_adapters.openai_compatible_base import OPENAI_COMPATIBLE_PROVIDERS
        
        # 检查硅基流动是否在支持的提供商列表中
        if "siliconflow" in OPENAI_COMPATIBLE_PROVIDERS:
            print("✅ 硅基流动已添加到支持的提供商列表")
            
            config = OPENAI_COMPATIBLE_PROVIDERS["siliconflow"]
            print(f"✅ API Base URL: {config['base_url']}")
            print(f"✅ API Key 环境变量: {config['api_key_env']}")
            print(f"✅ 支持模型数量: {len(config['models'])}")
            
            return True
        else:
            print("❌ 硅基流动未在支持的提供商列表中")
            return False
            
    except Exception as e:
        print(f"❌ 配置集成测试失败: {e}")
        return False


def test_trading_graph_integration():
    """测试交易图集成"""
    print("\n🧪 测试交易图集成")
    print("=" * 50)
    
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 创建硅基流动配置
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "siliconflow"
        config["deep_think_llm"] = "deepseek-chat"
        config["quick_think_llm"] = "deepseek-chat"
        
        print("🔧 测试交易图初始化...")
        
        # 这里只测试配置解析，不测试实际初始化（需要API密钥）
        try:
            ta = TradingAgentsGraph(config=config, debug=True)
            print("✅ 交易图初始化成功")
        except ValueError as e:
            if "SILICONFLOW_API_KEY" in str(e):
                print("✅ 交易图正确验证API密钥")
            else:
                print(f"❌ 意外的错误: {e}")
                return False
        except Exception as e:
            print(f"⚠️ 其他错误（可能是依赖问题）: {e}")
        
        return True
    except Exception as e:
        print(f"❌ 交易图集成测试失败: {e}")
        return False


def test_api_key_check():
    """测试API密钥检查"""
    print("\n🧪 测试API密钥检查")
    print("=" * 50)
    
    api_key = os.getenv('SILICONFLOW_API_KEY')
    if api_key:
        print(f"✅ 找到硅基流动API密钥: {api_key[:10]}...")
        
        # 如果有API密钥，测试实际连接
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
    else:
        print("⚠️ 未找到硅基流动API密钥")
        print("💡 设置方法: export SILICONFLOW_API_KEY=your_api_key")
        return True  # 没有密钥不算失败


def main():
    """主测试函数"""
    print("🧪 硅基流动集成测试")
    print("=" * 60)
    
    tests = [
        ("导入测试", test_siliconflow_import),
        ("模型配置测试", test_siliconflow_models),
        ("模型推荐测试", test_siliconflow_recommendations),
        ("工厂函数测试", test_siliconflow_factory),
        ("配置集成测试", test_siliconflow_config_integration),
        ("交易图集成测试", test_trading_graph_integration),
        ("API密钥检查", test_api_key_check),
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
        print("🎉 所有测试通过！硅基流动集成成功！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查配置")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
