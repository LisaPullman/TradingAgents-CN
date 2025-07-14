#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试600990股票名称映射问题
找出为什么600990会被错误地显示为"四维图新"而不是"四创电子"
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_china_news_enhanced_mapping():
    """测试china_news_enhanced模块的映射"""
    print("🔍 测试china_news_enhanced模块...")
    
    try:
        from tradingagents.dataflows.china_news_enhanced import ChinaStockNewsAggregator
        
        aggregator = ChinaStockNewsAggregator()
        name = aggregator.get_stock_name('600990')
        
        print(f"  china_news_enhanced: 600990 -> {name}")
        
        if name == "四创电子":
            print("  ✅ china_news_enhanced映射正确")
            return True
        else:
            print(f"  ❌ china_news_enhanced映射错误，期望'四创电子'，实际'{name}'")
            return False
            
    except Exception as e:
        print(f"  ❌ china_news_enhanced测试失败: {e}")
        return False


def test_tdx_utils_mapping():
    """测试tdx_utils模块的映射"""
    print("\n🔍 测试tdx_utils模块...")
    
    try:
        from tradingagents.dataflows.tdx_utils import TongDaXinDataProvider
        
        provider = TongDaXinDataProvider()
        name = provider._get_stock_name('600990')
        
        print(f"  tdx_utils: 600990 -> {name}")
        
        if name == "四创电子":
            print("  ✅ tdx_utils映射正确")
            return True
        elif name == "股票600990":
            print("  ⚠️ tdx_utils使用默认格式（未找到映射）")
            return True  # 这是可以接受的
        else:
            print(f"  ❌ tdx_utils映射错误，期望'四创电子'或'股票600990'，实际'{name}'")
            return False
            
    except Exception as e:
        print(f"  ❌ tdx_utils测试失败: {e}")
        return False


def test_common_stock_names():
    """测试_common_stock_names字典"""
    print("\n🔍 测试_common_stock_names字典...")
    
    try:
        from tradingagents.dataflows.tdx_utils import _common_stock_names
        
        if '600990' in _common_stock_names:
            name = _common_stock_names['600990']
            print(f"  _common_stock_names: 600990 -> {name}")
            
            if name == "四创电子":
                print("  ✅ _common_stock_names映射正确")
                return True
            else:
                print(f"  ❌ _common_stock_names映射错误，期望'四创电子'，实际'{name}'")
                return False
        else:
            print("  ⚠️ 600990不在_common_stock_names字典中")
            return True  # 这是可以接受的
            
    except Exception as e:
        print(f"  ❌ _common_stock_names测试失败: {e}")
        return False


def test_agent_utils_integration():
    """测试agent_utils集成"""
    print("\n🔍 测试agent_utils集成...")
    
    try:
        from tradingagents.agents.utils.agent_utils import AgentUtils
        from tradingagents.default_config import DEFAULT_CONFIG
        
        toolkit = AgentUtils(config=DEFAULT_CONFIG)
        
        # 测试中国股票新闻增强工具
        result = toolkit.get_china_stock_news_enhanced("600990", "2024-12-20")
        content = result.content if hasattr(result, 'content') else result
        
        print(f"  agent_utils新闻工具结果长度: {len(content)}")
        
        if "四创电子" in content:
            print("  ✅ agent_utils使用正确的股票名称")
            return True
        elif "四维图新" in content:
            print("  ❌ agent_utils使用错误的股票名称'四维图新'")
            print(f"  📋 内容预览: {content[:200]}...")
            return False
        else:
            print("  ⚠️ agent_utils结果中未找到股票名称")
            print(f"  📋 内容预览: {content[:200]}...")
            return True  # 可能是数据缺失，不算错误
            
    except Exception as e:
        print(f"  ❌ agent_utils测试失败: {e}")
        return False


