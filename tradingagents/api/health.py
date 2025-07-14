#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents-CN 健康检查API
提供系统健康状态检查端点
"""

import time
import psutil
from typing import Dict, Any
from datetime import datetime

from ..core.monitoring import get_monitor
from ..core.security import get_security_auditor
from ..core.performance import get_system_performance
from ..core.logging_config import get_logger


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.logger = get_logger("health_api")
        self.start_time = time.time()
    
    def get_basic_health(self) -> Dict[str, Any]:
        """获取基础健康状态"""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time() - self.start_time,
            "version": "1.0.0"
        }
    
    def get_detailed_health(self) -> Dict[str, Any]:
        """获取详细健康状态"""
        try:
            # 基础信息
            health_data = self.get_basic_health()
            
            # 系统性能
            performance = get_system_performance()
            health_data["performance"] = performance
            
            # 监控状态
            monitor = get_monitor()
            monitoring_status = monitor.get_health_status()
            health_data["monitoring"] = monitoring_status
            
            # 安全状态
            security_auditor = get_security_auditor()
            security_summary = security_auditor.get_security_summary(hours=1)
            health_data["security"] = {
                "recent_events": len(security_summary.get("by_type", {})),
                "critical_events": len([
                    e for e in security_summary.get("critical_events", [])
                ])
            }
            
            # 系统资源
            health_data["resources"] = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            }
            
            # 确定整体状态
            overall_status = self._determine_overall_status(health_data)
            health_data["status"] = overall_status
            
            return health_data
            
        except Exception as e:
            self.logger.error("Health check failed", exception=e)
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _determine_overall_status(self, health_data: Dict[str, Any]) -> str:
        """确定整体健康状态"""
        try:
            resources = health_data.get("resources", {})
            
            # 检查CPU使用率
            if resources.get("cpu_percent", 0) > 90:
                return "unhealthy"
            
            # 检查内存使用率
            if resources.get("memory_percent", 0) > 90:
                return "unhealthy"
            
            # 检查磁盘使用率
            if resources.get("disk_percent", 0) > 95:
                return "unhealthy"
            
            # 检查监控状态
            monitoring = health_data.get("monitoring", {})
            if monitoring.get("overall_status") == "unhealthy":
                return "degraded"
            
            # 检查安全事件
            security = health_data.get("security", {})
            if security.get("critical_events", 0) > 0:
                return "degraded"
            
            # 检查性能指标
            performance = health_data.get("performance", {})
            if (performance.get("cpu_percent", 0) > 80 or 
                performance.get("memory_percent", 0) > 80):
                return "degraded"
            
            return "healthy"
            
        except Exception:
            return "unknown"
    
    def get_readiness(self) -> Dict[str, Any]:
        """获取就绪状态（用于Kubernetes readiness probe）"""
        try:
            # 检查关键组件是否就绪
            readiness_checks = {
                "database": self._check_database_connection(),
                "cache": self._check_cache_connection(),
                "monitoring": self._check_monitoring_system(),
                "security": self._check_security_system()
            }
            
            all_ready = all(readiness_checks.values())
            
            return {
                "ready": all_ready,
                "timestamp": datetime.now().isoformat(),
                "checks": readiness_checks
            }
            
        except Exception as e:
            self.logger.error("Readiness check failed", exception=e)
            return {
                "ready": False,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _check_database_connection(self) -> bool:
        """检查数据库连接"""
        try:
            # 这里应该实际检查数据库连接
            # 暂时返回True，实际部署时需要实现具体的数据库检查
            return True
        except Exception:
            return False
    
    def _check_cache_connection(self) -> bool:
        """检查缓存连接"""
        try:
            # 这里应该实际检查Redis连接
            # 暂时返回True，实际部署时需要实现具体的缓存检查
            return True
        except Exception:
            return False
    
    def _check_monitoring_system(self) -> bool:
        """检查监控系统"""
        try:
            monitor = get_monitor()
            health_status = monitor.get_health_status()
            return health_status.get("overall_status") != "unhealthy"
        except Exception:
            return False
    
    def _check_security_system(self) -> bool:
        """检查安全系统"""
        try:
            security_auditor = get_security_auditor()
            # 如果能获取安全摘要，说明安全系统正常
            security_auditor.get_security_summary(hours=1)
            return True
        except Exception:
            return False


# 全局健康检查器实例
_health_checker = None


def get_health_checker() -> HealthChecker:
    """获取健康检查器实例"""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


# Flask/FastAPI 路由函数
def health_endpoint():
    """基础健康检查端点"""
    checker = get_health_checker()
    return checker.get_basic_health()


def health_detailed_endpoint():
    """详细健康检查端点"""
    checker = get_health_checker()
    return checker.get_detailed_health()


def readiness_endpoint():
    """就绪检查端点"""
    checker = get_health_checker()
    return checker.get_readiness()


def liveness_endpoint():
    """存活检查端点"""
    return {
        "alive": True,
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time() - get_health_checker().start_time
    }


# Streamlit 健康检查函数
def streamlit_health_check():
    """Streamlit应用健康检查"""
    import streamlit as st
    
    checker = get_health_checker()
    health_data = checker.get_detailed_health()
    
    # 显示健康状态
    status = health_data.get("status", "unknown")
    if status == "healthy":
        st.success(f"🟢 系统状态: {status}")
    elif status == "degraded":
        st.warning(f"🟡 系统状态: {status}")
    else:
        st.error(f"🔴 系统状态: {status}")
    
    # 显示详细信息
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("系统资源")
        resources = health_data.get("resources", {})
        st.metric("CPU使用率", f"{resources.get('cpu_percent', 0):.1f}%")
        st.metric("内存使用率", f"{resources.get('memory_percent', 0):.1f}%")
        st.metric("磁盘使用率", f"{resources.get('disk_percent', 0):.1f}%")
    
    with col2:
        st.subheader("系统信息")
        st.metric("运行时间", f"{health_data.get('uptime', 0):.0f}秒")
        st.metric("版本", health_data.get('version', 'unknown'))
        
        monitoring = health_data.get("monitoring", {})
        st.metric("监控状态", monitoring.get("overall_status", "unknown"))
    
    return health_data


if __name__ == "__main__":
    # 命令行健康检查
    import sys
    
    checker = get_health_checker()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--detailed":
        health_data = checker.get_detailed_health()
    else:
        health_data = checker.get_basic_health()
    
    import json
    print(json.dumps(health_data, indent=2, ensure_ascii=False))
    
    # 根据健康状态设置退出码
    status = health_data.get("status", "unknown")
    if status == "healthy":
        sys.exit(0)
    elif status == "degraded":
        sys.exit(1)
    else:
        sys.exit(2)
