#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents-CN 统一异常处理框架
提供健壮的错误处理和用户友好的错误信息
"""

import time
import traceback
from enum import Enum
from typing import Dict, Any, Optional


class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"          # 轻微错误，不影响主要功能
    MEDIUM = "medium"    # 中等错误，影响部分功能
    HIGH = "high"        # 严重错误，影响核心功能
    CRITICAL = "critical" # 致命错误，系统无法继续运行


class ErrorCategory(Enum):
    """错误分类"""
    API = "api"                    # API调用错误
    DATA_SOURCE = "data_source"    # 数据源错误
    LLM = "llm"                   # 大模型调用错误
    ANALYSIS = "analysis"          # 分析过程错误
    CONFIGURATION = "configuration" # 配置错误
    NETWORK = "network"           # 网络错误
    DATABASE = "database"         # 数据库错误
    VALIDATION = "validation"     # 数据验证错误
    PERMISSION = "permission"     # 权限错误
    RESOURCE = "resource"         # 资源不足错误


class TradingAgentsException(Exception):
    """TradingAgents基础异常类"""
    
    def __init__(
        self,
        message: str,
        error_code: str = None,
        category: ErrorCategory = ErrorCategory.API,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Dict[str, Any] = None,
        suggestions: list = None,
        original_exception: Exception = None
    ):
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.suggestions = suggestions or []
        self.original_exception = original_exception
        self.timestamp = time.time()
        self.traceback_info = traceback.format_exc() if original_exception else None
        self.error_code = error_code or self._generate_error_code()

        super().__init__(self.message)
    
    def _generate_error_code(self) -> str:
        """生成错误代码"""
        return f"{self.category.value.upper()}_{int(self.timestamp)}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "details": self.details,
            "suggestions": self.suggestions,
            "timestamp": self.timestamp,
            "traceback": self.traceback_info
        }
    
    def get_user_message(self, language: str = "zh") -> str:
        """获取用户友好的错误信息"""
        from .error_messages import get_user_friendly_message
        return get_user_friendly_message(self.error_code, self.category, language)


class APIException(TradingAgentsException):
    """API调用异常"""

    def __init__(self, message: str, api_name: str = None, status_code: int = None, **kwargs):
        details = kwargs.pop('details', {})
        details.update({
            "api_name": api_name,
            "status_code": status_code
        })

        suggestions = kwargs.pop('suggestions', [])
        if status_code == 401:
            suggestions.append("检查API密钥是否正确配置")
        elif status_code == 429:
            suggestions.append("API调用频率过高，请稍后重试")
        elif status_code == 500:
            suggestions.append("API服务器内部错误，请稍后重试")

        super().__init__(
            message=message,
            category=ErrorCategory.API,
            severity=ErrorSeverity.HIGH if status_code in [401, 403] else ErrorSeverity.MEDIUM,
            details=details,
            suggestions=suggestions,
            **kwargs
        )

        # 在父类初始化后设置子类特有属性
        self.api_name = api_name
        self.status_code = status_code


class DataSourceException(TradingAgentsException):
    """数据源异常"""

    def __init__(self, message: str, source_name: str = None, **kwargs):
        details = kwargs.pop('details', {})
        details.update({"source_name": source_name})

        suggestions = kwargs.pop('suggestions', [])
        suggestions.extend([
            "检查网络连接是否正常",
            "确认数据源API配置正确",
            "尝试使用备用数据源"
        ])

        super().__init__(
            message=message,
            category=ErrorCategory.DATA_SOURCE,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            suggestions=suggestions,
            **kwargs
        )

        self.source_name = source_name


class LLMException(TradingAgentsException):
    """大模型调用异常"""

    def __init__(self, message: str, model_name: str = None, **kwargs):
        details = kwargs.pop('details', {})
        details.update({"model_name": model_name})

        suggestions = kwargs.pop('suggestions', [])
        suggestions.extend([
            "检查LLM API密钥配置",
            "确认模型名称正确",
            "尝试使用备用模型"
        ])

        super().__init__(
            message=message,
            category=ErrorCategory.LLM,
            severity=ErrorSeverity.HIGH,
            details=details,
            suggestions=suggestions,
            **kwargs
        )

        self.model_name = model_name


class AnalysisException(TradingAgentsException):
    """分析过程异常"""

    def __init__(self, message: str, analyst_type: str = None, **kwargs):
        details = kwargs.pop('details', {})
        details.update({"analyst_type": analyst_type})

        suggestions = kwargs.pop('suggestions', [])
        suggestions.extend([
            "检查输入数据是否完整",
            "确认分析参数配置正确",
            "尝试简化分析请求"
        ])

        super().__init__(
            message=message,
            category=ErrorCategory.ANALYSIS,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            suggestions=suggestions,
            **kwargs
        )

        self.analyst_type = analyst_type


class ConfigurationException(TradingAgentsException):
    """配置异常"""

    def __init__(self, message: str, config_key: str = None, **kwargs):
        self.config_key = config_key

        details = kwargs.pop('details', {})
        details.update({"config_key": config_key})

        suggestions = kwargs.pop('suggestions', [])
        suggestions.extend([
            "检查.env文件配置",
            "确认环境变量设置正确",
            "参考配置文档示例"
        ])

        super().__init__(
            message=message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH,
            details=details,
            suggestions=suggestions,
            **kwargs
        )


class NetworkException(TradingAgentsException):
    """网络异常"""

    def __init__(self, message: str, url: str = None, **kwargs):
        self.url = url

        details = kwargs.pop('details', {})
        details.update({"url": url})

        suggestions = kwargs.pop('suggestions', [])
        suggestions.extend([
            "检查网络连接",
            "确认防火墙设置",
            "尝试使用代理或VPN"
        ])

        super().__init__(
            message=message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            suggestions=suggestions,
            **kwargs
        )


class DatabaseException(TradingAgentsException):
    """数据库异常"""

    def __init__(self, message: str, operation: str = None, **kwargs):
        self.operation = operation

        details = kwargs.pop('details', {})
        details.update({"operation": operation})

        suggestions = kwargs.pop('suggestions', [])
        suggestions.extend([
            "检查数据库连接配置",
            "确认数据库服务运行正常",
            "检查数据库权限设置"
        ])

        super().__init__(
            message=message,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            details=details,
            suggestions=suggestions,
            **kwargs
        )


class ValidationException(TradingAgentsException):
    """数据验证异常"""

    def __init__(self, message: str, field_name: str = None, **kwargs):
        details = kwargs.pop('details', {})
        details.update({"field_name": field_name})

        suggestions = kwargs.pop('suggestions', [])
        suggestions.extend([
            "检查输入数据格式",
            "确认数据类型正确",
            "参考API文档要求"
        ])

        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            details=details,
            suggestions=suggestions,
            **kwargs
        )

        self.field_name = field_name


# 异常映射表，用于将常见异常转换为TradingAgents异常
EXCEPTION_MAPPING = {
    ConnectionError: NetworkException,
    TimeoutError: NetworkException,
    ValueError: ValidationException,
    KeyError: ConfigurationException,
    FileNotFoundError: ConfigurationException,
    PermissionError: TradingAgentsException,
}


def convert_exception(exc: Exception, context: str = None) -> TradingAgentsException:
    """将标准异常转换为TradingAgents异常"""
    exc_type = type(exc)
    
    if isinstance(exc, TradingAgentsException):
        return exc
    
    # 查找映射的异常类型
    mapped_exception_class = EXCEPTION_MAPPING.get(exc_type, TradingAgentsException)
    
    message = f"{context}: {str(exc)}" if context else str(exc)
    
    return mapped_exception_class(
        message=message,
        original_exception=exc,
        details={"original_type": exc_type.__name__}
    )
