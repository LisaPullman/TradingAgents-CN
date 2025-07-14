#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents-CN 生产环境启动脚本
支持优雅关闭、健康检查和资源监控
"""

import os
import sys
import signal
import time
import threading
from pathlib import Path
from typing import Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tradingagents.core.logging_config import get_logger, setup_logging
from tradingagents.core.monitoring import start_monitoring, stop_monitoring
from tradingagents.core.performance import optimize_memory
from tradingagents.api.health import get_health_checker


class ProductionServer:
    """生产环境服务器"""
    
    def __init__(self):
        self.logger = get_logger("production_server")
        self.health_checker = get_health_checker()
        self.running = False
        self.shutdown_event = threading.Event()
        
        # 设置信号处理
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # 如果在Unix系统上，也处理SIGHUP
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        signal_name = signal.Signals(signum).name
        self.logger.info(f"Received signal {signal_name}, initiating graceful shutdown...")
        self.shutdown()
    
    def setup_environment(self):
        """设置生产环境"""
        # 设置环境变量
        os.environ.setdefault('TRADINGAGENTS_ENV', 'production')
        os.environ.setdefault('TRADINGAGENTS_LOG_LEVEL', 'INFO')
        os.environ.setdefault('TRADINGAGENTS_LOG_DIR', './logs')
        
        # 创建必要的目录
        log_dir = Path(os.environ['TRADINGAGENTS_LOG_DIR'])
        log_dir.mkdir(exist_ok=True)
        
        data_dir = Path('./data')
        data_dir.mkdir(exist_ok=True)
        
        cache_dir = Path('./cache')
        cache_dir.mkdir(exist_ok=True)
        
        # 设置日志
        setup_logging(
            log_level=os.environ['TRADINGAGENTS_LOG_LEVEL'],
            log_dir=str(log_dir)
        )
        
        self.logger.info("Production environment setup completed")
    
    def start_services(self):
        """启动服务"""
        self.logger.info("Starting TradingAgents-CN production services...")
        
        # 启动监控系统
        start_monitoring()
        self.logger.info("Monitoring system started")
        
        # 优化内存
        collected = optimize_memory()
        self.logger.info(f"Memory optimization completed, collected {collected} objects")
        
        # 启动健康检查
        self.logger.info("Health check system ready")
        
        # 这里可以添加其他服务的启动逻辑
        # 例如：Web服务器、API服务器、后台任务等
        
        self.running = True
        self.logger.info("All services started successfully")
    
    def run_health_monitor(self):
        """运行健康监控"""
        while self.running and not self.shutdown_event.is_set():
            try:
                health_data = self.health_checker.get_detailed_health()
                status = health_data.get("status", "unknown")
                
                if status == "unhealthy":
                    self.logger.critical("System health check failed", health_status=status)
                elif status == "degraded":
                    self.logger.warning("System performance degraded", health_status=status)
                else:
                    self.logger.debug("System health check passed", health_status=status)
                
                # 等待30秒或直到收到关闭信号
                self.shutdown_event.wait(30)
                
            except Exception as e:
                self.logger.error("Health monitoring error", exception=e)
                self.shutdown_event.wait(10)
    
    def run_streamlit_app(self):
        """运行Streamlit应用"""
        try:
            import streamlit.web.cli as stcli
            import sys
            
            # 设置Streamlit参数
            sys.argv = [
                "streamlit",
                "run",
                "web/app.py",
                "--server.address=0.0.0.0",
                "--server.port=8501",
                "--server.headless=true",
                "--server.enableCORS=false",
                "--server.enableXsrfProtection=false"
            ]
            
            self.logger.info("Starting Streamlit application...")
            stcli.main()
            
        except Exception as e:
            self.logger.error("Failed to start Streamlit application", exception=e)
            raise
    
    def run(self):
        """运行服务器"""
        try:
            # 设置环境
            self.setup_environment()
            
            # 启动服务
            self.start_services()
            
            # 启动健康监控线程
            health_thread = threading.Thread(target=self.run_health_monitor, daemon=True)
            health_thread.start()
            
            # 检查是否需要启动Streamlit
            if os.getenv('START_STREAMLIT', 'true').lower() == 'true':
                # 在主线程中运行Streamlit
                self.run_streamlit_app()
            else:
                # 如果不启动Streamlit，保持服务运行
                self.logger.info("Server running, waiting for shutdown signal...")
                while self.running and not self.shutdown_event.is_set():
                    self.shutdown_event.wait(1)
            
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.critical("Server startup failed", exception=e)
            raise
        finally:
            self.shutdown()
    
    def shutdown(self):
        """优雅关闭"""
        if not self.running:
            return
        
        self.logger.info("Initiating graceful shutdown...")
        self.running = False
        self.shutdown_event.set()
        
        try:
            # 停止监控系统
            stop_monitoring()
            self.logger.info("Monitoring system stopped")
            
            # 执行最后的内存优化
            collected = optimize_memory()
            self.logger.info(f"Final memory cleanup completed, collected {collected} objects")
            
            self.logger.info("Graceful shutdown completed")
            
        except Exception as e:
            self.logger.error("Error during shutdown", exception=e)


def main():
    """主函数"""
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    # 检查必要的环境变量
    required_env_vars = []
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {missing_vars}")
        print("Please check your .env file or environment configuration")
        sys.exit(1)
    
    # 创建并运行服务器
    server = ProductionServer()
    
    try:
        server.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
