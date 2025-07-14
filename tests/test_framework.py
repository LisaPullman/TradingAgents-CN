#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents-CN 测试框架
提供统一的测试工具、模拟对象和测试运行器
"""

import os
import sys
import time
import json
import tempfile
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass
from contextlib import contextmanager

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@dataclass
class TestResult:
    """测试结果"""
    name: str
    passed: bool
    duration: float
    error: Optional[str] = None
    traceback: Optional[str] = None


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.setup_functions: List[Callable] = []
        self.teardown_functions: List[Callable] = []
    
    def add_setup(self, func: Callable):
        """添加设置函数"""
        self.setup_functions.append(func)
    
    def add_teardown(self, func: Callable):
        """添加清理函数"""
        self.teardown_functions.append(func)
    
    def run_test(self, test_func: Callable, test_name: str = None) -> TestResult:
        """运行单个测试"""
        if test_name is None:
            test_name = test_func.__name__
        
        start_time = time.time()
        
        try:
            # 运行设置函数
            for setup_func in self.setup_functions:
                setup_func()
            
            # 运行测试
            test_func()
            
            duration = time.time() - start_time
            result = TestResult(
                name=test_name,
                passed=True,
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(
                name=test_name,
                passed=False,
                duration=duration,
                error=str(e),
                traceback=traceback.format_exc()
            )
        
        finally:
            # 运行清理函数
            for teardown_func in self.teardown_functions:
                try:
                    teardown_func()
                except Exception as e:
                    print(f"Teardown failed: {e}")
        
        self.results.append(result)
        return result
    
    def run_test_class(self, test_class) -> List[TestResult]:
        """运行测试类"""
        instance = test_class()
        test_methods = [method for method in dir(instance) if method.startswith('test_')]
        
        class_results = []
        for method_name in test_methods:
            method = getattr(instance, method_name)
            result = self.run_test(method, f"{test_class.__name__}.{method_name}")
            class_results.append(result)
        
        return class_results
    
    def get_summary(self) -> Dict[str, Any]:
        """获取测试总结"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        total_duration = sum(r.duration for r in self.results)
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "total_duration": total_duration,
            "results": self.results
        }
    
    def print_summary(self):
        """打印测试总结"""
        summary = self.get_summary()
        
        print(f"\n📊 测试总结")
        print("=" * 50)
        print(f"总计: {summary['total']}")
        print(f"通过: {summary['passed']}")
        print(f"失败: {summary['failed']}")
        print(f"通过率: {summary['pass_rate']:.1f}%")
        print(f"总耗时: {summary['total_duration']:.2f}s")
        
        if summary['failed'] > 0:
            print(f"\n❌ 失败的测试:")
            for result in self.results:
                if not result.passed:
                    print(f"  - {result.name}: {result.error}")


class MockFactory:
    """模拟对象工厂"""
    
    @staticmethod
    def create_mock_llm(responses: List[str] = None):
        """创建模拟LLM"""
        mock_llm = Mock()
        
        if responses:
            mock_llm.invoke.side_effect = responses
        else:
            mock_llm.invoke.return_value = "Mock LLM response"
        
        return mock_llm
    
    @staticmethod
    def create_mock_api_response(status_code: int = 200, data: Dict = None):
        """创建模拟API响应"""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = data or {"status": "success"}
        mock_response.text = json.dumps(data or {"status": "success"})
        return mock_response
    
    @staticmethod
    def create_mock_stock_data():
        """创建模拟股票数据"""
        return {
            "symbol": "AAPL",
            "price": 150.0,
            "change": 2.5,
            "change_percent": 1.67,
            "volume": 1000000,
            "market_cap": 2500000000000
        }
    
    @staticmethod
    def create_mock_news_data():
        """创建模拟新闻数据"""
        return [
            {
                "title": "Test News 1",
                "content": "This is test news content 1",
                "source": "Test Source",
                "timestamp": "2024-01-01T10:00:00Z",
                "sentiment": "positive"
            },
            {
                "title": "Test News 2", 
                "content": "This is test news content 2",
                "source": "Test Source",
                "timestamp": "2024-01-01T11:00:00Z",
                "sentiment": "neutral"
            }
        ]
    
    @staticmethod
    def create_mock_config():
        """创建模拟配置"""
        return {
            "llm_provider": "test",
            "deep_think_llm": "test-model",
            "quick_think_llm": "test-model",
            "api_keys": {
                "test_api": "test_key"
            }
        }


