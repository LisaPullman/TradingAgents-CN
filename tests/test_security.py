#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全性测试
测试API密钥管理、输入验证、访问控制等安全功能
"""

import os
import time
import tempfile
from pathlib import Path
from unittest.mock import patch

import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.core.security import (
    APIKeyManager, InputValidator, AccessController, SecurityAuditor,
    SecurityLevel, SecurityEvent,
    get_api_key_manager, get_input_validator, get_access_controller, get_security_auditor
)


class TestAPIKeyManager:
    """测试API密钥管理器"""
    
    def test_validate_api_key(self):
        """测试API密钥验证"""
        manager = APIKeyManager()
        
        # 测试有效的API密钥
        valid_keys = {
            "openai": "sk-" + "a" * 48,
            "siliconflow": "sk-abcdefghijklmnopqrstuvwxyz123456",
            "deepseek": "sk-" + "b" * 48,
            "dashscope": "sk-" + "c" * 32
        }
        
        for provider, key in valid_keys.items():
            assert manager.validate_api_key(key, provider) == True
        
        # 测试无效的API密钥
        invalid_keys = [
            ("openai", "invalid-key"),
            ("siliconflow", "sk-short"),
            ("deepseek", "no-prefix"),
            ("dashscope", "sk-" + "d" * 10)  # 太短
        ]
        
        for provider, key in invalid_keys:
            assert manager.validate_api_key(key, provider) == False
        
        print("✅ API密钥验证测试通过")
    
    def test_mask_api_key(self):
        """测试API密钥掩码"""
        manager = APIKeyManager()
        
        # 测试正常长度密钥
        key = "sk-abcdefghijklmnopqrstuvwxyz123456"
        masked = manager.mask_api_key(key)
        assert masked.startswith("sk-a")
        assert masked.endswith("3456")
        assert "*" in masked
        
        # 测试短密钥
        short_key = "short"
        masked_short = manager.mask_api_key(short_key)
        assert masked_short == "*" * len(short_key)
        
        # 测试空密钥
        assert manager.mask_api_key("") == "None"
        assert manager.mask_api_key(None) == "None"
        
        print("✅ API密钥掩码测试通过")
    
    def test_check_key_exposure(self):
        """测试密钥暴露检查"""
        manager = APIKeyManager()
        
        # 测试包含密钥的文本
        text_with_key = "My API key is sk-abcdefghijklmnopqrstuvwxyz123456789012345678"
        exposed = manager.check_key_exposure(text_with_key)
        assert len(exposed) > 0
        
        # 测试不包含密钥的文本
        safe_text = "This is a safe text without any API keys"
        exposed_safe = manager.check_key_exposure(safe_text)
        assert len(exposed_safe) == 0
        
        print("✅ 密钥暴露检查测试通过")
    
    def test_get_secure_env_var(self):
        """测试安全环境变量获取"""
        manager = APIKeyManager()
        
        # 测试存在的环境变量
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            value = manager.get_secure_env_var("TEST_VAR", required=False)
            assert value == "test_value"
        
        # 测试不存在的可选环境变量
        value = manager.get_secure_env_var("NON_EXISTENT_VAR", required=False)
        assert value is None
        
        # 测试不存在的必需环境变量
        try:
            manager.get_secure_env_var("REQUIRED_VAR", required=True)
            assert False, "Should have raised exception"
        except Exception:
            pass
        
        print("✅ 安全环境变量获取测试通过")


class TestInputValidator:
    """测试输入验证器"""
    
    def test_validate_stock_symbol(self):
        """测试股票代码验证"""
        validator = InputValidator()
        
        # 测试有效股票代码
        valid_symbols = ["AAPL", "GOOGL", "MSFT", "600519", "BRK.A"]
        for symbol in valid_symbols:
            assert validator.validate_stock_symbol(symbol) == True
        
        # 测试无效股票代码
        invalid_symbols = [
            "",  # 空字符串
            None,  # None值
            "TOOLONGSTOCKSYMBOL",  # 太长
            "AAPL<script>",  # 包含恶意字符
            "'; DROP TABLE stocks; --",  # SQL注入
            "javascript:alert(1)"  # JavaScript注入
        ]
        
        for symbol in invalid_symbols:
            assert validator.validate_stock_symbol(symbol) == False
        
        print("✅ 股票代码验证测试通过")
    
    def test_validate_date_string(self):
        """测试日期字符串验证"""
        validator = InputValidator()
        
        # 测试有效日期
        valid_dates = ["2024-01-01", "2024-12-31", "2023-02-28"]
        for date_str in valid_dates:
            assert validator.validate_date_string(date_str) == True
        
        # 测试无效日期
        invalid_dates = [
            "",  # 空字符串
            None,  # None值
            "2024/01/01",  # 错误格式
            "2024-13-01",  # 无效月份
            "2024-01-32",  # 无效日期
            "not-a-date"  # 非日期字符串
        ]
        
        for date_str in invalid_dates:
            assert validator.validate_date_string(date_str) == False
        
        print("✅ 日期字符串验证测试通过")
    
    def test_sanitize_user_input(self):
        """测试用户输入清理"""
        validator = InputValidator()
        
        # 测试正常输入
        clean_input = "This is a normal input"
        sanitized = validator.sanitize_user_input(clean_input)
        assert sanitized == clean_input
        
        # 测试包含危险字符的输入
        dangerous_input = "Hello <script>alert('xss')</script> world"
        sanitized = validator.sanitize_user_input(dangerous_input)
        assert "<script>" not in sanitized
        assert "alert" in sanitized  # 内容保留，只移除危险字符
        
        # 测试长度限制
        long_input = "a" * 2000
        sanitized = validator.sanitize_user_input(long_input, max_length=100)
        assert len(sanitized) == 100
        
        print("✅ 用户输入清理测试通过")
    
    def test_check_injection_patterns(self):
        """测试注入攻击模式检查"""
        validator = InputValidator()
        
        # 测试XSS攻击
        xss_text = "<script>alert('xss')</script>"
        patterns = validator.check_injection_patterns(xss_text)
        assert "XSS" in patterns
        
        # 测试SQL注入
        sql_text = "'; DROP TABLE users; --"
        patterns = validator.check_injection_patterns(sql_text)
        assert "SQL injection" in patterns
        
        # 测试安全文本
        safe_text = "This is a safe text"
        patterns = validator.check_injection_patterns(safe_text)
        assert len(patterns) == 0
        
        print("✅ 注入攻击模式检查测试通过")


class TestAccessController:
    """测试访问控制器"""
    
    def test_rate_limiting(self):
        """测试速率限制"""
        controller = AccessController()
        
        # 测试正常请求
        for i in range(5):
            assert controller.check_rate_limit("test_user", max_requests=10, window_seconds=60) == True
        
        # 测试超过限制
        for i in range(10):
            controller.check_rate_limit("test_user2", max_requests=5, window_seconds=60)
        
        # 第11次请求应该被拒绝
        assert controller.check_rate_limit("test_user2", max_requests=5, window_seconds=60) == False
        
        print("✅ 速率限制测试通过")
    
    def test_ip_blocking(self):
        """测试IP阻止"""
        controller = AccessController()
        
        test_ip = "192.168.1.100"
        
        # 初始状态不应该被阻止
        assert controller.is_ip_blocked(test_ip) == False
        
        # 阻止IP
        controller.block_ip(test_ip, "Suspicious activity")
        
        # 现在应该被阻止
        assert controller.is_ip_blocked(test_ip) == True
        
        print("✅ IP阻止测试通过")
    
    def test_file_access_validation(self):
        """测试文件访问验证"""
        controller = AccessController()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建测试文件
            allowed_dir = Path(temp_dir) / "allowed"
            allowed_dir.mkdir()
            test_file = allowed_dir / "test.txt"
            test_file.write_text("test content")
            
            # 测试允许的文件访问
            assert controller.validate_file_access(str(test_file), [str(allowed_dir)]) == True
            
            # 测试不允许的文件访问
            forbidden_file = Path(temp_dir) / "forbidden.txt"
            forbidden_file.write_text("forbidden content")
            assert controller.validate_file_access(str(forbidden_file), [str(allowed_dir)]) == False
            
            # 测试路径遍历攻击
            traversal_path = str(allowed_dir) + "/../forbidden.txt"
            assert controller.validate_file_access(traversal_path, [str(allowed_dir)]) == False
        
        print("✅ 文件访问验证测试通过")


class TestSecurityAuditor:
    """测试安全审计器"""
    
    def test_log_security_event(self):
        """测试安全事件记录"""
        auditor = SecurityAuditor()
        
        # 记录安全事件
        auditor.log_security_event(
            "test_event",
            SecurityLevel.HIGH,
            "Test security event",
            user_id="test_user",
            action="test_action"
        )
        
        # 检查事件是否被记录
        assert len(auditor.events) == 1
        event = auditor.events[0]
        assert event.event_type == "test_event"
        assert event.severity == SecurityLevel.HIGH
        assert event.message == "Test security event"
        
        print("✅ 安全事件记录测试通过")
    
    def test_security_summary(self):
        """测试安全事件摘要"""
        auditor = SecurityAuditor()
        
        # 记录多个事件
        auditor.log_security_event("login_attempt", SecurityLevel.LOW, "User login")
        auditor.log_security_event("failed_login", SecurityLevel.MEDIUM, "Failed login")
        auditor.log_security_event("injection_attack", SecurityLevel.CRITICAL, "SQL injection detected")
        
        # 获取摘要
        summary = auditor.get_security_summary(hours=24)
        
        assert summary["total_events"] == 3
        assert summary["by_severity"]["critical"] == 1
        assert summary["by_severity"]["medium"] == 1
        assert summary["by_severity"]["low"] == 1
        assert len(summary["critical_events"]) == 1
        
        print("✅ 安全事件摘要测试通过")
    
    def test_environment_security_check(self):
        """测试环境安全检查"""
        auditor = SecurityAuditor()
        
        # 测试调试模式检查
        with patch.dict(os.environ, {"DEBUG": "true"}):
            issues = auditor.check_environment_security()
            assert any("Debug mode" in issue for issue in issues)
        
        # 测试默认密码检查
        with patch.dict(os.environ, {"DB_PASSWORD": "password"}):
            issues = auditor.check_environment_security()
            assert any("Default password" in issue for issue in issues)
        
        print("✅ 环境安全检查测试通过")


class TestIntegration:
    """集成测试"""
    
    def test_security_managers_integration(self):
        """测试安全管理器集成"""
        # 获取全局实例
        api_manager = get_api_key_manager()
        validator = get_input_validator()
        controller = get_access_controller()
        auditor = get_security_auditor()
        
        # 测试实例是否正确创建
        assert api_manager is not None
        assert validator is not None
        assert controller is not None
        assert auditor is not None
        
        # 测试单例模式
        assert get_api_key_manager() is api_manager
        assert get_input_validator() is validator
        assert get_access_controller() is controller
        assert get_security_auditor() is auditor
        
        print("✅ 安全管理器集成测试通过")
    
    def test_security_workflow(self):
        """测试安全工作流"""
        validator = get_input_validator()
        controller = get_access_controller()
        auditor = get_security_auditor()
        
        # 模拟用户请求处理流程
        user_input = "AAPL"
        user_ip = "192.168.1.1"
        
        # 1. 验证输入
        if not validator.validate_stock_symbol(user_input):
            auditor.log_security_event(
                "invalid_input",
                SecurityLevel.MEDIUM,
                "Invalid stock symbol provided"
            )
            return False
        
        # 2. 检查速率限制
        if not controller.check_rate_limit(user_ip, max_requests=100):
            auditor.log_security_event(
                "rate_limit_exceeded",
                SecurityLevel.HIGH,
                "Rate limit exceeded"
            )
            return False
        
        # 3. 检查IP是否被阻止
        if controller.is_ip_blocked(user_ip):
            auditor.log_security_event(
                "blocked_ip_access",
                SecurityLevel.CRITICAL,
                "Blocked IP attempted access"
            )
            return False
        
        # 请求成功
        auditor.log_security_event(
            "successful_request",
            SecurityLevel.LOW,
            "Request processed successfully"
        )
        
        assert len(auditor.events) >= 1
        print("✅ 安全工作流测试通过")


def run_security_tests():
    """运行安全性测试"""
    print("🧪 运行安全性测试...")
    
    test_classes = [
        TestAPIKeyManager,
        TestInputValidator,
        TestAccessController,
        TestSecurityAuditor,
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
                passed_tests += 1
            except Exception as e:
                print(f"  ❌ {method_name}: {e}")
    
    print(f"\n📊 测试结果: {passed_tests}/{total_tests} 通过")
    return passed_tests == total_tests


def run_tests():
    """运行测试的标准接口"""
    return run_security_tests()


if __name__ == "__main__":
    success = run_security_tests()
    sys.exit(0 if success else 1)
