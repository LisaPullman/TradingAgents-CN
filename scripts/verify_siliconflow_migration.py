#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硅基流动迁移验证脚本
验证迁移是否成功完成
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_default_config():
    """检查默认配置"""
    print("🔍 检查默认配置...")
    
    try:
        from tradingagents.default_config import DEFAULT_CONFIG
        
        provider = DEFAULT_CONFIG.get("llm_provider")
        deep_model = DEFAULT_CONFIG.get("deep_think_llm")
        quick_model = DEFAULT_CONFIG.get("quick_think_llm")
        
        print(f"  LLM提供商: {provider}")
        print(f"  深度思考模型: {deep_model}")
        print(f"  快速思考模型: {quick_model}")
        
        if provider == "siliconflow":
            print("✅ 默认配置已更新为硅基流动")
            return True
        else:
            print(f"❌ 默认配置仍为: {provider}")
            return False
            
    except Exception as e:
        print(f"❌ 检查默认配置失败: {e}")
        return False


def check_api_key():
    """检查API密钥"""
    print("\n🔑 检查API密钥...")
    
    siliconflow_key = os.getenv('SILICONFLOW_API_KEY')
    if siliconflow_key:
        print(f"✅ 硅基流动API密钥: {siliconflow_key[:10]}...")
        return True
    else:
        print("❌ 未找到硅基流动API密钥")
        return False


def check_adapter_import():
    """检查适配器导入"""
    print("\n📦 检查适配器导入...")
    
    try:
        from tradingagents.llm_adapters.siliconflow_adapter import ChatSiliconFlow
        print("✅ 硅基流动适配器导入成功")
        return True
    except ImportError as e:
        print(f"❌ 硅基流动适配器导入失败: {e}")
        return False


def test_model_creation():
    """测试模型创建"""
    print("\n🤖 测试模型创建...")
    
    try:
        from tradingagents.llm_adapters.siliconflow_adapter import create_siliconflow_llm
        
        # 测试创建模型（不实际调用API）
        llm = create_siliconflow_llm(
            model="deepseek-ai/DeepSeek-V3",
            api_key="test_key"
        )
        print("✅ 模型创建成功")
        return True
    except Exception as e:
        print(f"❌ 模型创建失败: {e}")
        return False


def test_trading_graph_init():
    """测试交易图初始化"""
    print("\n📊 测试交易图初始化...")
    
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 创建硅基流动配置
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "siliconflow"
        config["deep_think_llm"] = "deepseek-ai/DeepSeek-V3"
        config["quick_think_llm"] = "deepseek-ai/DeepSeek-V3"
        
        # 测试初始化（会因为API密钥验证失败，但这是预期的）
        try:
            ta = TradingAgentsGraph(config=config, debug=True)
            print("✅ 交易图初始化成功")
            return True
        except ValueError as e:
            if "SILICONFLOW_API_KEY" in str(e):
                print("✅ 交易图正确验证API密钥")
                return True
            else:
                print(f"❌ 意外的错误: {e}")
                return False
    except Exception as e:
        print(f"❌ 交易图初始化失败: {e}")
        return False


def check_cli_options():
    """检查CLI选项"""
    print("\n💻 检查CLI选项...")
    
    try:
        from cli.utils import BASE_URLS, SHALLOW_AGENT_OPTIONS, DEEP_AGENT_OPTIONS
        
        # 检查BASE_URLS
        first_option = BASE_URLS[0][0] if BASE_URLS else ""
        if "硅基流动" in first_option:
            print("✅ CLI默认选项已更新为硅基流动")
        else:
            print(f"❌ CLI默认选项仍为: {first_option}")
            return False
        
        # 检查模型选项
        if "硅基流动 (siliconflow)" in SHALLOW_AGENT_OPTIONS:
            print("✅ CLI快速模型选项包含硅基流动")
        else:
            print("❌ CLI快速模型选项缺少硅基流动")
            return False
        
        if "硅基流动 (siliconflow)" in DEEP_AGENT_OPTIONS:
            print("✅ CLI深度模型选项包含硅基流动")
        else:
            print("❌ CLI深度模型选项缺少硅基流动")
            return False
        
        return True
    except Exception as e:
        print(f"❌ 检查CLI选项失败: {e}")
        return False


def check_documentation():
    """检查文档更新"""
    print("\n📚 检查文档更新...")
    
    try:
        readme_path = project_root / "README.md"
        if readme_path.exists():
            content = readme_path.read_text(encoding='utf-8')
            if "SILICONFLOW_API_KEY" in content:
                print("✅ README文档已更新")
            else:
                print("❌ README文档未更新")
                return False
        
        config_doc = project_root / "docs" / "configuration" / "siliconflow-config.md"
        if config_doc.exists():
            print("✅ 硅基流动配置文档存在")
        else:
            print("❌ 硅基流动配置文档缺失")
            return False
        
        return True
    except Exception as e:
        print(f"❌ 检查文档失败: {e}")
        return False


def run_integration_test():
    """运行集成测试"""
    print("\n🧪 运行集成测试...")
    
    try:
        # 检查API密钥
        if not os.getenv('SILICONFLOW_API_KEY'):
            print("⚠️ 跳过集成测试（无API密钥）")
            return True
        
        # 运行实际连接测试
        from tradingagents.llm_adapters.siliconflow_adapter import test_siliconflow_connection
        
        if test_siliconflow_connection():
            print("✅ 硅基流动连接测试成功")
            return True
        else:
            print("❌ 硅基流动连接测试失败")
            return False
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        return False


def main():
    """主验证函数"""
    print("🔍 硅基流动迁移验证")
    print("=" * 60)
    
    tests = [
        ("默认配置检查", check_default_config),
        ("API密钥检查", check_api_key),
        ("适配器导入检查", check_adapter_import),
        ("模型创建测试", test_model_creation),
        ("交易图初始化测试", test_trading_graph_init),
        ("CLI选项检查", check_cli_options),
        ("文档更新检查", check_documentation),
        ("集成测试", run_integration_test),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} 出现异常: {e}")
            results[test_name] = False
    
    # 总结结果
    print("\n📊 验证结果总结")
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
        print("\n🎉 硅基流动迁移验证成功！")
        print("💡 建议运行完整测试: python examples/siliconflow_examples/simple_test.py")
        return True
    else:
        print("\n⚠️ 部分验证失败，请检查配置")
        print("🔧 可能需要手动调整配置或重新运行迁移脚本")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
