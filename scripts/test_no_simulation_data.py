#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试验证：确保不再出现模拟数据
验证所有硬编码的模拟数据已被移除
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_china_news_no_simulation():
    """测试中国新闻模块不再生成模拟数据"""
    print("🧪 测试中国新闻模块...")
    
    try:
        from tradingagents.dataflows.china_news_enhanced import get_china_stock_news_enhanced
        
        # 测试有效日期（应该不包含模拟数据）
        result = get_china_stock_news_enhanced("600990", "2024-12-20")
        
        # 检查是否包含模拟数据的关键词
        simulation_keywords = [
            "模拟案例",
            "演示分析", 
            "模拟数据",
            "演示数据",
            "假设",
            "模拟实现",
            "业绩稳健增长，市场前景看好",  # 之前的硬编码内容
            "获机构调研关注，投资价值凸显",  # 之前的硬编码内容
            "技术创新驱动发展",  # 之前的硬编码内容
        ]
        
        found_simulation = []
        for keyword in simulation_keywords:
            if keyword in result:
                found_simulation.append(keyword)
        
        if found_simulation:
            print(f"  ❌ 仍包含模拟数据关键词: {found_simulation}")
            print(f"  📋 结果预览: {result[:300]}...")
            return False
        else:
            print("  ✅ 未发现模拟数据关键词")
            
            # 检查是否正确处理数据缺失
            if "真实新闻数据暂时不可用" in result or "数据获取限制" in result:
                print("  ✅ 正确处理数据缺失情况")
                return True
            elif "新闻事件分析" in result and len(result) > 500:
                print("  ✅ 获取到真实新闻数据")
                return True
            else:
                print("  ⚠️ 结果格式异常")
                print(f"  📋 结果预览: {result[:200]}...")
                return False
                
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False


def test_news_analyst_prompts():
    """测试新闻分析师提示词"""
    print("\n📰 测试新闻分析师提示词...")
    
    try:
        from tradingagents.agents.analysts.news_analyst import create_news_analyst
        
        # 检查源代码中的提示词
        news_file = project_root / "tradingagents" / "agents" / "analysts" / "news_analyst.py"
        content = news_file.read_text(encoding='utf-8')
        
        # 检查是否包含禁止模拟的指令
        required_phrases = [
            "严格禁止",
            "不允许编造",
            "不允许模拟",
            "必须基于工具获取的真实数据",
            "真实新闻数据暂时不可用"
        ]
        
        missing_phrases = []
        for phrase in required_phrases:
            if phrase not in content:
                missing_phrases.append(phrase)
        
        if missing_phrases:
            print(f"  ❌ 缺少必要的反模拟指令: {missing_phrases}")
            return False
        else:
            print("  ✅ 包含完整的反模拟指令")
            return True
            
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False


def test_social_analyst_prompts():
    """测试社交媒体分析师提示词"""
    print("\n😊 测试社交媒体分析师提示词...")
    
    try:
        # 检查源代码中的提示词
        social_file = project_root / "tradingagents" / "agents" / "analysts" / "social_media_analyst.py"
        content = social_file.read_text(encoding='utf-8')
        
        # 检查是否包含禁止模拟的指令
        required_phrases = [
            "严格禁止",
            "不允许编造",
            "不允许模拟",
            "必须基于工具获取的真实数据",
            "真实社交媒体数据暂时不可用"
        ]
        
        missing_phrases = []
        for phrase in required_phrases:
            if phrase not in content:
                missing_phrases.append(phrase)
        
        if missing_phrases:
            print(f"  ❌ 缺少必要的反模拟指令: {missing_phrases}")
            return False
        else:
            print("  ✅ 包含完整的反模拟指令")
            return True
            
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False


def test_web_demo_mode():
    """测试Web界面演示模式标识"""
    print("\n🌐 测试Web界面演示模式...")
    
    try:
        from web.utils.analysis_runner import generate_demo_results
        
        # 生成演示结果
        demo_result = generate_demo_results(
            "600990", "2024-12-20", ["news"], "deep", "siliconflow", "deepseek-v3", "测试错误"
        )
        
        # 检查是否明确标注为演示数据
        demo_indicators = [
            "演示数据",
            "模拟数据", 
            "需要配置API密钥",
            "这是演示",
            "实际分析需要"
        ]
        
        found_indicators = []
        demo_content = str(demo_result)
        for indicator in demo_indicators:
            if indicator in demo_content:
                found_indicators.append(indicator)
        
        if found_indicators:
            print(f"  ✅ Web演示模式正确标注: {found_indicators}")
            return True
        else:
            print("  ❌ Web演示模式缺少标注")
            print(f"  📋 内容预览: {demo_content[:200]}...")
            return False
            
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False


