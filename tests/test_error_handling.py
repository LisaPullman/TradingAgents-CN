#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误处理系统测试
测试统一异常处理、重试机制、断路器等功能
"""

import time
import logging
from unittest.mock import patch, MagicMock

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.core.exceptions import (
    TradingAgentsException, APIException, DataSourceException,
    LLMException, AnalysisException, ConfigurationException,
    NetworkException, DatabaseException, ValidationException,
    ErrorCategory, ErrorSeverity, convert_exception
)
from tradingagents.core.error_messages import (
    get_user_friendly_message, get_solution_suggestions, format_error_for_user
)
from tradingagents.core.decorators import (
    handle_exceptions, retry_with_backoff, circuit_breaker,
    resilient_call, RetryConfig, CircuitBreaker,
    validate_inputs, is_valid_stock_code, is_valid_date, is_positive_number
)


class TestTradingAgentsExceptions:
    """测试自定义异常类"""
    
    def test_base_exception(self):
        """测试基础异常类"""
        exc = TradingAgentsException(
            message="Test error",
            error_code="TEST_001",
            category=ErrorCategory.API,
            severity=ErrorSeverity.HIGH,
            details={"key": "value"},
            suggestions=["suggestion1", "suggestion2"]
        )
        
        assert exc.message == "Test error"
        assert exc.error_code == "TEST_001"
        assert exc.category == ErrorCategory.API
        assert exc.severity == ErrorSeverity.HIGH
        assert exc.details == {"key": "value"}
        assert exc.suggestions == ["suggestion1", "suggestion2"]
        assert exc.timestamp > 0
        
        # 测试转换为字典
        exc_dict = exc.to_dict()
        assert exc_dict["error_code"] == "TEST_001"
        assert exc_dict["message"] == "Test error"
        assert exc_dict["category"] == "api"
        assert exc_dict["severity"] == "high"
    
    def test_api_exception(self):
        """测试API异常"""
        exc = APIException(
            message="API call failed",
            api_name="test_api",
            status_code=401
        )
        
        assert exc.api_name == "test_api"
        assert exc.status_code == 401
        assert exc.category == ErrorCategory.API
        assert "检查API密钥是否正确配置" in exc.suggestions
    
    def test_data_source_exception(self):
        """测试数据源异常"""
        exc = DataSourceException(
            message="Data source failed",
            source_name="tushare"
        )
        
        assert exc.source_name == "tushare"
        assert exc.category == ErrorCategory.DATA_SOURCE
        assert "检查网络连接是否正常" in exc.suggestions
    
    def test_llm_exception(self):
        """测试LLM异常"""
        exc = LLMException(
            message="LLM call failed",
            model_name="gpt-4"
        )
        
        assert exc.model_name == "gpt-4"
        assert exc.category == ErrorCategory.LLM
        assert exc.severity == ErrorSeverity.HIGH
    
    def test_convert_exception(self):
        """测试异常转换"""
        # 测试标准异常转换
        original_exc = ValueError("Invalid value")
        converted = convert_exception(original_exc, "test_context")
        
        assert isinstance(converted, ValidationException)
        assert "test_context: Invalid value" in converted.message
        assert converted.original_exception == original_exc
        
        # 测试已经是TradingAgents异常的情况
        trading_exc = APIException("API error")
        converted = convert_exception(trading_exc)
        assert converted == trading_exc


class TestErrorMessages:
    """测试错误信息本地化"""
    
    def test_get_user_friendly_message(self):
        """测试获取用户友好错误信息"""
        # 测试已知错误代码
        msg_zh = get_user_friendly_message("API_KEY_MISSING", ErrorCategory.API, "zh")
        msg_en = get_user_friendly_message("API_KEY_MISSING", ErrorCategory.API, "en")
        
        assert "API密钥未配置" in msg_zh
        assert "API key not configured" in msg_en
        
        # 测试未知错误代码
        msg = get_user_friendly_message("UNKNOWN_ERROR", ErrorCategory.API, "zh")
        assert "API调用出现问题" in msg
    
    def test_get_solution_suggestions(self):
        """测试获取解决方案建议"""
        suggestions_zh = get_solution_suggestions(ErrorCategory.API, "zh")
        suggestions_en = get_solution_suggestions(ErrorCategory.API, "en")
        
        assert len(suggestions_zh) > 0
        assert len(suggestions_en) > 0
        assert "检查API密钥" in suggestions_zh[0]
        assert "Check if API key" in suggestions_en[0]
    
    def test_format_error_for_user(self):
        """测试格式化用户错误信息"""
        exc = APIException("API failed", api_name="test", status_code=401)
        formatted = format_error_for_user(exc, "zh")
        
        assert "error_code" in formatted
        assert "message" in formatted
        assert "suggestions" in formatted
        assert formatted["category"] == "api"
        assert formatted["severity"] == "high"


class TestDecorators:
    """测试装饰器功能"""
    
    def test_handle_exceptions_decorator(self):
        """测试异常处理装饰器"""
        
        @handle_exceptions(fallback_value="fallback", log_error=False)
        def failing_function():
            raise ValueError("Test error")
        
        result = failing_function()
        assert result == "fallback"
        
        @handle_exceptions(reraise=True)
        def failing_function_reraise():
            raise ValueError("Test error")

        try:
            failing_function_reraise()
            assert False, "Should have raised TradingAgentsException"
        except TradingAgentsException:
            pass
    
    def test_retry_decorator(self):
        """测试重试装饰器"""
        call_count = 0
        
        @retry_with_backoff(RetryConfig(max_attempts=3, base_delay=0.01))
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Network error")
            return "success"
        
        result = flaky_function()
        assert result == "success"
        assert call_count == 3
    
    def test_circuit_breaker(self):
        """测试断路器"""
        breaker = CircuitBreaker(failure_threshold=2, timeout=0.1)
        
        def failing_function():
            raise APIException("API error")
        
        # 触发失败
        try:
            breaker.call(failing_function)
            assert False, "Should have raised APIException"
        except APIException:
            pass

        try:
            breaker.call(failing_function)
            assert False, "Should have raised APIException"
        except APIException:
            pass

        # 断路器应该打开
        assert breaker.state.value == "open"

        # 第三次调用应该被断路器阻止
        try:
            breaker.call(failing_function)
            assert False, "Should have raised APIException"
        except APIException as e:
            assert "Circuit breaker is OPEN" in str(e)
    
    def test_validate_inputs_decorator(self):
        """测试输入验证装饰器"""
        
        @validate_inputs(
            stock_code=is_valid_stock_code,
            date=is_valid_date,
            amount=is_positive_number
        )
        def test_function(stock_code, date, amount):
            return f"{stock_code}-{date}-{amount}"
        
        # 正常调用
        result = test_function("AAPL", "2024-01-01", 100)
        assert result == "AAPL-2024-01-01-100"
        
        # 无效股票代码
        try:
            test_function("", "2024-01-01", 100)
            assert False, "Should have raised ValidationException"
        except ValidationException:
            pass

        # 无效日期
        try:
            test_function("AAPL", "invalid-date", 100)
            assert False, "Should have raised ValidationException"
        except ValidationException:
            pass

        # 无效金额
        try:
            test_function("AAPL", "2024-01-01", -100)
            assert False, "Should have raised ValidationException"
        except ValidationException:
            pass


class TestValidators:
    """测试验证器函数"""
    
    def test_is_valid_stock_code(self):
        """测试股票代码验证"""
        assert is_valid_stock_code("AAPL") == True
        assert is_valid_stock_code("600519") == True
        assert is_valid_stock_code("BRK.A") == True
        assert is_valid_stock_code("") == False
        assert is_valid_stock_code("AB") == False  # 太短
        assert is_valid_stock_code(123) == False  # 不是字符串
    
    def test_is_valid_date(self):
        """测试日期验证"""
        assert is_valid_date("2024-01-01") == True
        assert is_valid_date("2024-12-31") == True
        assert is_valid_date("invalid-date") == False
        assert is_valid_date("2024/01/01") == False  # 错误格式
        assert is_valid_date(20240101) == False  # 不是字符串
    
    def test_is_positive_number(self):
        """测试正数验证"""
        assert is_positive_number(100) == True
        assert is_positive_number(0.1) == True
        assert is_positive_number("100") == True
        assert is_positive_number(0) == False
        assert is_positive_number(-100) == False
        assert is_positive_number("invalid") == False


class TestIntegration:
    """集成测试"""
    
    def test_resilient_call_decorator(self):
        """测试综合弹性调用装饰器"""
        call_count = 0
        
        @resilient_call(
            retry_config=RetryConfig(max_attempts=2, base_delay=0.01),
            circuit_breaker_config={"failure_threshold": 3, "timeout": 0.1},
            fallback_value="fallback_result"
        )
        def test_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("Network error")
            return "success"
        
        result = test_function()
        assert result == "success"
        assert call_count == 2
    
    def test_error_handling_workflow(self):
        """测试完整的错误处理工作流"""
        
        # 模拟一个复杂的函数调用链
        @handle_exceptions(fallback_value=None, context="data_fetch")
        def fetch_data(source: str):
            if source == "fail":
                raise ConnectionError("Connection failed")
            return {"data": "success"}
        
        @retry_with_backoff(RetryConfig(max_attempts=2, base_delay=0.01))
        def process_data(data):
            if data is None:
                raise DataSourceException("No data available", source_name="test")
            return f"processed_{data['data']}"
        
        # 测试成功路径
        data = fetch_data("success")
        result = process_data(data)
        assert result == "processed_success"
        
        # 测试失败路径
        data = fetch_data("fail")  # 返回None（fallback值）
        try:
            process_data(data)
            assert False, "Should have raised DataSourceException"
        except DataSourceException:
            pass


def run_error_handling_tests():
    """运行错误处理测试"""
    print("🧪 运行错误处理系统测试...")
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 运行测试
    test_classes = [
        TestTradingAgentsExceptions,
        TestErrorMessages,
        TestDecorators,
        TestValidators,
        TestIntegration
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n📋 测试类: {test_class.__name__}")
        instance = test_class()
        
        # 获取所有测试方法
        test_methods = [method for method in dir(instance) if method.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(instance, method_name)
                method()
                print(f"  ✅ {method_name}")
                passed_tests += 1
            except Exception as e:
                print(f"  ❌ {method_name}: {e}")
    
    print(f"\n📊 测试结果: {passed_tests}/{total_tests} 通过")
    return passed_tests == total_tests


def run_tests():
    """运行测试的标准接口"""
    return run_error_handling_tests()


if __name__ == "__main__":
    success = run_error_handling_tests()
    exit(0 if success else 1)
