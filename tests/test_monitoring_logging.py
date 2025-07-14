#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控和日志系统测试
测试日志记录、性能监控、健康检查等功能
"""

import os
import time
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.core.logging_config import (
    TradingAgentsLogger, StructuredFormatter, PerformanceLogger,
    MetricsCollector, get_logger, setup_logging
)
from tradingagents.core.monitoring import (
    HealthChecker, SystemMonitor, AlertManager, TradingAgentsMonitor,
    HealthStatus, HealthCheckResult, SystemMetrics, get_monitor
)


class TestLoggingSystem:
    """测试日志系统"""
    
    def test_structured_formatter(self):
        """测试结构化格式器"""
        import logging
        
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # 添加额外数据
        record.extra_data = {"key": "value", "number": 123}
        
        formatted = formatter.format(record)
        parsed = json.loads(formatted)
        
        assert parsed["message"] == "Test message"
        assert parsed["level"] == "INFO"
        assert parsed["key"] == "value"
        assert parsed["number"] == 123
        print("✅ 结构化格式器测试通过")
    
    def test_performance_logger(self):
        """测试性能日志器"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['TRADINGAGENTS_LOG_DIR'] = temp_dir
            
            perf_logger = PerformanceLogger("test_performance")
            
            # 测试性能测量
            with perf_logger.measure("test_operation", param1="value1"):
                time.sleep(0.01)  # 模拟操作
            
            print("✅ 性能日志器测试通过")
    
    def test_metrics_collector(self):
        """测试指标收集器"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['TRADINGAGENTS_LOG_DIR'] = temp_dir
            
            metrics = MetricsCollector()
            
            # 测试计数器
            metrics.increment("api_calls", 1, {"endpoint": "test"})
            metrics.increment("api_calls", 2, {"endpoint": "test"})
            
            # 测试仪表盘
            metrics.gauge("cpu_usage", 75.5)
            
            # 测试直方图
            metrics.histogram("response_time", 123.45)
            
            # 获取指标
            all_metrics = metrics.get_metrics()
            assert "api_calls[endpoint=test]" in all_metrics
            assert all_metrics["api_calls[endpoint=test]"] == 3
            assert all_metrics["cpu_usage"] == 75.5
            
            print("✅ 指标收集器测试通过")
    
    def test_trading_agents_logger(self):
        """测试TradingAgents日志器"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['TRADINGAGENTS_LOG_DIR'] = temp_dir
            
            logger = TradingAgentsLogger("test_logger")
            
            # 测试各种日志级别
            logger.debug("Debug message", debug_info="test")
            logger.info("Info message", info_data="test")
            logger.warning("Warning message", warning_type="test")
            logger.error("Error message", error_code="TEST_001")
            
            # 测试专用日志方法
            logger.log_api_call("test_api", "GET", "http://test.com", 200, 0.5)
            logger.log_analysis_start("market", "AAPL")
            logger.log_analysis_complete("market", "AAPL", 2.5, True)
            logger.log_llm_call("gpt-4", 100, 50, 0.01)
            
            # 检查日志文件是否创建
            log_file = Path(temp_dir) / "test_logger.log"
            assert log_file.exists()
            
            print("✅ TradingAgents日志器测试通过")


