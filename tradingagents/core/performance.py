#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents-CN 性能优化模块
提供缓存、并发处理、内存优化等性能提升功能
"""

import os
import time
import asyncio
import threading
import functools
import weakref
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import OrderedDict
import pickle
import hashlib

from .logging_config import get_logger


@dataclass
class PerformanceMetrics:
    """性能指标"""
    operation: str
    duration: float
    memory_usage: int
    cpu_usage: float
    cache_hits: int
    cache_misses: int
    timestamp: float


class LRUCache:
    """LRU缓存实现"""
    
    def __init__(self, max_size: int = 1000, ttl: Optional[float] = None):
        self.max_size = max_size
        self.ttl = ttl
        self.cache = OrderedDict()
        self.timestamps = {}
        self.hits = 0
        self.misses = 0
        self.logger = get_logger("performance.cache")
    
    def get(self, key: str) -> Any:
        """获取缓存值"""
        if key not in self.cache:
            self.misses += 1
            return None
        
        # 检查TTL
        if self.ttl and time.time() - self.timestamps[key] > self.ttl:
            del self.cache[key]
            del self.timestamps[key]
            self.misses += 1
            return None
        
        # 移动到末尾（最近使用）
        value = self.cache.pop(key)
        self.cache[key] = value
        self.hits += 1
        return value
    
    def set(self, key: str, value: Any):
        """设置缓存值"""
        if key in self.cache:
            # 更新现有值
            self.cache.pop(key)
        elif len(self.cache) >= self.max_size:
            # 移除最久未使用的项
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            if oldest_key in self.timestamps:
                del self.timestamps[oldest_key]
        
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.timestamps.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "ttl": self.ttl
        }


class MemoryPool:
    """内存池管理器"""
    
    def __init__(self, initial_size: int = 100):
        self.pool = []
        self.in_use = set()
        self.logger = get_logger("performance.memory_pool")
        
        # 预分配对象
        for _ in range(initial_size):
            self.pool.append({})
    
    def acquire(self) -> Dict:
        """获取对象"""
        if self.pool:
            obj = self.pool.pop()
            self.in_use.add(id(obj))
            return obj
        else:
            # 池为空，创建新对象
            obj = {}
            self.in_use.add(id(obj))
            return obj
    
    def release(self, obj: Dict):
        """释放对象"""
        obj_id = id(obj)
        if obj_id in self.in_use:
            obj.clear()  # 清空对象
            self.pool.append(obj)
            self.in_use.remove(obj_id)
    
    def get_stats(self) -> Dict[str, int]:
        """获取内存池统计"""
        return {
            "available": len(self.pool),
            "in_use": len(self.in_use),
            "total": len(self.pool) + len(self.in_use)
        }


class AsyncTaskManager:
    """异步任务管理器"""
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_tasks = {}
        self.logger = get_logger("performance.async_tasks")
    
    def submit_task(self, func: Callable, *args, **kwargs) -> str:
        """提交异步任务"""
        task_id = hashlib.md5(f"{func.__name__}_{time.time()}".encode()).hexdigest()
        
        future = self.executor.submit(func, *args, **kwargs)
        self.active_tasks[task_id] = {
            "future": future,
            "function": func.__name__,
            "start_time": time.time()
        }
        
        self.logger.info(f"Task submitted: {task_id}", function=func.__name__)
        return task_id
    
    def get_result(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """获取任务结果"""
        if task_id not in self.active_tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task_info = self.active_tasks[task_id]
        future = task_info["future"]
        
        try:
            result = future.result(timeout=timeout)
            duration = time.time() - task_info["start_time"]
            
            self.logger.info(
                f"Task completed: {task_id}",
                function=task_info["function"],
                duration=duration
            )
            
            del self.active_tasks[task_id]
            return result
            
        except Exception as e:
            self.logger.error(f"Task failed: {task_id}", error=str(e))
            del self.active_tasks[task_id]
            raise
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if task_id not in self.active_tasks:
            return False
        
        future = self.active_tasks[task_id]["future"]
        cancelled = future.cancel()
        
        if cancelled:
            del self.active_tasks[task_id]
            self.logger.info(f"Task cancelled: {task_id}")
        
        return cancelled
    
    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """获取活跃任务列表"""
        tasks = []
        for task_id, task_info in self.active_tasks.items():
            tasks.append({
                "task_id": task_id,
                "function": task_info["function"],
                "start_time": task_info["start_time"],
                "duration": time.time() - task_info["start_time"],
                "done": task_info["future"].done()
            })
        return tasks
    
    def shutdown(self, wait: bool = True):
        """关闭任务管理器"""
        self.executor.shutdown(wait=wait)


class PerformanceProfiler:
    """性能分析器"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.logger = get_logger("performance.profiler")
    
    def profile(self, operation: str):
        """性能分析装饰器"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                import psutil
                import os
                
                # 记录开始状态
                process = psutil.Process(os.getpid())
                start_time = time.time()
                start_memory = process.memory_info().rss
                start_cpu = process.cpu_percent()
                
                try:
                    result = func(*args, **kwargs)
                    
                    # 记录结束状态
                    end_time = time.time()
                    end_memory = process.memory_info().rss
                    end_cpu = process.cpu_percent()
                    
                    # 计算指标
                    duration = end_time - start_time
                    memory_usage = end_memory - start_memory
                    cpu_usage = (start_cpu + end_cpu) / 2
                    
                    # 记录性能指标
                    metrics = PerformanceMetrics(
                        operation=operation,
                        duration=duration,
                        memory_usage=memory_usage,
                        cpu_usage=cpu_usage,
                        cache_hits=0,  # 需要从缓存获取
                        cache_misses=0,  # 需要从缓存获取
                        timestamp=start_time
                    )
                    
                    self.metrics.append(metrics)
                    
                    self.logger.info(
                        f"Performance metrics for {operation}",
                        duration=duration,
                        memory_usage=memory_usage,
                        cpu_usage=cpu_usage
                    )
                    
                    return result
                    
                except Exception as e:
                    self.logger.error(f"Performance profiling failed for {operation}", error=str(e))
                    raise
            
            return wrapper
        return decorator
    
    def get_metrics_summary(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """获取性能指标摘要"""
        filtered_metrics = self.metrics
        if operation:
            filtered_metrics = [m for m in self.metrics if m.operation == operation]
        
        if not filtered_metrics:
            return {}
        
        durations = [m.duration for m in filtered_metrics]
        memory_usages = [m.memory_usage for m in filtered_metrics]
        cpu_usages = [m.cpu_usage for m in filtered_metrics]
        
        return {
            "operation": operation or "all",
            "count": len(filtered_metrics),
            "avg_duration": sum(durations) / len(durations),
            "max_duration": max(durations),
            "min_duration": min(durations),
            "avg_memory": sum(memory_usages) / len(memory_usages),
            "max_memory": max(memory_usages),
            "avg_cpu": sum(cpu_usages) / len(cpu_usages),
            "max_cpu": max(cpu_usages)
        }


def memoize(max_size: int = 128, ttl: Optional[float] = None):
    """记忆化装饰器"""
    def decorator(func: Callable) -> Callable:
        cache = LRUCache(max_size=max_size, ttl=ttl)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            key = hashlib.md5(
                pickle.dumps((args, sorted(kwargs.items())))
            ).hexdigest()
            
            # 尝试从缓存获取
            result = cache.get(key)
            if result is not None:
                return result
            
            # 计算结果并缓存
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result
        
        # 添加缓存管理方法
        wrapper.cache_clear = cache.clear
        wrapper.cache_stats = cache.get_stats
        
        return wrapper
    return decorator


def batch_process(batch_size: int = 10, max_workers: int = 4):
    """批处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(items: List[Any], *args, **kwargs):
            if not items:
                return []
            
            results = []
            
            # 分批处理
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                
                for i in range(0, len(items), batch_size):
                    batch = items[i:i + batch_size]
                    future = executor.submit(func, batch, *args, **kwargs)
                    futures.append(future)
                
                # 收集结果
                for future in as_completed(futures):
                    try:
                        batch_result = future.result()
                        if isinstance(batch_result, list):
                            results.extend(batch_result)
                        else:
                            results.append(batch_result)
                    except Exception as e:
                        logger = get_logger("performance.batch_process")
                        logger.error(f"Batch processing failed", error=str(e))
            
            return results
        
        return wrapper
    return decorator