def test_web_interface():
    """测试Web界面可能的映射"""
    print("\n🔍 测试Web界面映射...")
    
    try:
        # 检查Web界面是否有独立的股票映射
        web_files = [
            "web/utils/analysis_runner.py",
            "web/utils/stock_utils.py",
            "web/static/js/stock_search.js"
        ]
        
        found_mapping = False
        
        for file_path in web_files:
            full_path = project_root / file_path
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding='utf-8')
                    if "600990" in content:
                        print(f"  📁 在{file_path}中找到600990")
                        
                        # 查找相关行
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if "600990" in line:
                                print(f"    第{i+1}行: {line.strip()}")
                                found_mapping = True
                                
                                if "四维图新" in line:
                                    print(f"  ❌ 在{file_path}中发现错误映射!")
                                    return False
                except Exception as e:
                    print(f"  ⚠️ 读取{file_path}失败: {e}")
        
        if not found_mapping:
            print("  ✅ Web界面文件中未找到600990映射")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Web界面测试失败: {e}")
        return False


def test_database_cache():
    """测试数据库缓存中的映射"""
    print("\n🔍 测试数据库缓存...")
    
    try:
        # 检查是否有MongoDB缓存
        from tradingagents.dataflows.tdx_utils import _get_stock_name_from_mongodb
        
        mongodb_name = _get_stock_name_from_mongodb('600990')
        
        if mongodb_name:
            print(f"  MongoDB缓存: 600990 -> {mongodb_name}")
            
            if mongodb_name == "四创电子":
                print("  ✅ MongoDB缓存映射正确")
                return True
            else:
                print(f"  ❌ MongoDB缓存映射错误，期望'四创电子'，实际'{mongodb_name}'")
                return False
        else:
            print("  ⚠️ MongoDB中未找到600990映射")
            return True
            
    except Exception as e:
        print(f"  ❌ 数据库缓存测试失败: {e}")
        return False


def search_all_files_for_mapping():
    """搜索所有文件中的600990映射"""
    print("\n🔍 搜索所有文件中的600990映射...")
    
    try:
        # 搜索关键目录
        search_dirs = [
            "tradingagents",
            "web", 
            "cli",
            "scripts",
            "tests"
        ]
        
        found_files = []
        
        for dir_name in search_dirs:
            dir_path = project_root / dir_name
            if dir_path.exists():
                for py_file in dir_path.rglob("*.py"):
                    try:
                        content = py_file.read_text(encoding='utf-8')
                        if "600990" in content and "四维图新" in content:
                            found_files.append(py_file)
                            print(f"  ❌ 发现错误映射: {py_file.relative_to(project_root)}")
                            
                            # 显示相关行
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if "600990" in line and "四维图新" in line:
                                    print(f"    第{i+1}行: {line.strip()}")
                    except Exception:
                        continue
        
        if found_files:
            print(f"  ❌ 在{len(found_files)}个文件中发现错误映射")
            return False
        else:
            print("  ✅ 未在文件中发现600990->四维图新的错误映射")
            return True
            
    except Exception as e:
        print(f"  ❌ 文件搜索失败: {e}")
        return False


def main():
    """主调试函数"""
    print("🔍 600990股票名称映射调试")
    print("=" * 60)
    print("目标: 找出为什么600990会被错误显示为'四维图新'")
    print("正确: 600990 = 四创电子")
    print("=" * 60)
    
    tests = [
        ("china_news_enhanced映射", test_china_news_enhanced_mapping),
        ("tdx_utils映射", test_tdx_utils_mapping),
        ("_common_stock_names字典", test_common_stock_names),
        ("agent_utils集成", test_agent_utils_integration),
        ("Web界面映射", test_web_interface),
        ("数据库缓存", test_database_cache),
        ("全文件搜索", search_all_files_for_mapping),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} 出现异常: {e}")
            results[test_name] = False
    
    # 总结结果
    print("\n📊 调试结果总结")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    error_sources = []
    
    for test_name, success in results.items():
        status = "✅ 正确" if success else "❌ 错误"
        print(f"  {test_name}: {status}")
        if success:
            passed += 1
        else:
            error_sources.append(test_name)
    
    print(f"\n🎯 总体结果: {passed}/{total} 测试通过")
    
    if error_sources:
        print(f"\n❌ 发现错误来源: {', '.join(error_sources)}")
        print("💡 建议检查这些模块中的股票名称映射")
    else:
        print("\n✅ 未发现明显的错误映射")
        print("💡 错误可能来自:")
        print("  - 外部API返回的数据")
        print("  - 运行时动态生成的映射")
        print("  - 缓存中的过期数据")
    
    return len(error_sources) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