class TestMonitoringSystem:
    """测试监控系统"""
    
    def test_health_checker(self):
        """测试健康检查器"""
        checker = HealthChecker()
        
        # 注册测试检查
        def healthy_check():
            return HealthCheckResult(
                name="test_healthy",
                status=HealthStatus.HEALTHY,
                message="All good"
            )
        
        def unhealthy_check():
            return HealthCheckResult(
                name="test_unhealthy",
                status=HealthStatus.UNHEALTHY,
                message="Something wrong"
            )
        
        def failing_check():
            raise Exception("Check failed")
        
        checker.register_check("healthy", healthy_check)
        checker.register_check("unhealthy", unhealthy_check)
        checker.register_check("failing", failing_check)
        
        # 运行单个检查
        result = checker.run_check("healthy")
        assert result.status == HealthStatus.HEALTHY
        
        # 运行所有检查
        results = checker.run_all_checks()
        assert len(results) == 3
        assert results["healthy"].status == HealthStatus.HEALTHY
        assert results["unhealthy"].status == HealthStatus.UNHEALTHY
        assert results["failing"].status == HealthStatus.UNHEALTHY
        
        # 测试整体状态
        overall = checker.get_overall_status(results)
        assert overall == HealthStatus.UNHEALTHY
        
        print("✅ 健康检查器测试通过")
    
    def test_system_monitor(self):
        """测试系统监控器"""
        monitor = SystemMonitor(interval=1)
        
        # 测试指标收集
        metrics = monitor.collect_metrics()
        assert isinstance(metrics, SystemMetrics)
        assert metrics.cpu_percent >= 0
        assert metrics.memory_percent >= 0
        assert metrics.disk_percent >= 0
        assert isinstance(metrics.network_io, dict)
        assert metrics.process_count > 0
        
        print("✅ 系统监控器测试通过")
    
    def test_alert_manager(self):
        """测试告警管理器"""
        alert_manager = AlertManager()
        
        # 添加告警处理器
        alerts_received = []
        def test_handler(alert):
            alerts_received.append(alert)
        
        alert_manager.add_handler(test_handler)
        
        # 发送告警
        alert_manager.send_alert("warning", "Test alert", component="test")
        
        # 检查告警
        assert len(alerts_received) == 1
        assert alerts_received[0]["level"] == "warning"
        assert alerts_received[0]["message"] == "Test alert"
        
        # 获取最近告警
        recent = alert_manager.get_recent_alerts(hours=1)
        assert len(recent) == 1
        
        print("✅ 告警管理器测试通过")
    
    def test_trading_agents_monitor(self):
        """测试TradingAgents监控系统"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['TRADINGAGENTS_LOG_DIR'] = temp_dir
            
            monitor = TradingAgentsMonitor()
            
            # 测试健康状态
            health_status = monitor.get_health_status()
            assert "overall_status" in health_status
            assert "checks" in health_status
            assert "timestamp" in health_status
            
            # 测试系统状态
            system_status = monitor.get_system_status()
            assert "metrics" in system_status
            assert "recent_alerts" in system_status
            assert "monitoring_active" in system_status
            
            print("✅ TradingAgents监控系统测试通过")


class TestIntegration:
    """集成测试"""
    
    def test_logging_monitoring_integration(self):
        """测试日志和监控集成"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['TRADINGAGENTS_LOG_DIR'] = temp_dir
            
            # 获取全局实例
            logger = get_logger("integration_test")
            monitor = get_monitor()
            
            # 记录一些日志
            logger.info("Integration test started")
            
            with logger.performance.measure("test_operation"):
                time.sleep(0.01)
            
            logger.metrics.increment("test_counter")
            logger.metrics.gauge("test_gauge", 42.0)
            
            # 检查健康状态
            health = monitor.get_health_status()
            assert health["overall_status"] in ["healthy", "degraded", "unhealthy"]
            
            logger.info("Integration test completed")
            
            print("✅ 日志监控集成测试通过")
    
    def test_error_logging_integration(self):
        """测试错误日志集成"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['TRADINGAGENTS_LOG_DIR'] = temp_dir
            
            logger = get_logger("error_test")
            
            # 测试异常日志记录
            try:
                raise ValueError("Test error")
            except Exception as e:
                logger.error("Test error occurred", exception=e, context="test")
            
            # 检查错误日志文件
            error_log = Path(temp_dir) / "error_test_error.log"
            assert error_log.exists()
            
            print("✅ 错误日志集成测试通过")


def run_monitoring_logging_tests():
    """运行监控和日志测试"""
    print("🧪 运行监控和日志系统测试...")
    
    # 设置测试环境
    os.environ['TRADINGAGENTS_LOG_LEVEL'] = 'DEBUG'
    
    test_classes = [
        TestLoggingSystem,
        TestMonitoringSystem,
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
    return run_monitoring_logging_tests()


if __name__ == "__main__":
    success = run_monitoring_logging_tests()
    exit(0 if success else 1)
