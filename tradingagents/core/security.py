#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents-CN 安全模块
提供API密钥管理、输入验证、访问控制等安全功能
"""

import os
import re
import hashlib
import secrets
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .logging_config import get_logger
from .exceptions import TradingAgentsException, ErrorCategory, ErrorSeverity


class SecurityLevel(Enum):
    """安全级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """安全事件"""
    event_type: str
    severity: SecurityLevel
    message: str
    details: Dict[str, Any]
    timestamp: float
    source_ip: Optional[str] = None
    user_id: Optional[str] = None


class APIKeyManager:
    """API密钥管理器"""
    
    def __init__(self):
        self.logger = get_logger("security.api_keys")
        self._masked_keys_cache = {}
    
    def validate_api_key(self, key: str, provider: str) -> bool:
        """验证API密钥格式"""
        if not key or not isinstance(key, str):
            return False
        
        # 不同提供商的密钥格式验证
        patterns = {
            "openai": r"^sk-[a-zA-Z0-9]{48}$",
            "siliconflow": r"^sk-[a-zA-Z0-9\-_]{20,}$",
            "deepseek": r"^sk-[a-zA-Z0-9]{48}$",
            "dashscope": r"^sk-[a-zA-Z0-9]{32}$",
            "default": r"^[a-zA-Z0-9\-_]{10,}$"
        }
        
        pattern = patterns.get(provider.lower(), patterns["default"])
        
        if not re.match(pattern, key):
            self.logger.warning(
                f"Invalid API key format for {provider}",
                provider=provider,
                key_length=len(key)
            )
            return False
        
        return True
    
    def mask_api_key(self, key: str) -> str:
        """掩码API密钥用于日志记录"""
        if not key:
            return "None"
        
        if key in self._masked_keys_cache:
            return self._masked_keys_cache[key]
        
        if len(key) <= 8:
            masked = "*" * len(key)
        else:
            masked = key[:4] + "*" * (len(key) - 8) + key[-4:]
        
        self._masked_keys_cache[key] = masked
        return masked
    
    def check_key_exposure(self, text: str) -> List[str]:
        """检查文本中是否暴露了API密钥"""
        # 常见的API密钥模式
        key_patterns = [
            r"sk-[a-zA-Z0-9]{48}",  # OpenAI/DeepSeek格式
            r"sk-[a-zA-Z0-9\-_]{20,}",  # SiliconFlow格式
            r"[a-zA-Z0-9]{32,}",  # 通用长密钥
        ]
        
        exposed_keys = []
        for pattern in key_patterns:
            matches = re.findall(pattern, text)
            exposed_keys.extend(matches)
        
        if exposed_keys:
            self.logger.critical(
                "API keys detected in text",
                exposed_count=len(exposed_keys),
                security_event="key_exposure"
            )
        
        return exposed_keys
    
    def get_secure_env_var(self, var_name: str, required: bool = True) -> Optional[str]:
        """安全地获取环境变量"""
        value = os.getenv(var_name)
        
        if required and not value:
            self.logger.error(
                f"Required environment variable not set: {var_name}",
                security_event="missing_env_var"
            )
            raise TradingAgentsException(
                f"Required environment variable {var_name} not set",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH
            )
        
        if value:
            self.logger.debug(
                f"Environment variable loaded: {var_name}",
                masked_value=self.mask_api_key(value)
            )
        
        return value


