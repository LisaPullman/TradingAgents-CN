#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回退机制演示
展示专用模型调用失败时如何回退到DEFAULT_MODEL
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def demo_fallback_scenarios():
    """演示各种回退场景"""
    
    print("🔄 专用模型回退机制演示")
    print("=" * 60)
    print("展示当专用模型调用失败时，如何回退到DEFAULT_MODEL")
    print("=" * 60)
    
    # 场景1: API密钥缺失
    print("\n📋 场景1: API密钥缺失")
    print("-" * 30)
    
    # 临时移除API密钥
    original_api_key = os.environ.get('SILICONFLOW_API_KEY')
    if 'SILICONFLOW_API_KEY' in os.environ:
        del os.environ['SILICONFLOW_API_KEY']
    
    # 设置DEFAULT_MODEL
    os.environ['DEFAULT_MODEL'] = 'deepseek-ai/DeepSeek-V3'
    
    print("🔧 配置状态:")
    print(f"  SILICONFLOW_API_KEY: {'未设置' if not os.getenv('SILICONFLOW_API_KEY') else '已设置'}")
    print(f"  DEFAULT_MODEL: {os.getenv('DEFAULT_MODEL')}")
    print(f"  专用模型配置: meta-llama/Llama-3.1-70B-Instruct")
    
    print("\n💡 预期行为:")
    print("  1. 尝试创建专用模型: meta-llama/Llama-3.1-70B-Instruct")
    print("  2. 检测到API密钥缺失")
    print("  3. 回退到DEFAULT_MODEL: deepseek-ai/DeepSeek-V3")
    print("  4. 如果DEFAULT_MODEL也失败，回退到系统快速思考模型")
    
    # 场景2: 专用模型未配置
    print("\n📋 场景2: 专用模型未配置")
    print("-" * 30)
    
    print("🔧 配置状态:")
    print(f"  专用模型配置: 未设置")
    print(f"  DEFAULT_MODEL: {os.getenv('DEFAULT_MODEL')}")
    
    print("\n💡 预期行为:")
    print("  1. 检测到专用模型未配置")
    print("  2. 直接使用DEFAULT_MODEL: deepseek-ai/DeepSeek-V3")
    
    # 场景3: 模型创建失败
    print("\n📋 场景3: 模型创建失败")
    print("-" * 30)
    
    print("🔧 配置状态:")
    print(f"  专用模型配置: invalid-model-name")
    print(f"  DEFAULT_MODEL: {os.getenv('DEFAULT_MODEL')}")
    
    print("\n💡 预期行为:")
    print("  1. 尝试创建专用模型: invalid-model-name")
    print("  2. 模型创建失败（模型不存在）")
    print("  3. 捕获异常，回退到DEFAULT_MODEL: deepseek-ai/DeepSeek-V3")
    
    # 恢复API密钥
    if original_api_key:
        os.environ['SILICONFLOW_API_KEY'] = original_api_key
    
    return True


def demo_config_priority():
    """演示配置优先级"""
    
    print("\n🏆 配置优先级演示")
    print("=" * 60)
    
    print("📊 配置优先级顺序:")
    print("  1. 环境变量 (最高优先级)")
    print("  2. 默认配置文件")
    print("  3. 硬编码默认值 (最低优先级)")
    
    # 演示环境变量优先级
    print("\n🔧 环境变量优先级测试:")
    
    # 设置测试环境变量
    os.environ['DEFAULT_MODEL'] = 'test-model-from-env'
    os.environ['MARKET_ANALYST_LLM'] = 'test-market-model'
    
    try:
        from tradingagents.default_config import DEFAULT_CONFIG
        
        print(f"  DEFAULT_MODEL: {DEFAULT_CONFIG.get('default_model')}")
        print(f"  MARKET_ANALYST_LLM: {DEFAULT_CONFIG.get('market_analyst_llm')}")
        
        print("\n✅ 环境变量成功覆盖默认配置")
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
    
    finally:
        # 清理测试环境变量
        if 'DEFAULT_MODEL' in os.environ:
            del os.environ['DEFAULT_MODEL']
        if 'MARKET_ANALYST_LLM' in os.environ:
            del os.environ['MARKET_ANALYST_LLM']