class TestEnvironment:
    """测试环境管理器"""
    
    def __init__(self):
        self.temp_dirs: List[str] = []
        self.env_vars: Dict[str, str] = {}
        self.original_env: Dict[str, str] = {}
    
    @contextmanager
    def temporary_directory(self):
        """创建临时目录"""
        temp_dir = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        try:
            yield temp_dir
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @contextmanager
    def environment_variables(self, **env_vars):
        """设置临时环境变量"""
        # 保存原始环境变量
        for key, value in env_vars.items():
            if key in os.environ:
                self.original_env[key] = os.environ[key]
            os.environ[key] = value
        
        try:
            yield
        finally:
            # 恢复原始环境变量
            for key in env_vars.keys():
                if key in self.original_env:
                    os.environ[key] = self.original_env[key]
                elif key in os.environ:
                    del os.environ[key]
            self.original_env.clear()
    
    @contextmanager
    def mock_imports(self, **mocks):
        """模拟导入"""
        with patch.dict('sys.modules', mocks):
            yield
    
    def cleanup(self):
        """清理测试环境"""
        # 清理临时目录
        import shutil
        for temp_dir in self.temp_dirs:
            shutil.rmtree(temp_dir, ignore_errors=True)
        self.temp_dirs.clear()
        
        # 恢复环境变量
        for key, value in self.original_env.items():
            os.environ[key] = value
        self.original_env.clear()


class AssertionHelper:
    """断言助手"""
    
    @staticmethod
    def assert_contains(container, item, message: str = None):
        """断言包含"""
        if item not in container:
            raise AssertionError(message or f"Expected {item} to be in {container}")
    
    @staticmethod
    def assert_not_contains(container, item, message: str = None):
        """断言不包含"""
        if item in container:
            raise AssertionError(message or f"Expected {item} not to be in {container}")
    
    @staticmethod
    def assert_length(container, expected_length: int, message: str = None):
        """断言长度"""
        actual_length = len(container)
        if actual_length != expected_length:
            raise AssertionError(
                message or f"Expected length {expected_length}, got {actual_length}"
            )
    
    @staticmethod
    def assert_type(obj, expected_type, message: str = None):
        """断言类型"""
        if not isinstance(obj, expected_type):
            raise AssertionError(
                message or f"Expected type {expected_type}, got {type(obj)}"
            )
    
    @staticmethod
    def assert_raises(exception_type, func, *args, **kwargs):
        """断言抛出异常"""
        try:
            func(*args, **kwargs)
            raise AssertionError(f"Expected {exception_type} to be raised")
        except exception_type:
            pass  # 期望的异常
        except Exception as e:
            raise AssertionError(f"Expected {exception_type}, got {type(e)}")
    
    @staticmethod
    def assert_dict_contains(dict_obj: dict, expected_keys: List[str], message: str = None):
        """断言字典包含指定键"""
        missing_keys = [key for key in expected_keys if key not in dict_obj]
        if missing_keys:
            raise AssertionError(
                message or f"Dictionary missing keys: {missing_keys}"
            )
    
    @staticmethod
    def assert_json_valid(json_str: str, message: str = None):
        """断言JSON有效"""
        try:
            json.loads(json_str)
        except json.JSONDecodeError as e:
            raise AssertionError(message or f"Invalid JSON: {e}")


# 全局测试实例
test_runner = TestRunner()
mock_factory = MockFactory()
test_env = TestEnvironment()
assert_helper = AssertionHelper()


def run_all_tests():
    """运行所有测试"""
    print("🧪 运行TradingAgents-CN完整测试套件...")
    
    # 测试文件列表
    test_files = [
        "test_error_handling.py",
        "test_monitoring_logging.py",
        "test_core_functionality.py",
        "test_security.py",
        "test_performance.py"
    ]
    
    total_passed = 0
    total_failed = 0
    
    for test_file in test_files:
        test_path = Path(__file__).parent / test_file
        if test_path.exists():
            print(f"\n📋 运行 {test_file}...")
            try:
                # 动态导入并运行测试
                import importlib.util
                spec = importlib.util.spec_from_file_location("test_module", test_path)
                test_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(test_module)
                
                # 查找并运行测试函数
                if hasattr(test_module, 'run_tests'):
                    success = test_module.run_tests()
                elif hasattr(test_module, 'main'):
                    success = test_module.main()
                else:
                    print(f"  ⚠️ 未找到测试运行函数")
                    continue
                
                if success:
                    total_passed += 1
                    print(f"  ✅ {test_file} 通过")
                else:
                    total_failed += 1
                    print(f"  ❌ {test_file} 失败")
                    
            except Exception as e:
                total_failed += 1
                print(f"  ❌ {test_file} 运行出错: {e}")
        else:
            print(f"  ⚠️ 测试文件不存在: {test_file}")
    
    print(f"\n📊 测试套件总结:")
    print(f"  通过: {total_passed}")
    print(f"  失败: {total_failed}")
    print(f"  总计: {total_passed + total_failed}")
    
    return total_failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
