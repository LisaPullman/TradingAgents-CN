#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents-CN 监控系统
提供系统健康检查、性能监控和告警功能
"""

import os
import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum

from .logging_config import get_logger


class HealthStatus(Enum):
    """健康状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheckResult:
    """健康检查结果"""
    name: str
    status: HealthStatus
    message: str
    details: Dict[str, Any] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.details is None:
            self.details = {}


@dataclass
class SystemMetrics:
    """系统指标"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    process_count: int
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.checks: Dict[str, Callable] = {}
        self.logger = get_logger("health_checker")
    
    def register_check(self, name: str, check_func: Callable):
        """注册健康检查函数"""
        self.checks[name] = check_func
        self.logger.info(f"Registered health check: {name}")
    
    def run_check(self, name: str) -> HealthCheckResult:
        """运行单个健康检查"""
        if name not in self.checks:
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check '{name}' not found"
            )
        
        try:
            result = self.checks[name]()
            if isinstance(result, HealthCheckResult):
                return result
            elif isinstance(result, dict):
                return HealthCheckResult(name=name, **result)
            else:
                return HealthCheckResult(
                    name=name,
                    status=HealthStatus.HEALTHY,
                    message=str(result)
                )
        except Exception as e:
            self.logger.error(f"Health check '{name}' failed", exception=e)
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Check failed: {str(e)}",
                details={"error_type": type(e).__name__}
            )
    
    def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """运行所有健康检查"""
        results = {}
        for name in self.checks:
            results[name] = self.run_check(name)
        return results
    
    def get_overall_status(self, results: Dict[str, HealthCheckResult]) -> HealthStatus:
        """获取整体健康状态"""
        if not results:
            return HealthStatus.UNHEALTHY
        
        statuses = [result.status for result in results.values()]
        
        if any(status == HealthStatus.UNHEALTHY for status in statuses):
            return HealthStatus.UNHEALTHY
        elif any(status == HealthStatus.DEGRADED for status in statuses):
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY


class SystemMonitor:
    """系统监控器"""
    
    def __init__(self, interval: int = 60):
        self.interval = interval
        self.running = False
        self.thread = None
        self.logger = get_logger("system_monitor")
        self.metrics_history: List[SystemMetrics] = []
        self.max_history = 1440  # 24小时的分钟数
    
    def start(self):
        """启动监控"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        self.logger.info("System monitoring started")
    
    def stop(self):
        """停止监控"""
        self.running = False
        if self.thread:
            self.thread.join()
        self.logger.info("System monitoring stopped")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                metrics = self.collect_metrics()
                self.metrics_history.append(metrics)
                
                # 保持历史记录在限制范围内
                if len(self.metrics_history) > self.max_history:
                    self.metrics_history = self.metrics_history[-self.max_history:]
                
                # 记录指标
                self.logger.info(
                    "System metrics collected",
                    cpu_percent=metrics.cpu_percent,
                    memory_percent=metrics.memory_percent,
                    disk_percent=metrics.disk_percent,
                    process_count=metrics.process_count
                )
                
                # 检查告警条件
                self._check_alerts(metrics)
                
            except Exception as e:
                self.logger.error("Error collecting system metrics", exception=e)
            
            time.sleep(self.interval)
    
    def collect_metrics(self) -> SystemMetrics:
        """收集系统指标"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存使用率
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # 磁盘使用率
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        # 网络IO
        network = psutil.net_io_counters()
        network_io = {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
            "packets_sent": network.packets_sent,
            "packets_recv": network.packets_recv
        }
        
        # 进程数量
        process_count = len(psutil.pids())
        
        return SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_percent=disk_percent,
            network_io=network_io,
            process_count=process_count
        )
    
    def _check_alerts(self, metrics: SystemMetrics):
        """检查告警条件"""
        # CPU告警
        if metrics.cpu_percent > 90:
            self.logger.warning(
                "High CPU usage detected",
                cpu_percent=metrics.cpu_percent,
                alert_type="high_cpu"
            )
        
        # 内存告警
        if metrics.memory_percent > 90:
            self.logger.warning(
                "High memory usage detected",
                memory_percent=metrics.memory_percent,
                alert_type="high_memory"
            )
        
        # 磁盘告警
        if metrics.disk_percent > 90:
            self.logger.warning(
                "High disk usage detected",
                disk_percent=metrics.disk_percent,
                alert_type="high_disk"
            )
    
    def get_latest_metrics(self) -> Optional[SystemMetrics]:
        """获取最新指标"""
        return self.metrics_history[-1] if self.metrics_history else None
    
    def get_metrics_history(self, hours: int = 1) -> List[SystemMetrics]:
        """获取指标历史"""
        if not self.metrics_history:
            return []
        
        cutoff_time = time.time() - (hours * 3600)
        return [m for m in self.metrics_history if m.timestamp >= cutoff_time]


class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.alerts: List[Dict[str, Any]] = []
        self.alert_handlers: List[Callable] = []
        self.logger = get_logger("alert_manager")
    
    def add_handler(self, handler: Callable):
        """添加告警处理器"""
        self.alert_handlers.append(handler)
    
    def send_alert(self, level: str, message: str, **kwargs):
        """发送告警"""
        alert = {
            "level": level,
            "message": message,
            "timestamp": time.time(),
            "details": kwargs
        }
        
        self.alerts.append(alert)
        self.logger.warning(f"Alert: {message}", alert_level=level, **kwargs)
        
        # 调用所有告警处理器
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Alert handler failed: {e}")
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """获取最近的告警"""
        cutoff_time = time.time() - (hours * 3600)
        return [alert for alert in self.alerts if alert["timestamp"] >= cutoff_time]


class TradingAgentsMonitor:
    """TradingAgents监控系统"""
    
    def __init__(self):
        self.health_checker = HealthChecker()
        self.system_monitor = SystemMonitor()
        self.alert_manager = AlertManager()
        self.logger = get_logger("monitor")
        
        # 注册默认健康检查
        self._register_default_checks()
    
    def _register_default_checks(self):
        """注册默认健康检查"""
        
        def check_system_resources():
            """检查系统资源"""
            metrics = self.system_monitor.collect_metrics()
            
            if metrics.cpu_percent > 95 or metrics.memory_percent > 95:
                return HealthCheckResult(
                    name="system_resources",
                    status=HealthStatus.UNHEALTHY,
                    message="System resources critically low",
                    details=asdict(metrics)
                )
            elif metrics.cpu_percent > 80 or metrics.memory_percent > 80:
                return HealthCheckResult(
                    name="system_resources",
                    status=HealthStatus.DEGRADED,
                    message="System resources under pressure",
                    details=asdict(metrics)
                )
            else:
                return HealthCheckResult(
                    name="system_resources",
                    status=HealthStatus.HEALTHY,
                    message="System resources normal",
                    details=asdict(metrics)
                )
        
        def check_log_directory():
            """检查日志目录"""
            log_dir = os.getenv('TRADINGAGENTS_LOG_DIR', './logs')
            if not os.path.exists(log_dir):
                return HealthCheckResult(
                    name="log_directory",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Log directory does not exist: {log_dir}"
                )
            elif not os.access(log_dir, os.W_OK):
                return HealthCheckResult(
                    name="log_directory",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Log directory not writable: {log_dir}"
                )
            else:
                return HealthCheckResult(
                    name="log_directory",
                    status=HealthStatus.HEALTHY,
                    message="Log directory accessible"
                )
        
        self.health_checker.register_check("system_resources", check_system_resources)
        self.health_checker.register_check("log_directory", check_log_directory)
    
    def start_monitoring(self):
        """启动监控"""
        self.system_monitor.start()
        self.logger.info("TradingAgents monitoring started")
    
    def stop_monitoring(self):
        """停止监控"""
        self.system_monitor.stop()
        self.logger.info("TradingAgents monitoring stopped")
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        check_results = self.health_checker.run_all_checks()
        overall_status = self.health_checker.get_overall_status(check_results)
        
        return {
            "overall_status": overall_status.value,
            "checks": {name: asdict(result) for name, result in check_results.items()},
            "timestamp": time.time()
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        latest_metrics = self.system_monitor.get_latest_metrics()
        recent_alerts = self.alert_manager.get_recent_alerts(hours=1)
        
        return {
            "metrics": asdict(latest_metrics) if latest_metrics else None,
            "recent_alerts": recent_alerts,
            "monitoring_active": self.system_monitor.running,
            "timestamp": time.time()
        }


# 全局监控实例
_monitor = None


def get_monitor() -> TradingAgentsMonitor:
    """获取监控实例"""
    global _monitor
    if _monitor is None:
        _monitor = TradingAgentsMonitor()
    return _monitor


def start_monitoring():
    """启动全局监控"""
    monitor = get_monitor()
    monitor.start_monitoring()


def stop_monitoring():
    """停止全局监控"""
    monitor = get_monitor()
    monitor.stop_monitoring()