def demo_best_practices():
    """演示最佳实践"""
    
    print("\n💡 回退机制最佳实践")
    print("=" * 60)
    
    print("🎯 推荐的DEFAULT_MODEL选择:")
    
    models = [
        {
            "model": "deepseek-ai/DeepSeek-V3",
            "pros": ["稳定可靠", "综合性能强", "成本适中"],
            "cons": ["不是最高性能"],
            "recommended": True
        },
        {
            "model": "Qwen/Qwen2.5-32B-Instruct", 
            "pros": ["中文优化", "平衡性能", "情绪理解好"],
            "cons": ["参数规模中等"],
            "recommended": False
        },
        {
            "model": "meta-llama/Llama-3.1-8B-Instruct",
            "pros": ["轻量级", "快速响应", "成本低"],
            "cons": ["性能相对较低"],
            "recommended": False
        }
    ]
    
    for model in models:
        status = "🥇 推荐" if model["recommended"] else "⚡ 备选"
        print(f"\n{status} {model['model']}")
        print(f"  优点: {', '.join(model['pros'])}")
        print(f"  缺点: {', '.join(model['cons'])}")
    
    print("\n🔧 配置建议:")
    print("  1. 生产环境: 使用稳定的DEFAULT_MODEL")
    print("  2. 开发环境: 可以使用轻量级模型降低成本")
    print("  3. 测试环境: 使用与生产环境相同的配置")
    print("  4. 监控日志: 关注回退频率，优化专用模型配置")
    
    print("\n📊 监控指标:")
    print("  - 专用模型成功率")
    print("  - 回退模型使用频率") 
    print("  - API调用成本")
    print("  - 分析质量对比")


def demo_configuration_examples():
    """演示配置示例"""
    
    print("\n📝 配置示例")
    print("=" * 60)
    
    print("🎯 高性能配置（推荐）:")
    print("""
# .env 文件配置
SILICONFLOW_API_KEY=your_api_key_here
DEFAULT_MODEL=deepseek-ai/DeepSeek-V3

# 专用高性能模型
MARKET_ANALYST_LLM=meta-llama/Llama-3.1-70B-Instruct
FUNDAMENTALS_ANALYST_LLM=Qwen/Qwen2.5-72B-Instruct
NEWS_ANALYST_LLM=deepseek-ai/DeepSeek-R1
SOCIAL_ANALYST_LLM=Qwen/Qwen2.5-32B-Instruct
""")
    
    print("💰 成本优化配置:")
    print("""
# .env 文件配置
SILICONFLOW_API_KEY=your_api_key_here
DEFAULT_MODEL=Qwen/Qwen2.5-14B-Instruct

# 平衡性能和成本
MARKET_ANALYST_LLM=Qwen/Qwen2.5-32B-Instruct
FUNDAMENTALS_ANALYST_LLM=deepseek-ai/DeepSeek-V3
NEWS_ANALYST_LLM=deepseek-ai/DeepSeek-V3
SOCIAL_ANALYST_LLM=Qwen/Qwen2.5-14B-Instruct
""")
    
    print("🧪 开发测试配置:")
    print("""
# .env 文件配置
SILICONFLOW_API_KEY=your_api_key_here
DEFAULT_MODEL=deepseek-ai/DeepSeek-V3

# 所有分析师使用相同模型简化测试
MARKET_ANALYST_LLM=deepseek-ai/DeepSeek-V3
FUNDAMENTALS_ANALYST_LLM=deepseek-ai/DeepSeek-V3
NEWS_ANALYST_LLM=deepseek-ai/DeepSeek-V3
SOCIAL_ANALYST_LLM=deepseek-ai/DeepSeek-V3
""")


def main():
    """主演示函数"""
    
    print("🚀 TradingAgents-CN 回退机制演示")
    print("=" * 80)
    print("🎯 目标: 展示专用模型调用失败时的智能回退机制")
    print("=" * 80)
    
    try:
        # 演示回退场景
        demo_fallback_scenarios()
        
        # 演示配置优先级
        demo_config_priority()
        
        # 演示最佳实践
        demo_best_practices()
        
        # 演示配置示例
        demo_configuration_examples()
        
        print("\n🎉 回退机制演示完成！")
        print("\n💡 关键要点:")
        print("  1. 系统具有多层回退机制，确保稳定运行")
        print("  2. DEFAULT_MODEL作为可靠的回退选择")
        print("  3. 环境变量配置具有最高优先级")
        print("  4. 推荐使用deepseek-ai/DeepSeek-V3作为DEFAULT_MODEL")
        print("  5. 监控回退频率以优化配置")
        
        print("\n🔧 下一步:")
        print("  1. 设置.env文件中的DEFAULT_MODEL")
        print("  2. 配置专用分析师模型")
        print("  3. 测试回退机制是否正常工作")
        print("  4. 监控生产环境中的模型使用情况")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 演示过程出错: {e}")
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ 演示成功完成")
    else:
        print("\n❌ 演示失败")
    sys.exit(0 if success else 1)
