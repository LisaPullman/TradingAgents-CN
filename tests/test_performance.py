#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能优化测试
测试缓存、并发处理、内存优化等性能功能
"""

import time
import threading
from pathlib import Path

import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.core.performance import (
    LRUCache, MemoryPool, AsyncTaskManager, PerformanceProfiler,
    memoize, batch_process, optimize_memory, get_system_performance,
    get_cache_manager, get_memory_pool, get_task_manager, get_profiler
)


class TestLRUCache:
    """测试LRU缓存"""
    
    def test_basic_operations(self):
        """测试基本操作"""
        cache = LRUCache(max_size=3)
        
        # 测试设置和获取
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        
        # 测试LRU淘汰
        cache.set("key4", "value4")  # 应该淘汰key1
        assert cache.get("key1") is None
        assert cache.get("key4") == "value4"
        
        print("✅ LRU缓存基本操作测试通过")
    
    def test_ttl(self):
        """测试TTL功能"""
        cache = LRUCache(max_size=10, ttl=0.1)  # 0.1秒TTL
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # 等待TTL过期
        time.sleep(0.15)
        assert cache.get("key1") is None
        
        print("✅ LRU缓存TTL测试通过")
    
    def test_stats(self):
        """测试统计功能"""
        cache = LRUCache(max_size=10)
        
        # 产生一些缓存命中和未命中
        cache.set("key1", "value1")
        cache.get("key1")  # 命中
        cache.get("key2")  # 未命中
        
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["size"] == 1
        
        print("✅ LRU缓存统计测试通过")


class TestMemoryPool:
    """测试内存池"""
    
    def test_acquire_release(self):
        """测试获取和释放"""
        pool = MemoryPool(initial_size=5)
        
        # 获取对象
        obj1 = pool.acquire()
        obj2 = pool.acquire()
        
        assert isinstance(obj1, dict)
        assert isinstance(obj2, dict)
        assert obj1 is not obj2
        
        # 释放对象
        pool.release(obj1)
        pool.release(obj2)
        
        # 再次获取应该重用对象
        obj3 = pool.acquire()
        assert obj3 is obj1 or obj3 is obj2
        
        print("✅ 内存池获取释放测试通过")
    
    def test_stats(self):
        """测试统计功能"""
        pool = MemoryPool(initial_size=3)
        
        initial_stats = pool.get_stats()
        assert initial_stats["available"] == 3
        assert initial_stats["in_use"] == 0
        
        obj = pool.acquire()
        stats_after_acquire = pool.get_stats()
        assert stats_after_acquire["available"] == 2
        assert stats_after_acquire["in_use"] == 1
        
        pool.release(obj)
        stats_after_release = pool.get_stats()
        assert stats_after_release["available"] == 3
        assert stats_after_release["in_use"] == 0
        
        print("✅ 内存池统计测试通过")


class TestAsyncTaskManager:
    """测试异步任务管理器"""
    
    def test_submit_and_get_result(self):
        """测试提交任务和获取结果"""
        manager = AsyncTaskManager(max_workers=2)
        
        def test_function(x, y):
            time.sleep(0.1)  # 模拟耗时操作
            return x + y
        
        # 提交任务
        task_id = manager.submit_task(test_function, 1, 2)
        assert isinstance(task_id, str)
        
        # 获取结果
        result = manager.get_result(task_id, timeout=1.0)
        assert result == 3
        
        manager.shutdown()
        print("✅ 异步任务管理器基本功能测试通过")
    
    def test_multiple_tasks(self):
        """测试多任务处理"""
        manager = AsyncTaskManager(max_workers=3)
        
        def square(x):
            time.sleep(0.05)
            return x * x
        
        # 提交多个任务
        task_ids = []
        for i in range(5):
            task_id = manager.submit_task(square, i)
            task_ids.append(task_id)
        
        # 获取所有结果
        results = []
        for task_id in task_ids:
            result = manager.get_result(task_id, timeout=1.0)
            results.append(result)
        
        expected = [i * i for i in range(5)]
        assert results == expected
        
        manager.shutdown()
        print("✅ 异步任务管理器多任务测试通过")
    
    def test_task_cancellation(self):
        """测试任务取消"""
        manager = AsyncTaskManager(max_workers=1)
        
        def slow_function():
            time.sleep(1.0)
            return "completed"
        
        # 提交任务
        task_id = manager.submit_task(slow_function)
        
        # 立即取消
        cancelled = manager.cancel_task(task_id)
        
        # 注意：已经开始执行的任务可能无法取消
        # 这里主要测试取消机制是否工作
        assert isinstance(cancelled, bool)
        
        manager.shutdown()
        print("✅ 异步任务管理器取消测试通过")


class TestPerformanceProfiler:
    """测试性能分析器"""
    
    def test_profiling_decorator(self):
        """测试性能分析装饰器"""
        profiler = PerformanceProfiler()
        
        @profiler.profile("test_operation")
        def test_function():
            time.sleep(0.1)
            return "result"
        
        result = test_function()
        assert result == "result"
        
        # 检查是否记录了性能指标
        assert len(profiler.metrics) == 1
        metric = profiler.metrics[0]
        assert metric.operation == "test_operation"
        assert metric.duration >= 0.1
        
        print("✅ 性能分析装饰器测试通过")
    
    def test_metrics_summary(self):
        """测试性能指标摘要"""
        profiler = PerformanceProfiler()
        
        @profiler.profile("test_op")
        def test_function(duration):
            time.sleep(duration)
            return "done"
        
        # 执行多次以获得统计数据
        test_function(0.05)
        test_function(0.1)
        test_function(0.15)
        
        summary = profiler.get_metrics_summary("test_op")
        assert summary["count"] == 3
        assert summary["avg_duration"] > 0
        assert summary["max_duration"] >= summary["min_duration"]
        
        print("✅ 性能指标摘要测试通过")


class TestDecorators:
    """测试装饰器"""
    
    def test_memoize_decorator(self):
        """测试记忆化装饰器"""
        call_count = 0
        
        @memoize(max_size=10)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            time.sleep(0.01)  # 模拟耗时计算
            return x * x
        
        # 第一次调用
        result1 = expensive_function(5)
        assert result1 == 25
        assert call_count == 1
        
        # 第二次调用相同参数，应该使用缓存
        result2 = expensive_function(5)
        assert result2 == 25
        assert call_count == 1  # 没有增加
        
        # 不同参数
        result3 = expensive_function(6)
        assert result3 == 36
        assert call_count == 2
        
        # 检查缓存统计
        stats = expensive_function.cache_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 2
        
        print("✅ 记忆化装饰器测试通过")
    
    def test_batch_process_decorator(self):
        """测试批处理装饰器"""
        
        @batch_process(batch_size=3, max_workers=2)
        def process_batch(items):
            # 模拟批处理
            return [item * 2 for item in items]
        
        # 测试数据
        input_data = list(range(10))
        results = process_batch(input_data)
        
        expected = [item * 2 for item in input_data]
        assert sorted(results) == sorted(expected)
        
        print("✅ 批处理装饰器测试通过")


class TestSystemPerformance:
    """测试系统性能"""
    
    def test_memory_optimization(self):
        """测试内存优化"""
        # 创建一些对象
        large_list = [i for i in range(10000)]
        del large_list
        
        # 执行内存优化
        collected = optimize_memory()
        assert isinstance(collected, int)
        assert collected >= 0
        
        print("✅ 内存优化测试通过")
    
    def test_system_performance_metrics(self):
        """测试系统性能指标"""
        metrics = get_system_performance()
        
        required_keys = [
            "cpu_percent", "memory_percent", "disk_usage",
            "cache_stats", "memory_pool_stats", "active_tasks"
        ]
        
        for key in required_keys:
            assert key in metrics
        
        assert isinstance(metrics["cpu_percent"], (int, float))
        assert isinstance(metrics["memory_percent"], (int, float))
        assert isinstance(metrics["cache_stats"], dict)
        
        print("✅ 系统性能指标测试通过")


class TestIntegration:
    """集成测试"""
    
    def test_global_managers(self):
        """测试全局管理器"""
        cache = get_cache_manager()
        pool = get_memory_pool()
        task_manager = get_task_manager()
        profiler = get_profiler()
        
        assert isinstance(cache, LRUCache)
        assert isinstance(pool, MemoryPool)
        assert isinstance(task_manager, AsyncTaskManager)
        assert isinstance(profiler, PerformanceProfiler)
        
        # 测试单例模式
        assert get_cache_manager() is cache
        assert get_memory_pool() is pool
        assert get_task_manager() is task_manager
        assert get_profiler() is profiler
        
        print("✅ 全局管理器测试通过")
    
    def test_performance_workflow(self):
        """测试性能优化工作流"""
        cache = get_cache_manager()
        profiler = get_profiler()
        
        @profiler.profile("workflow_test")
        def workflow_function(data):
            # 检查缓存
            cache_key = f"workflow_{hash(str(data))}"
            result = cache.get(cache_key)
            
            if result is None:
                # 模拟计算
                time.sleep(0.05)
                result = sum(data)
                cache.set(cache_key, result)
            
            return result
        
        # 第一次调用（缓存未命中）
        data = [1, 2, 3, 4, 5]
        result1 = workflow_function(data)
        assert result1 == 15
        
        # 第二次调用（缓存命中）
        result2 = workflow_function(data)
        assert result2 == 15
        
        # 检查性能指标
        assert len(profiler.metrics) >= 2
        
        # 检查缓存统计
        stats = cache.get_stats()
        assert stats["hits"] >= 1
        
        print("✅ 性能优化工作流测试通过")


def run_performance_tests():
    """运行性能优化测试"""
    print("🧪 运行性能优化测试...")
    
    test_classes = [
        TestLRUCache,
        TestMemoryPool,
        TestAsyncTaskManager,
        TestPerformanceProfiler,
        TestDecorators,
        TestSystemPerformance,
        TestIntegration
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n📋 测试类: {test_class.__name__}")
        instance = test_class()
        
        # 获取所有测试方法
        test_methods = [method for method in dir(instance) if method.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(instance, method_name)
                method()
                passed_tests += 1
            except Exception as e:
                print(f"  ❌ {method_name}: {e}")
    
    print(f"\n📊 测试结果: {passed_tests}/{total_tests} 通过")
    return passed_tests == total_tests


def run_tests():
    """运行测试的标准接口"""
    return run_performance_tests()


if __name__ == "__main__":
    success = run_performance_tests()
    sys.exit(0 if success else 1)