def test_code_search_for_simulation():
    """搜索代码中的模拟数据残留（排除禁止指令中的正当使用）"""
    print("\n🔍 搜索代码中的模拟数据残留...")

    try:
        # 要检查的关键文件
        key_files = [
            "tradingagents/dataflows/china_news_enhanced.py",
            "tradingagents/dataflows/siliconflow_news_utils.py"
        ]

        # 检查是否有实际的模拟数据生成（而非禁止指令）
        simulation_content_patterns = [
            r'news_items\s*=\s*\[.*模拟',  # 硬编码的模拟新闻列表
            r'return.*模拟案例',  # 返回模拟案例
            r'content.*业绩稳健增长',  # 之前的硬编码内容
            r'title.*获机构调研关注',  # 之前的硬编码内容
        ]

        found_issues = []

        for file_path in key_files:
            full_path = project_root / file_path
            if full_path.exists():
                content = full_path.read_text(encoding='utf-8')

                for pattern in simulation_content_patterns:
                    import re
                    matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                    if matches:
                        found_issues.append(f"{file_path}: {pattern} -> {matches}")

        if found_issues:
            print(f"  ❌ 发现模拟数据生成代码:")
            for issue in found_issues:
                print(f"    - {issue}")
            return False
        else:
            print("  ✅ 未发现模拟数据生成代码")

            # 检查是否正确包含了禁止指令
            analyst_files = [
                "tradingagents/agents/analysts/news_analyst.py",
                "tradingagents/agents/analysts/social_media_analyst.py"
            ]

            for file_path in analyst_files:
                full_path = project_root / file_path
                if full_path.exists():
                    content = full_path.read_text(encoding='utf-8')
                    if "严格禁止" not in content or "不允许" not in content:
                        print(f"  ⚠️ {file_path} 缺少禁止指令")
                        return False

            print("  ✅ 所有分析师都包含正确的禁止指令")
            return True

    except Exception as e:
        print(f"  ❌ 搜索失败: {e}")
        return False


def test_future_date_handling():
    """测试未来日期处理（确保不生成模拟数据）"""
    print("\n🔮 测试未来日期处理...")
    
    try:
        from tradingagents.dataflows.china_news_enhanced import get_china_stock_news_enhanced
        
        # 测试明确的未来日期
        result = get_china_stock_news_enhanced("600990", "2026-01-01")
        
        # 检查是否正确处理未来日期而不生成模拟数据
        if "日期验证警告" in result and "未来日期" in result:
            print("  ✅ 正确处理未来日期")
            
            # 确保不包含模拟新闻内容
            simulation_content = [
                "业绩稳健增长",
                "市场前景看好", 
                "机构调研关注",
                "技术创新驱动"
            ]
            
            found_simulation = [s for s in simulation_content if s in result]
            if found_simulation:
                print(f"  ❌ 未来日期处理中仍包含模拟内容: {found_simulation}")
                return False
            else:
                print("  ✅ 未来日期处理不包含模拟内容")
                return True
        else:
            print("  ❌ 未来日期处理异常")
            print(f"  📋 结果预览: {result[:200]}...")
            return False
            
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🧪 模拟数据移除验证测试")
    print("=" * 60)
    print("目标: 确保所有硬编码的模拟数据已被移除")
    print("=" * 60)
    
    tests = [
        ("中国新闻模块测试", test_china_news_no_simulation),
        ("新闻分析师提示词测试", test_news_analyst_prompts),
        ("社交媒体分析师提示词测试", test_social_analyst_prompts),
        ("Web演示模式测试", test_web_demo_mode),
        ("代码模拟数据搜索", test_code_search_for_simulation),
        ("未来日期处理测试", test_future_date_handling),
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
        print("\n🎉 模拟数据移除成功！")
        print("💡 现在系统将：")
        print("  - 只使用真实数据进行分析")
        print("  - 明确说明数据缺失情况")
        print("  - 不再生成任何模拟内容")
        print("  - 提供真实的数据获取建议")
    elif passed >= total * 0.8:
        print("\n✅ 模拟数据基本移除成功！")
        print("⚠️ 部分功能可能需要进一步优化")
    else:
        print("\n❌ 模拟数据移除不完整")
        print("🔧 需要进一步检查和修复")
    
    return passed >= total * 0.8


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
