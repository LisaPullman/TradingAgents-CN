#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误处理装饰器
提供统一的异常处理、重试机制和断路器模式
"""

import time
import random
import functools
import logging
from typing import Callable, Any, Optional, Type, Union
from enum import Enum

from .exceptions import (
    TradingAgentsException, APIException, NetworkException, 
    ErrorCategory, ErrorSeverity, convert_exception
)


class CircuitState(Enum):
    """断路器状态"""
    CLOSED = "closed"      # 正常状态
    OPEN = "open"          # 断开状态
    HALF_OPEN = "half_open" # 半开状态


class RetryConfig:
    """重试配置"""
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: tuple = None
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or (
            APIException, NetworkException, ConnectionError, TimeoutError
        )


class CircuitBreaker:
    """断路器实现"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.success_count = 0  # 半开状态下的成功计数
    
    def call(self, func: Callable, *args, **kwargs):
        """通过断路器调用函数"""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                logging.info(f"Circuit breaker for {func.__name__} switched to HALF_OPEN")
            else:
                raise APIException(
                    f"Circuit breaker is OPEN for {func.__name__}",
                    error_code="CIRCUIT_BREAKER_OPEN"
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """成功回调"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 3:  # 连续3次成功后关闭断路器
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                logging.info("Circuit breaker switched to CLOSED")
        else:
            self.failure_count = 0
    
    def _on_failure(self):
        """失败回调"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logging.warning(f"Circuit breaker switched to OPEN after {self.failure_count} failures")


# 全局断路器实例
_circuit_breakers = {}


def get_circuit_breaker(name: str, **kwargs) -> CircuitBreaker:
    """获取或创建断路器实例"""
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(**kwargs)
    return _circuit_breakers[name]


def handle_exceptions(
    fallback_value: Any = None,
    log_error: bool = True,
    reraise: bool = False,
    context: str = None,
    category: ErrorCategory = ErrorCategory.API
):
    """统一异常处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except TradingAgentsException as e:
                if log_error:
                    logging.error(
                        f"{func.__name__} failed: {e.message}",
                        extra={
                            "error_code": e.error_code,
                            "category": e.category.value,
                            "severity": e.severity.value,
                            "details": e.details
                        }
                    )
                if reraise:
                    raise
                return fallback_value
            except Exception as e:
                # 转换为TradingAgents异常
                trading_exception = convert_exception(e, context or func.__name__)
                trading_exception.category = category
                
                if log_error:
                    logging.error(
                        f"{func.__name__} unexpected error: {str(e)}",
                        extra={
                            "error_code": trading_exception.error_code,
                            "original_type": type(e).__name__
                        }
                    )
                
                if reraise:
                    raise trading_exception
                return fallback_value
        return wrapper
    return decorator


def retry_with_backoff(config: RetryConfig = None):
    """带指数退避的重试装饰器"""
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except config.retryable_exceptions as e:
                    last_exception = e
                    if attempt == config.max_attempts - 1:
                        break
                    
                    # 计算延迟时间（指数退避 + 随机抖动）
                    delay = min(
                        config.base_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )
                    
                    if config.jitter:
                        jitter = random.uniform(0, delay * 0.1)
                        delay += jitter
                    
                    logging.warning(
                        f"Retry {attempt + 1}/{config.max_attempts} for {func.__name__} "
                        f"after {delay:.2f}s delay. Error: {str(e)}"
                    )
                    time.sleep(delay)
                except Exception as e:
                    # 非可重试异常，直接抛出
                    raise
            
            # 所有重试都失败了
            if isinstance(last_exception, TradingAgentsException):
                raise last_exception
            else:
                raise convert_exception(last_exception, f"All {config.max_attempts} retries failed")
        
        return wrapper
    return decorator


def circuit_breaker(
    name: str = None,
    failure_threshold: int = 5,
    timeout: float = 60.0,
    expected_exception: Type[Exception] = Exception
):
    """断路器装饰器"""
    def decorator(func: Callable) -> Callable:
        breaker_name = name or f"{func.__module__}.{func.__name__}"
        breaker = get_circuit_breaker(
            breaker_name,
            failure_threshold=failure_threshold,
            timeout=timeout,
            expected_exception=expected_exception
        )
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        
        return wrapper
    return decorator


def resilient_call(
    retry_config: RetryConfig = None,
    circuit_breaker_config: dict = None,
    fallback_value: Any = None,
    context: str = None
):
    """综合弹性调用装饰器（重试 + 断路器 + 异常处理）"""
    def decorator(func: Callable) -> Callable:
        # 应用断路器
        if circuit_breaker_config:
            func = circuit_breaker(**circuit_breaker_config)(func)
        
        # 应用重试机制
        if retry_config:
            func = retry_with_backoff(retry_config)(func)
        
        # 应用异常处理
        func = handle_exceptions(
            fallback_value=fallback_value,
            context=context or func.__name__
        )(func)
        
        return func
    return decorator


def timeout(seconds: float):
    """超时装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")
            
            # 设置超时信号
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(seconds))
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # 恢复原来的信号处理器
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        
        return wrapper
    return decorator


def validate_inputs(**validators):
    """输入验证装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取函数参数名
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # 验证参数
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not validator(value):
                        from .exceptions import ValidationException
                        raise ValidationException(
                            f"Parameter '{param_name}' validation failed",
                            field_name=param_name,
                            details={"value": str(value), "validator": validator.__name__}
                        )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# 常用验证器
def is_valid_stock_code(code: str) -> bool:
    """验证股票代码格式"""
    if not isinstance(code, str):
        return False
    # 简单的股票代码验证（可以根据需要扩展）
    return len(code) >= 4 and code.replace('.', '').isalnum()


def is_valid_date(date_str: str) -> bool:
    """验证日期格式"""
    if not isinstance(date_str, str):
        return False
    try:
        from datetime import datetime
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def is_positive_number(value) -> bool:
    """验证正数"""
    try:
        return float(value) > 0
    except (ValueError, TypeError):
        return False
