#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents-CN 系统优化报告生成器
生成完整的系统优化状态报告
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.core.logging_config import get_logger
from tradingagents.core.monitoring import get_monitor
from tradingagents.core.security import get_security_auditor
from tradingagents.core.performance import get_system_performance


def run_test_suite() -> Dict[str, Any]:
    """运行测试套件并收集结果"""
    print("🧪 运行测试套件...")
    
    test_results = {}
    test_files = [
        "test_error_handling.py",
        "test_monitoring_logging.py", 
        "test_core_functionality.py",
        "test_security.py",
        "test_performance.py"
    ]
    
    for test_file in test_files:
        test_path = project_root / "tests" / test_file
        if test_path.exists():
            try:
                # 运行测试
                import subprocess
                result = subprocess.run(
                    [sys.executable, str(test_path)],
                    capture_output=True,
                    text=True,
                    cwd=str(project_root)
                )
                
                test_results[test_file] = {
                    "passed": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr if result.stderr else None
                }
                
            except Exception as e:
                test_results[test_file] = {
                    "passed": False,
                    "output": "",
                    "error": str(e)
                }
        else:
            test_results[test_file] = {
                "passed": False,
                "output": "",
                "error": f"Test file not found: {test_file}"
            }
    
    return test_results


def analyze_code_coverage() -> Dict[str, Any]:
    """分析代码覆盖率"""
    print("📊 分析代码覆盖率...")
    
    try:
        # 运行覆盖率分析
        import subprocess
        result = subprocess.run(
            [sys.executable, "scripts/test_coverage_report.py"],
            capture_output=True,
            text=True,
            cwd=str(project_root)
        )
        
        # 尝试读取JSON报告
        json_report_path = project_root / "coverage_report.json"
        if json_report_path.exists():
            with open(json_report_path, 'r', encoding='utf-8') as f:
                coverage_data = json.load(f)
            return coverage_data
        else:
            return {
                "overall_coverage": 0,
                "total_modules": 0,
                "tested_modules": 0,
                "error": "Coverage report not generated"
            }
            
    except Exception as e:
        return {
            "overall_coverage": 0,
            "total_modules": 0,
            "tested_modules": 0,
            "error": str(e)
        }


def check_security_status() -> Dict[str, Any]:
    """检查安全状态"""
    print("🔒 检查安全状态...")
    
    try:
        auditor = get_security_auditor()
        
        # 检查环境安全
        env_issues = auditor.check_environment_security()
        
        # 获取安全事件摘要
        security_summary = auditor.get_security_summary(hours=24)
        
        return {
            "environment_issues": env_issues,
            "security_events": security_summary,
            "status": "secure" if not env_issues else "issues_found"
        }
        
    except Exception as e:
        return {
            "environment_issues": [],
            "security_events": {},
            "status": "error",
            "error": str(e)
        }


def check_performance_status() -> Dict[str, Any]:
    """检查性能状态"""
    print("⚡ 检查性能状态...")
    
    try:
        performance_data = get_system_performance()
        
        # 性能评级
        cpu_status = "good" if performance_data["cpu_percent"] < 80 else "warning" if performance_data["cpu_percent"] < 95 else "critical"
        memory_status = "good" if performance_data["memory_percent"] < 80 else "warning" if performance_data["memory_percent"] < 95 else "critical"
        
        overall_status = "good"
        if cpu_status == "critical" or memory_status == "critical":
            overall_status = "critical"
        elif cpu_status == "warning" or memory_status == "warning":
            overall_status = "warning"
        
        return {
            "metrics": performance_data,
            "cpu_status": cpu_status,
            "memory_status": memory_status,
            "overall_status": overall_status
        }
        
    except Exception as e:
        return {
            "metrics": {},
            "cpu_status": "unknown",
            "memory_status": "unknown", 
            "overall_status": "error",
            "error": str(e)
        }


def check_monitoring_status() -> Dict[str, Any]:
    """检查监控状态"""
    print("📊 检查监控状态...")
    
    try:
        monitor = get_monitor()
        
        # 获取健康状态
        health_status = monitor.get_health_status()
        
        # 获取系统状态
        system_status = monitor.get_system_status()
        
        return {
            "health_status": health_status,
            "system_status": system_status,
            "monitoring_active": system_status.get("monitoring_active", False)
        }
        
    except Exception as e:
        return {
            "health_status": {},
            "system_status": {},
            "monitoring_active": False,
            "error": str(e)
        }