class InputValidator:
    """输入验证器"""
    
    def __init__(self):
        self.logger = get_logger("security.input_validator")
    
    def validate_stock_symbol(self, symbol: str) -> bool:
        """验证股票代码"""
        if not symbol or not isinstance(symbol, str):
            return False
        
        # 移除空白字符
        symbol = symbol.strip().upper()
        
        # 基本格式检查
        if not re.match(r"^[A-Z0-9.]{1,10}$", symbol):
            self.logger.warning(
                "Invalid stock symbol format",
                symbol=symbol,
                security_event="invalid_input"
            )
            return False
        
        # 检查恶意模式
        malicious_patterns = [
            r"[<>\"'&]",  # HTML/SQL注入字符
            r"(script|javascript|vbscript)",  # 脚本标签
            r"(union|select|insert|update|delete|drop)",  # SQL关键词
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, symbol, re.IGNORECASE):
                self.logger.critical(
                    "Malicious pattern detected in stock symbol",
                    symbol=symbol,
                    pattern=pattern,
                    security_event="injection_attempt"
                )
                return False
        
        return True
    
    def validate_date_string(self, date_str: str) -> bool:
        """验证日期字符串"""
        if not date_str or not isinstance(date_str, str):
            return False
        
        # 严格的日期格式验证
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return False
        
        try:
            from datetime import datetime
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def sanitize_user_input(self, user_input: str, max_length: int = 1000) -> str:
        """清理用户输入"""
        if not user_input:
            return ""
        
        # 长度限制
        if len(user_input) > max_length:
            self.logger.warning(
                "User input truncated due to length",
                original_length=len(user_input),
                max_length=max_length
            )
            user_input = user_input[:max_length]
        
        # 移除危险字符
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00', '\r', '\n']
        for char in dangerous_chars:
            user_input = user_input.replace(char, '')
        
        # 移除多余空白
        user_input = re.sub(r'\s+', ' ', user_input).strip()
        
        return user_input
    
    def check_injection_patterns(self, text: str) -> List[str]:
        """检查注入攻击模式"""
        injection_patterns = [
            (r"<script[^>]*>.*?</script>", "XSS"),
            (r"javascript:", "JavaScript injection"),
            (r"(union|select|insert|update|delete|drop)\s+", "SQL injection"),
            (r"(exec|eval|system|shell_exec)\s*\(", "Code injection"),
            (r"\.\.\/", "Path traversal"),
            (r"(file|http|ftp)://", "URL injection"),
        ]
        
        detected_patterns = []
        for pattern, attack_type in injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                detected_patterns.append(attack_type)
                self.logger.critical(
                    f"Injection attack detected: {attack_type}",
                    pattern=pattern,
                    text_preview=text[:100],
                    security_event="injection_attack"
                )
        
        return detected_patterns


class AccessController:
    """访问控制器"""
    
    def __init__(self):
        self.logger = get_logger("security.access_control")
        self.rate_limits = {}
        self.blocked_ips = set()
    
    def check_rate_limit(self, identifier: str, max_requests: int = 100, 
                        window_seconds: int = 3600) -> bool:
        """检查速率限制"""
        current_time = time.time()
        
        if identifier not in self.rate_limits:
            self.rate_limits[identifier] = []
        
        # 清理过期的请求记录
        self.rate_limits[identifier] = [
            req_time for req_time in self.rate_limits[identifier]
            if current_time - req_time < window_seconds
        ]
        
        # 检查是否超过限制
        if len(self.rate_limits[identifier]) >= max_requests:
            self.logger.warning(
                "Rate limit exceeded",
                identifier=identifier,
                requests_count=len(self.rate_limits[identifier]),
                max_requests=max_requests,
                security_event="rate_limit_exceeded"
            )
            return False
        
        # 记录当前请求
        self.rate_limits[identifier].append(current_time)
        return True
    
    def block_ip(self, ip_address: str, reason: str):
        """阻止IP地址"""
        self.blocked_ips.add(ip_address)
        self.logger.critical(
            f"IP address blocked: {ip_address}",
            reason=reason,
            security_event="ip_blocked"
        )
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """检查IP是否被阻止"""
        return ip_address in self.blocked_ips
    
    def validate_file_access(self, file_path: str, allowed_dirs: List[str]) -> bool:
        """验证文件访问权限"""
        try:
            # 规范化路径
            normalized_path = os.path.normpath(os.path.abspath(file_path))
            
            # 检查是否在允许的目录内
            for allowed_dir in allowed_dirs:
                allowed_abs = os.path.normpath(os.path.abspath(allowed_dir))
                if normalized_path.startswith(allowed_abs):
                    return True
            
            self.logger.warning(
                "Unauthorized file access attempt",
                file_path=file_path,
                normalized_path=normalized_path,
                security_event="unauthorized_file_access"
            )
            return False
            
        except Exception as e:
            self.logger.error(
                "File access validation error",
                file_path=file_path,
                error=str(e)
            )
            return False


