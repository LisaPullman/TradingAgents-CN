# 错误处理和容错性改进方案

## 🎯 改进目标
- 建立统一的异常处理机制
- 实现优雅的错误降级策略
- 提供用户友好的错误信息
- 增强系统稳定性和可靠性

## 📋 具体改进措施

### 1. 统一异常处理框架

#### 1.1 创建异常处理基类
```python
# tradingagents/core/exceptions.py
class TradingAgentsException(Exception):
    """TradingAgents基础异常类"""
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class APIException(TradingAgentsException):
    """API调用异常"""
    pass

class DataSourceException(TradingAgentsException):
    """数据源异常"""
    pass

class AnalysisException(TradingAgentsException):
    """分析过程异常"""
    pass

class ConfigurationException(TradingAgentsException):
    """配置异常"""
    pass
```

#### 1.2 异常处理装饰器
```python
# tradingagents/core/decorators.py
import functools
import logging
from typing import Callable, Any

def handle_exceptions(
    fallback_value: Any = None,
    log_error: bool = True,
    reraise: bool = False
):
    """统一异常处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except TradingAgentsException as e:
                if log_error:
                    logging.error(f"{func.__name__} failed: {e.message}", 
                                extra={"error_code": e.error_code, "details": e.details})
                if reraise:
                    raise
                return fallback_value
            except Exception as e:
                if log_error:
                    logging.error(f"{func.__name__} unexpected error: {str(e)}")
                if reraise:
                    raise TradingAgentsException(f"Unexpected error in {func.__name__}: {str(e)}")
                return fallback_value
        return wrapper
    return decorator
```

### 2. API调用容错机制

#### 2.1 重试机制
```python
# tradingagents/core/retry.py
import time
import random
from typing import Callable, Any

class RetryConfig:
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0, 
                 max_delay: float = 60.0, exponential_base: float = 2.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base

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
                except (APIException, ConnectionError, TimeoutError) as e:
                    last_exception = e
                    if attempt == config.max_attempts - 1:
                        break
                    
                    # 计算延迟时间（指数退避 + 随机抖动）
                    delay = min(
                        config.base_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )
                    jitter = random.uniform(0, delay * 0.1)
                    time.sleep(delay + jitter)
                    
                    logging.warning(f"Retry {attempt + 1}/{config.max_attempts} for {func.__name__}")
            
            raise last_exception
        return wrapper
    return decorator
```

#### 2.2 断路器模式
```python
# tradingagents/core/circuit_breaker.py
import time
from enum import Enum
from typing import Callable

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func: Callable, *args, **kwargs):
        """通过断路器调用函数"""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise APIException("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

### 3. 数据源容错改进

#### 3.1 智能数据源切换
```python
# tradingagents/dataflows/resilient_data_manager.py
class ResilientDataManager:
    def __init__(self):
        self.data_sources = [
            ("tushare", self._get_tushare_data),
            ("akshare", self._get_akshare_data),
            ("baostock", self._get_baostock_data),
            ("fallback", self._get_fallback_data)
        ]
        self.circuit_breakers = {
            source: CircuitBreaker() for source, _ in self.data_sources
        }
    
    @handle_exceptions(fallback_value="❌ 所有数据源均不可用")
    def get_stock_data_resilient(self, symbol: str, start_date: str, end_date: str) -> str:
        """弹性数据获取"""
        errors = []
        
        for source_name, source_func in self.data_sources:
            try:
                circuit_breaker = self.circuit_breakers[source_name]
                result = circuit_breaker.call(source_func, symbol, start_date, end_date)
                
                if self._is_valid_data(result):
                    logging.info(f"Successfully got data from {source_name}")
                    return result
                else:
                    errors.append(f"{source_name}: 数据质量不符合要求")
                    
            except Exception as e:
                errors.append(f"{source_name}: {str(e)}")
                logging.warning(f"Data source {source_name} failed: {e}")
                continue
        
        # 所有数据源都失败，返回详细错误信息
        error_summary = "\n".join([f"- {error}" for error in errors])
        return f"❌ 数据获取失败\n\n详细错误:\n{error_summary}\n\n💡 建议检查网络连接和API配置"