def generate_optimization_recommendations(report_data: Dict[str, Any]) -> List[str]:
    """生成优化建议"""
    recommendations = []
    
    # 测试相关建议
    test_results = report_data.get("test_results", {})
    failed_tests = [name for name, result in test_results.items() if not result.get("passed", False)]
    if failed_tests:
        recommendations.append(f"修复失败的测试: {', '.join(failed_tests)}")
    
    # 覆盖率相关建议
    coverage = report_data.get("code_coverage", {})
    if coverage.get("overall_coverage", 0) < 70:
        recommendations.append("提高测试覆盖率至70%以上")
    
    # 安全相关建议
    security = report_data.get("security_status", {})
    env_issues = security.get("environment_issues", [])
    if env_issues:
        recommendations.append(f"修复安全问题: {len(env_issues)}个环境安全问题")
    
    # 性能相关建议
    performance = report_data.get("performance_status", {})
    if performance.get("overall_status") == "critical":
        recommendations.append("紧急优化系统性能 - CPU或内存使用率过高")
    elif performance.get("overall_status") == "warning":
        recommendations.append("优化系统性能 - CPU或内存使用率较高")
    
    # 监控相关建议
    monitoring = report_data.get("monitoring_status", {})
    if not monitoring.get("monitoring_active", False):
        recommendations.append("启动系统监控服务")
    
    if not recommendations:
        recommendations.append("系统状态良好，继续保持当前优化水平")
    
    return recommendations