class SecurityAuditor:
    """安全审计器"""
    
    def __init__(self):
        self.logger = get_logger("security.auditor")
        self.events: List[SecurityEvent] = []
    
    def log_security_event(self, event_type: str, severity: SecurityLevel,
                          message: str, **details):
        """记录安全事件"""
        event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            message=message,
            details=details,
            timestamp=time.time()
        )
        
        self.events.append(event)
        
        # 根据严重程度选择日志级别
        if severity == SecurityLevel.CRITICAL:
            self.logger.critical(message, **details)
        elif severity == SecurityLevel.HIGH:
            self.logger.error(message, **details)
        elif severity == SecurityLevel.MEDIUM:
            self.logger.warning(message, **details)
        else:
            self.logger.info(message, **details)
    
    def get_security_summary(self, hours: int = 24) -> Dict[str, Any]:
        """获取安全事件摘要"""
        cutoff_time = time.time() - (hours * 3600)
        recent_events = [e for e in self.events if e.timestamp >= cutoff_time]
        
        summary = {
            "total_events": len(recent_events),
            "by_severity": {},
            "by_type": {},
            "critical_events": []
        }
        
        for event in recent_events:
            # 按严重程度统计
            severity = event.severity.value
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
            
            # 按类型统计
            event_type = event.event_type
            summary["by_type"][event_type] = summary["by_type"].get(event_type, 0) + 1
            
            # 收集严重事件
            if event.severity in [SecurityLevel.CRITICAL, SecurityLevel.HIGH]:
                summary["critical_events"].append({
                    "type": event.event_type,
                    "message": event.message,
                    "timestamp": event.timestamp
                })
        
        return summary
    
    def check_environment_security(self) -> List[str]:
        """检查环境安全配置"""
        issues = []
        
        # 检查调试模式
        if os.getenv('DEBUG', '').lower() in ['true', '1', 'yes']:
            issues.append("Debug mode is enabled in production")
        
        # 检查默认密码
        default_passwords = ['password', '123456', 'admin', 'root']
        for env_var in os.environ:
            if 'password' in env_var.lower():
                value = os.getenv(env_var, '').lower()
                if value in default_passwords:
                    issues.append(f"Default password detected in {env_var}")
        
        # 检查文件权限
        sensitive_files = ['.env', 'config.py', 'secrets.json']
        for file_name in sensitive_files:
            if os.path.exists(file_name):
                file_stat = os.stat(file_name)
                if file_stat.st_mode & 0o077:  # 检查其他用户权限
                    issues.append(f"Insecure file permissions for {file_name}")
        
        return issues


# 全局安全实例
_api_key_manager = None
_input_validator = None
_access_controller = None
_security_auditor = None


def get_api_key_manager() -> APIKeyManager:
    """获取API密钥管理器"""
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager


def get_input_validator() -> InputValidator:
    """获取输入验证器"""
    global _input_validator
    if _input_validator is None:
        _input_validator = InputValidator()
    return _input_validator


def get_access_controller() -> AccessController:
    """获取访问控制器"""
    global _access_controller
    if _access_controller is None:
        _access_controller = AccessController()
    return _access_controller


def get_security_auditor() -> SecurityAuditor:
    """获取安全审计器"""
    global _security_auditor
    if _security_auditor is None:
        _security_auditor = SecurityAuditor()
    return _security_auditor