# 全局性能管理器实例
_cache_manager = None
_memory_pool = None
_task_manager = None
_profiler = None


def get_cache_manager() -> LRUCache:
    """获取缓存管理器"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = LRUCache(max_size=1000, ttl=3600)  # 1小时TTL
    return _cache_manager


def get_memory_pool() -> MemoryPool:
    """获取内存池"""
    global _memory_pool
    if _memory_pool is None:
        _memory_pool = MemoryPool(initial_size=100)
    return _memory_pool


def get_task_manager() -> AsyncTaskManager:
    """获取任务管理器"""
    global _task_manager
    if _task_manager is None:
        _task_manager = AsyncTaskManager(max_workers=10)
    return _task_manager


def get_profiler() -> PerformanceProfiler:
    """获取性能分析器"""
    global _profiler
    if _profiler is None:
        _profiler = PerformanceProfiler()
    return _profiler


def optimize_memory():
    """内存优化"""
    import gc
    
    # 强制垃圾回收
    collected = gc.collect()
    
    logger = get_logger("performance.memory")
    logger.info(f"Memory optimization completed", collected_objects=collected)
    
    return collected


def get_system_performance() -> Dict[str, Any]:
    """获取系统性能状态"""
    import psutil
    
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "cache_stats": get_cache_manager().get_stats(),
        "memory_pool_stats": get_memory_pool().get_stats(),
        "active_tasks": len(get_task_manager().get_active_tasks())
    }
