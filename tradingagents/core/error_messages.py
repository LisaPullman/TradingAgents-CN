#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误信息本地化模块
提供用户友好的多语言错误信息
"""

from .exceptions import ErrorCategory


# 错误信息模板
ERROR_MESSAGES = {
    # API相关错误
    "API_KEY_MISSING": {
        "zh": "API密钥未配置，请在.env文件中设置相应的API密钥",
        "en": "API key not configured, please set the API key in .env file"
    },
    "API_KEY_INVALID": {
        "zh": "API密钥无效，请检查密钥格式和有效性",
        "en": "Invalid API key, please check the key format and validity"
    },
    "API_RATE_LIMIT": {
        "zh": "API调用频率超限，请稍后重试",
        "en": "API rate limit exceeded, please try again later"
    },
    "API_QUOTA_EXCEEDED": {
        "zh": "API配额已用完，请检查账户余额",
        "en": "API quota exceeded, please check account balance"
    },
    "API_SERVER_ERROR": {
        "zh": "API服务器内部错误，请稍后重试",
        "en": "API server internal error, please try again later"
    },
    
    # 数据源相关错误
    "DATA_SOURCE_UNAVAILABLE": {
        "zh": "数据源暂时不可用，正在尝试备用数据源",
        "en": "Data source temporarily unavailable, trying backup sources"
    },
    "DATA_SOURCE_TIMEOUT": {
        "zh": "数据源响应超时，请检查网络连接",
        "en": "Data source timeout, please check network connection"
    },
    "DATA_QUALITY_POOR": {
        "zh": "数据质量不符合要求，建议稍后重试",
        "en": "Data quality does not meet requirements, recommend retry later"
    },
    "STOCK_CODE_INVALID": {
        "zh": "股票代码格式不正确，请检查输入",
        "en": "Invalid stock code format, please check input"
    },
    
    # LLM相关错误
    "LLM_MODEL_UNAVAILABLE": {
        "zh": "指定的LLM模型不可用，正在切换到备用模型",
        "en": "Specified LLM model unavailable, switching to backup model"
    },
    "LLM_CONTEXT_TOO_LONG": {
        "zh": "输入内容过长，请减少输入文本长度",
        "en": "Input content too long, please reduce input text length"
    },
    "LLM_CONTENT_FILTERED": {
        "zh": "内容被安全过滤器拦截，请调整输入内容",
        "en": "Content filtered by safety filter, please adjust input"
    },
    
    # 分析相关错误
    "ANALYSIS_FAILED": {
        "zh": "分析过程失败，请检查输入数据和配置",
        "en": "Analysis failed, please check input data and configuration"
    },
    "ANALYSIS_TIMEOUT": {
        "zh": "分析超时，请尝试简化分析请求",
        "en": "Analysis timeout, please try to simplify analysis request"
    },
    "INSUFFICIENT_DATA": {
        "zh": "数据不足以进行有效分析，请扩大时间范围",
        "en": "Insufficient data for effective analysis, please expand time range"
    },
    
    # 配置相关错误
    "CONFIG_FILE_MISSING": {
        "zh": "配置文件缺失，请创建.env文件",
        "en": "Configuration file missing, please create .env file"
    },
    "CONFIG_INVALID": {
        "zh": "配置参数无效，请检查配置文件格式",
        "en": "Invalid configuration, please check config file format"
    },
    "REQUIRED_CONFIG_MISSING": {
        "zh": "必需的配置项缺失，请补充完整配置",
        "en": "Required configuration missing, please complete configuration"
    },
    
    # 网络相关错误
    "NETWORK_CONNECTION_FAILED": {
        "zh": "网络连接失败，请检查网络设置",
        "en": "Network connection failed, please check network settings"
    },
    "NETWORK_TIMEOUT": {
        "zh": "网络请求超时，请检查网络稳定性",
        "en": "Network request timeout, please check network stability"
    },
    "PROXY_ERROR": {
        "zh": "代理设置错误，请检查代理配置",
        "en": "Proxy configuration error, please check proxy settings"
    },
    
    # 数据库相关错误
    "DATABASE_CONNECTION_FAILED": {
        "zh": "数据库连接失败，请检查数据库配置",
        "en": "Database connection failed, please check database configuration"
    },
    "DATABASE_OPERATION_FAILED": {
        "zh": "数据库操作失败，请检查数据库状态",
        "en": "Database operation failed, please check database status"
    },
    
    # 验证相关错误
    "INVALID_DATE_FORMAT": {
        "zh": "日期格式不正确，请使用YYYY-MM-DD格式",
        "en": "Invalid date format, please use YYYY-MM-DD format"
    },
    "INVALID_PARAMETER": {
        "zh": "参数值无效，请检查参数范围和类型",
        "en": "Invalid parameter value, please check parameter range and type"
    },
    
    # 权限相关错误
    "PERMISSION_DENIED": {
        "zh": "权限不足，请检查访问权限设置",
        "en": "Permission denied, please check access permissions"
    },
    "AUTHENTICATION_FAILED": {
        "zh": "身份验证失败，请检查认证信息",
        "en": "Authentication failed, please check credentials"
    },
    
    # 资源相关错误
    "MEMORY_INSUFFICIENT": {
        "zh": "内存不足，请释放内存或减少并发请求",
        "en": "Insufficient memory, please free memory or reduce concurrent requests"
    },
    "DISK_SPACE_INSUFFICIENT": {
        "zh": "磁盘空间不足，请清理磁盘空间",
        "en": "Insufficient disk space, please free disk space"
    }
}

# 分类特定的通用错误信息
CATEGORY_MESSAGES = {
    ErrorCategory.API: {
        "zh": "API调用出现问题，请检查API配置和网络连接",
        "en": "API call issue, please check API configuration and network connection"
    },
    ErrorCategory.DATA_SOURCE: {
        "zh": "数据源访问出现问题，正在尝试备用方案",
        "en": "Data source access issue, trying backup solutions"
    },
    ErrorCategory.LLM: {
        "zh": "大模型调用出现问题，正在尝试备用模型",
        "en": "LLM call issue, trying backup models"
    },
    ErrorCategory.ANALYSIS: {
        "zh": "分析过程出现问题，请检查输入数据",
        "en": "Analysis process issue, please check input data"
    },
    ErrorCategory.CONFIGURATION: {
        "zh": "配置出现问题，请检查配置文件",
        "en": "Configuration issue, please check config files"
    },
    ErrorCategory.NETWORK: {
        "zh": "网络连接出现问题，请检查网络设置",
        "en": "Network connection issue, please check network settings"
    },
    ErrorCategory.DATABASE: {
        "zh": "数据库操作出现问题，请检查数据库状态",
        "en": "Database operation issue, please check database status"
    },
    ErrorCategory.VALIDATION: {
        "zh": "数据验证失败，请检查输入格式",
        "en": "Data validation failed, please check input format"
    },
    ErrorCategory.PERMISSION: {
        "zh": "权限验证失败，请检查访问权限",
        "en": "Permission verification failed, please check access rights"
    },
    ErrorCategory.RESOURCE: {
        "zh": "系统资源不足，请稍后重试",
        "en": "Insufficient system resources, please try again later"
    }
}

# 解决方案建议
SOLUTION_SUGGESTIONS = {
    ErrorCategory.API: {
        "zh": [
            "检查API密钥是否正确配置",
            "确认API服务状态正常",
            "检查网络连接和防火墙设置",
            "查看API使用配额和余额"
        ],
        "en": [
            "Check if API key is correctly configured",
            "Confirm API service status is normal",
            "Check network connection and firewall settings",
            "Check API usage quota and balance"
        ]
    },
    ErrorCategory.DATA_SOURCE: {
        "zh": [
            "检查数据源API配置",
            "确认网络连接稳定",
            "尝试使用备用数据源",
            "检查数据源服务状态"
        ],
        "en": [
            "Check data source API configuration",
            "Confirm stable network connection",
            "Try using backup data sources",
            "Check data source service status"
        ]
    },
    ErrorCategory.LLM: {
        "zh": [
            "检查LLM API密钥配置",
            "确认模型名称正确",
            "尝试使用备用模型",
            "检查输入内容长度"
        ],
        "en": [
            "Check LLM API key configuration",
            "Confirm model name is correct",
            "Try using backup models",
            "Check input content length"
        ]
    }
}


def get_user_friendly_message(error_code: str, category: ErrorCategory, language: str = "zh") -> str:
    """获取用户友好的错误信息"""
    
    # 首先尝试获取具体的错误信息
    if error_code in ERROR_MESSAGES:
        return ERROR_MESSAGES[error_code].get(language, ERROR_MESSAGES[error_code].get("zh", "未知错误"))
    
    # 如果没有具体错误信息，使用分类通用信息
    if category in CATEGORY_MESSAGES:
        return CATEGORY_MESSAGES[category].get(language, CATEGORY_MESSAGES[category].get("zh", "系统错误"))
    
    # 最后的兜底信息
    if language == "en":
        return f"Unknown error occurred (Code: {error_code})"
    else:
        return f"发生未知错误 (错误代码: {error_code})"


def get_solution_suggestions(category: ErrorCategory, language: str = "zh") -> list:
    """获取解决方案建议"""
    if category in SOLUTION_SUGGESTIONS:
        return SOLUTION_SUGGESTIONS[category].get(language, SOLUTION_SUGGESTIONS[category].get("zh", []))
    
    # 通用建议
    if language == "en":
        return [
            "Check system configuration",
            "Verify network connection",
            "Try again later",
            "Contact support if problem persists"
        ]
    else:
        return [
            "检查系统配置",
            "验证网络连接",
            "稍后重试",
            "如问题持续请联系技术支持"
        ]


def format_error_for_user(exception, language: str = "zh") -> dict:
    """格式化错误信息供用户查看"""
    from .exceptions import TradingAgentsException
    
    if not isinstance(exception, TradingAgentsException):
        # 转换为TradingAgents异常
        from .exceptions import convert_exception
        exception = convert_exception(exception)
    
    user_message = get_user_friendly_message(exception.error_code, exception.category, language)
    suggestions = get_solution_suggestions(exception.category, language)
    
    return {
        "error_code": exception.error_code,
        "message": user_message,
        "category": exception.category.value,
        "severity": exception.severity.value,
        "suggestions": suggestions,
        "timestamp": exception.timestamp,
        "details": exception.details if hasattr(exception, 'details') else {}
    }