def generate_html_report(report_data: Dict[str, Any], output_path: Path):
    """生成HTML报告"""
    
    # 计算总体评分
    scores = []
    
    # 测试评分 (30%)
    test_results = report_data.get("test_results", {})
    passed_tests = sum(1 for result in test_results.values() if result.get("passed", False))
    total_tests = len(test_results)
    test_score = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    scores.append(test_score * 0.3)
    
    # 覆盖率评分 (25%)
    coverage_score = report_data.get("code_coverage", {}).get("overall_coverage", 0)
    scores.append(coverage_score * 0.25)
    
    # 安全评分 (25%)
    security = report_data.get("security_status", {})
    security_score = 100 if security.get("status") == "secure" else 50
    scores.append(security_score * 0.25)
    
    # 性能评分 (20%)
    performance = report_data.get("performance_status", {})
    perf_status = performance.get("overall_status", "unknown")
    perf_score = {"good": 100, "warning": 70, "critical": 30, "error": 0, "unknown": 50}.get(perf_status, 50)
    scores.append(perf_score * 0.2)
    
    overall_score = sum(scores)
    
    # 生成HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>TradingAgents-CN 系统优化报告</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
            .score {{ font-size: 48px; font-weight: bold; margin: 20px 0; }}
            .score.excellent {{ color: #28a745; }}
            .score.good {{ color: #17a2b8; }}
            .score.warning {{ color: #ffc107; }}
            .score.critical {{ color: #dc3545; }}
            .section {{ margin: 30px 0; padding: 20px; border-radius: 8px; }}
            .section h2 {{ margin-top: 0; color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
            .status-good {{ background-color: #d4edda; border-left: 4px solid #28a745; }}
            .status-warning {{ background-color: #fff3cd; border-left: 4px solid #ffc107; }}
            .status-critical {{ background-color: #f8d7da; border-left: 4px solid #dc3545; }}
            .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #f8f9fa; border-radius: 5px; min-width: 150px; text-align: center; }}
            .recommendations {{ background-color: #e7f3ff; border-left: 4px solid #007bff; }}
            .recommendations ul {{ margin: 10px 0; }}
            .recommendations li {{ margin: 5px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f8f9fa; font-weight: bold; }}
            .test-passed {{ color: #28a745; }}
            .test-failed {{ color: #dc3545; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 TradingAgents-CN 系统优化报告</h1>
                <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <div class="score {'excellent' if overall_score >= 90 else 'good' if overall_score >= 80 else 'warning' if overall_score >= 60 else 'critical'}">{overall_score:.1f}/100</div>
            </div>
    """
    
    # 测试结果部分
    html_content += f"""
            <div class="section">
                <h2>🧪 测试结果</h2>
                <div class="metric">
                    <strong>通过率</strong><br>
                    {passed_tests}/{total_tests} ({test_score:.1f}%)
                </div>
                <table>
                    <tr><th>测试文件</th><th>状态</th><th>说明</th></tr>
    """
    
    for test_name, result in test_results.items():
        status = "✅ 通过" if result.get("passed", False) else "❌ 失败"
        status_class = "test-passed" if result.get("passed", False) else "test-failed"
        error = result.get("error", "")[:100] + "..." if result.get("error", "") and len(result.get("error", "")) > 100 else result.get("error", "")
        
        html_content += f"""
                    <tr>
                        <td>{test_name}</td>
                        <td class="{status_class}">{status}</td>
                        <td>{error or "正常"}</td>
                    </tr>
        """
    
    html_content += """
                </table>
            </div>
    """
    
    # 代码覆盖率部分
    coverage = report_data.get("code_coverage", {})
    html_content += f"""
            <div class="section">
                <h2>📊 代码覆盖率</h2>
                <div class="metric">
                    <strong>整体覆盖率</strong><br>
                    {coverage.get('overall_coverage', 0):.1f}%
                </div>
                <div class="metric">
                    <strong>已测试模块</strong><br>
                    {coverage.get('tested_modules', 0)}/{coverage.get('total_modules', 0)}
                </div>
            </div>
    """
    
    # 安全状态部分
    security = report_data.get("security_status", {})
    security_class = "status-good" if security.get("status") == "secure" else "status-warning"
    html_content += f"""
            <div class="section {security_class}">
                <h2>🔒 安全状态</h2>
                <p><strong>状态:</strong> {security.get('status', 'unknown')}</p>
                <p><strong>环境问题:</strong> {len(security.get('environment_issues', []))} 个</p>
            </div>
    """
    
    # 性能状态部分
    performance = report_data.get("performance_status", {})
    perf_class = f"status-{performance.get('overall_status', 'warning')}"
    metrics = performance.get("metrics", {})
    html_content += f"""
            <div class="section {perf_class}">
                <h2>⚡ 性能状态</h2>
                <div class="metric">
                    <strong>CPU使用率</strong><br>
                    {metrics.get('cpu_percent', 0):.1f}%
                </div>
                <div class="metric">
                    <strong>内存使用率</strong><br>
                    {metrics.get('memory_percent', 0):.1f}%
                </div>
                <div class="metric">
                    <strong>缓存命中率</strong><br>
                    {metrics.get('cache_stats', {}).get('hit_rate', 0):.1f}%
                </div>
            </div>
    """
    
    # 优化建议部分
    recommendations = report_data.get("recommendations", [])
    html_content += f"""
            <div class="section recommendations">
                <h2>💡 优化建议</h2>
                <ul>
    """
    
    for rec in recommendations:
        html_content += f"<li>{rec}</li>"
    
    html_content += """
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def main():
    """主函数"""
    print("🚀 生成TradingAgents-CN系统优化报告...")
    print("=" * 60)
    
    # 收集所有数据
    report_data = {
        "timestamp": time.time(),
        "test_results": run_test_suite(),
        "code_coverage": analyze_code_coverage(),
        "security_status": check_security_status(),
        "performance_status": check_performance_status(),
        "monitoring_status": check_monitoring_status()
    }
    
    # 生成优化建议
    report_data["recommendations"] = generate_optimization_recommendations(report_data)
    
    # 生成报告
    html_output = project_root / "system_optimization_report.html"
    generate_html_report(report_data, html_output)
    
    json_output = project_root / "system_optimization_report.json"
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
    
    # 打印摘要
    print("\n📈 系统优化报告摘要")
    print("=" * 60)
    
    test_results = report_data["test_results"]
    passed_tests = sum(1 for result in test_results.values() if result.get("passed", False))
    total_tests = len(test_results)
    print(f"测试通过率: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    coverage = report_data["code_coverage"]
    print(f"代码覆盖率: {coverage.get('overall_coverage', 0):.1f}%")
    
    security = report_data["security_status"]
    print(f"安全状态: {security.get('status', 'unknown')}")
    
    performance = report_data["performance_status"]
    print(f"性能状态: {performance.get('overall_status', 'unknown')}")
    
    print(f"\n💡 优化建议 ({len(report_data['recommendations'])} 项):")
    for i, rec in enumerate(report_data["recommendations"], 1):
        print(f"  {i}. {rec}")
    
    print(f"\n📄 详细报告已生成:")
    print(f"  HTML: {html_output}")
    print(f"  JSON: {json_output}")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
