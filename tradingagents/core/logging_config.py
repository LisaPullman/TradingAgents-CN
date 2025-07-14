#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents-CN 统一日志配置
提供结构化日志记录、性能监控和错误追踪
"""

import os
import sys
import json
import time
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from contextlib import contextmanager


class StructuredFormatter(logging.Formatter):
    """结构化日志格式器"""
    
    def format(self, record):
        # 基础日志信息
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # 添加额外的结构化信息
        if hasattr(record, 'extra_data'):
            log_entry.update(record.extra_data)
        
        # 添加异常信息
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # 添加性能信息
        if hasattr(record, 'duration'):
            log_entry["duration_ms"] = record.duration
        
        # 添加用户信息
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        
        # 添加请求信息
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        
        return json.dumps(log_entry, ensure_ascii=False)


class PerformanceLogger:
    """性能监控日志器"""
    
    def __init__(self, logger_name: str = "performance"):
        self.logger = logging.getLogger(logger_name)
    
    @contextmanager
    def measure(self, operation: str, **kwargs):
        """测量操作执行时间"""
        start_time = time.time()
        operation_id = f"{operation}_{int(start_time)}"
        
        self.logger.info(
            f"Operation started: {operation}",
            extra={
                "extra_data": {
                    "operation": operation,
                    "operation_id": operation_id,
                    "status": "started",
                    **kwargs
                }
            }
        )
        
        try:
            yield operation_id
            duration = (time.time() - start_time) * 1000
            self.logger.info(
                f"Operation completed: {operation}",
                extra={
                    "extra_data": {
                        "operation": operation,
                        "operation_id": operation_id,
                        "status": "completed",
                        "duration_ms": duration,
                        **kwargs
                    }
                }
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.logger.error(
                f"Operation failed: {operation}",
                extra={
                    "extra_data": {
                        "operation": operation,
                        "operation_id": operation_id,
                        "status": "failed",
                        "duration_ms": duration,
                        "error": str(e),
                        **kwargs
                    }
                },
                exc_info=True
            )
            raise


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.metrics = {}
        self.logger = logging.getLogger("metrics")
    
    def increment(self, metric_name: str, value: int = 1, tags: Dict[str, str] = None):
        """增加计数器指标"""
        key = self._get_metric_key(metric_name, tags)
        self.metrics[key] = self.metrics.get(key, 0) + value
        
        self.logger.info(
            f"Metric incremented: {metric_name}",
            extra={
                "extra_data": {
                    "metric_type": "counter",
                    "metric_name": metric_name,
                    "value": value,
                    "total": self.metrics[key],
                    "tags": tags or {}
                }
            }
        )
    
    def gauge(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """设置仪表盘指标"""
        key = self._get_metric_key(metric_name, tags)
        self.metrics[key] = value
        
        self.logger.info(
            f"Metric set: {metric_name}",
            extra={
                "extra_data": {
                    "metric_type": "gauge",
                    "metric_name": metric_name,
                    "value": value,
                    "tags": tags or {}
                }
            }
        )
    
    def histogram(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """记录直方图指标"""
        self.logger.info(
            f"Metric recorded: {metric_name}",
            extra={
                "extra_data": {
                    "metric_type": "histogram",
                    "metric_name": metric_name,
                    "value": value,
                    "tags": tags or {}
                }
            }
        )
    
    def _get_metric_key(self, metric_name: str, tags: Dict[str, str] = None) -> str:
        """生成指标键"""
        if not tags:
            return metric_name
        
        tag_str = ",".join([f"{k}={v}" for k, v in sorted(tags.items())])
        return f"{metric_name}[{tag_str}]"
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取所有指标"""
        return self.metrics.copy()


class TradingAgentsLogger:
    """TradingAgents统一日志器"""
    
    def __init__(self, name: str = "tradingagents"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.performance = PerformanceLogger(f"{name}.performance")
        self.metrics = MetricsCollector()
        self._setup_logger()
    
    def _setup_logger(self):
        """设置日志器"""
        if self.logger.handlers:
            return  # 已经设置过了
        
        # 设置日志级别
        log_level = os.getenv('TRADINGAGENTS_LOG_LEVEL', 'INFO').upper()
        self.logger.setLevel(getattr(logging, log_level, logging.INFO))
        
        # 创建日志目录
        log_dir = Path(os.getenv('TRADINGAGENTS_LOG_DIR', './logs'))
        log_dir.mkdir(exist_ok=True)
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器（结构化日志）
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / f"{self.name}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(file_handler)
        
        # 错误文件处理器
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / f"{self.name}_error.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(error_handler)
    
    def debug(self, message: str, **kwargs):
        """调试日志"""
        self.logger.debug(message, extra={"extra_data": kwargs})
    
    def info(self, message: str, **kwargs):
        """信息日志"""
        self.logger.info(message, extra={"extra_data": kwargs})
    
    def warning(self, message: str, **kwargs):
        """警告日志"""
        self.logger.warning(message, extra={"extra_data": kwargs})
    
    def error(self, message: str, exception: Exception = None, **kwargs):
        """错误日志"""
        if exception:
            kwargs["error_type"] = type(exception).__name__
            kwargs["error_message"] = str(exception)
        
        self.logger.error(message, extra={"extra_data": kwargs}, exc_info=exception)
    
    def critical(self, message: str, **kwargs):
        """严重错误日志"""
        self.logger.critical(message, extra={"extra_data": kwargs})
    
    def log_api_call(self, api_name: str, method: str, url: str, 
                     status_code: int = None, duration: float = None, **kwargs):
        """记录API调用"""
        self.info(
            f"API call: {api_name}",
            api_name=api_name,
            method=method,
            url=url,
            status_code=status_code,
            duration_ms=duration * 1000 if duration else None,
            **kwargs
        )
    
    def log_analysis_start(self, analyst_type: str, symbol: str, **kwargs):
        """记录分析开始"""
        self.info(
            f"Analysis started: {analyst_type}",
            analyst_type=analyst_type,
            symbol=symbol,
            **kwargs
        )
    
    def log_analysis_complete(self, analyst_type: str, symbol: str, 
                            duration: float, success: bool = True, **kwargs):
        """记录分析完成"""
        level = "info" if success else "error"
        getattr(self, level)(
            f"Analysis {'completed' if success else 'failed'}: {analyst_type}",
            analyst_type=analyst_type,
            symbol=symbol,
            duration_ms=duration * 1000,
            success=success,
            **kwargs
        )
    
    def log_llm_call(self, model_name: str, prompt_tokens: int = None, 
                     completion_tokens: int = None, cost: float = None, **kwargs):
        """记录LLM调用"""
        self.info(
            f"LLM call: {model_name}",
            model_name=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=(prompt_tokens or 0) + (completion_tokens or 0),
            cost=cost,
            **kwargs
        )


# 全局日志器实例
_loggers = {}


def get_logger(name: str = "tradingagents") -> TradingAgentsLogger:
    """获取日志器实例"""
    if name not in _loggers:
        _loggers[name] = TradingAgentsLogger(name)
    return _loggers[name]


def setup_logging(log_level: str = None, log_dir: str = None):
    """设置全局日志配置"""
    if log_level:
        os.environ['TRADINGAGENTS_LOG_LEVEL'] = log_level
    
    if log_dir:
        os.environ['TRADINGAGENTS_LOG_DIR'] = log_dir
    
    # 重新初始化所有日志器
    for logger in _loggers.values():
        logger._setup_logger()


# 便捷的全局日志器
logger = get_logger()
performance = logger.performance
metrics = logger.metrics