```

### 4. LLM调用容错

#### 4.1 模型降级策略
```python
# tradingagents/llm_adapters/resilient_llm.py
class ResilientLLMManager:
    def __init__(self, config: dict):
        self.config = config
        self.model_hierarchy = [
            ("primary", self._get_primary_model),
            ("secondary", self._get_secondary_model),
            ("fallback", self._get_fallback_model)
        ]
    
    @retry_with_backoff(RetryConfig(max_attempts=2))
    def invoke_with_fallback(self, messages: list, **kwargs) -> str:
        """带降级的LLM调用"""
        errors = []
        
        for level, model_getter in self.model_hierarchy:
            try:
                model = model_getter()
                if model is None:
                    continue
                
                result = model.invoke(messages, **kwargs)
                logging.info(f"LLM call successful with {level} model")
                return result
                
            except Exception as e:
                errors.append(f"{level}: {str(e)}")
                logging.warning(f"LLM {level} model failed: {e}")
                continue
        
        # 所有模型都失败
        error_summary = "; ".join(errors)
        raise AnalysisException(
            f"所有LLM模型调用失败: {error_summary}",
            error_code="LLM_ALL_FAILED",
            details={"errors": errors}
        )
```

### 5. 用户友好的错误信息

#### 5.1 错误信息本地化
```python
# tradingagents/core/error_messages.py
ERROR_MESSAGES = {
    "API_KEY_MISSING": {
        "zh": "API密钥未配置，请检查环境变量设置",
        "en": "API key not configured, please check environment variables"
    },
    "NETWORK_ERROR": {
        "zh": "网络连接失败，请检查网络设置",
        "en": "Network connection failed, please check network settings"
    },
    "DATA_SOURCE_UNAVAILABLE": {
        "zh": "数据源暂时不可用，正在尝试备用数据源",
        "en": "Data source temporarily unavailable, trying backup sources"
    },
    "ANALYSIS_FAILED": {
        "zh": "分析过程失败，请稍后重试",
        "en": "Analysis failed, please try again later"
    }
}

def get_user_friendly_message(error_code: str, language: str = "zh") -> str:
    """获取用户友好的错误信息"""
    return ERROR_MESSAGES.get(error_code, {}).get(language, f"未知错误: {error_code}")
```

### 6. 健康检查和自愈机制

#### 6.1 系统健康检查
```python
# tradingagents/core/health_check.py
class HealthChecker:
    def __init__(self):
        self.checks = [
            ("database", self._check_database),
            ("redis", self._check_redis),
            ("api_keys", self._check_api_keys),
            ("data_sources", self._check_data_sources),
            ("llm_models", self._check_llm_models)
        ]
    
    def run_health_check(self) -> dict:
        """运行完整的健康检查"""
        results = {}
        overall_status = "healthy"
        
        for check_name, check_func in self.checks:
            try:
                result = check_func()
                results[check_name] = result
                if result["status"] != "healthy":
                    overall_status = "degraded"
            except Exception as e:
                results[check_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                overall_status = "unhealthy"
        
        return {
            "overall_status": overall_status,
            "checks": results,
            "timestamp": time.time()
        }
```

## 📈 实施优先级

### 高优先级 (立即实施)
1. 统一异常处理框架
2. API调用重试机制
3. 用户友好错误信息

### 中优先级 (1-2周内)
1. 数据源容错改进
2. LLM调用降级策略
3. 断路器模式

### 低优先级 (1个月内)
1. 健康检查系统
2. 自愈机制
3. 高级监控功能

## 🎯 预期效果

实施这些改进后，系统将具备：
- 🛡️ **更强的容错能力**: 单点故障不会导致系统崩溃
- 🔄 **自动恢复能力**: 临时故障后能自动恢复正常
- 👥 **更好的用户体验**: 清晰的错误信息和处理建议
- 📊 **更高的可用性**: 系统整体可用性提升到99.5%以上
