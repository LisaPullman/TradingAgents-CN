#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents-CN 部署就绪性检查
全面评估项目是否具备上线部署条件
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class DeploymentChecker:
    """部署就绪性检查器"""
    
    def __init__(self):
        self.project_root = project_root
        self.issues = []
        self.warnings = []
        self.recommendations = []
        self.score = 0
        self.max_score = 0
    
    def add_issue(self, category: str, message: str, severity: str = "high"):
        """添加问题"""
        self.issues.append({
            "category": category,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_warning(self, category: str, message: str):
        """添加警告"""
        self.warnings.append({
            "category": category,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_recommendation(self, category: str, message: str):
        """添加建议"""
        self.recommendations.append({
            "category": category,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def check_score(self, points: int, condition: bool, category: str, success_msg: str, fail_msg: str):
        """检查并计分"""
        self.max_score += points
        if condition:
            self.score += points
            print(f"✅ {success_msg}")
        else:
            print(f"❌ {fail_msg}")
            self.add_issue(category, fail_msg)
    
    def check_dependencies(self) -> Dict[str, Any]:
        """检查依赖项"""
        print("\n🔍 检查依赖项...")
        
        # 检查requirements.txt
        req_file = self.project_root / "requirements.txt"
        self.check_score(5, req_file.exists(), "dependencies", 
                        "requirements.txt 文件存在", "缺少 requirements.txt 文件")
        
        # 检查关键依赖
        critical_deps = [
            "langchain", "langgraph", "openai", "requests", 
            "pandas", "numpy", "python-dotenv"
        ]
        
        if req_file.exists():
            content = req_file.read_text()
            missing_deps = [dep for dep in critical_deps if dep not in content.lower()]
            
            self.check_score(10, len(missing_deps) == 0, "dependencies",
                           "所有关键依赖项已定义", f"缺少关键依赖: {missing_deps}")
        
        # 检查Python版本兼容性
        python_version = sys.version_info
        self.check_score(5, python_version >= (3, 8), "dependencies",
                        f"Python版本兼容 ({python_version.major}.{python_version.minor})",
                        f"Python版本过低 ({python_version.major}.{python_version.minor}), 建议3.8+")
        
        return {"score": 20, "max_score": 20}
    
    def check_configuration(self) -> Dict[str, Any]:
        """检查配置管理"""
        print("\n⚙️ 检查配置管理...")
        
        # 检查环境变量配置
        env_example = self.project_root / ".env.example"
        env_file = self.project_root / ".env"
        
        self.check_score(5, env_example.exists(), "configuration",
                        ".env.example 文件存在", "缺少 .env.example 文件")
        
        # 检查配置文件
        config_files = [
            "tradingagents/default_config.py",
            "tradingagents/config/config_manager.py"
        ]
        
        existing_configs = sum(1 for f in config_files if (self.project_root / f).exists())
        self.check_score(10, existing_configs >= 1, "configuration",
                        "配置管理文件存在", "缺少配置管理文件")
        
        # 检查敏感信息
        if env_file.exists():
            content = env_file.read_text()
            if "your_api_key_here" in content or "placeholder" in content.lower():
                self.add_warning("configuration", "环境变量文件包含占位符，需要配置真实值")
        
        return {"score": 15, "max_score": 15}
    
    def check_security(self) -> Dict[str, Any]:
        """检查安全性"""
        print("\n🔒 检查安全性...")
        
        # 检查安全模块
        security_file = self.project_root / "tradingagents/core/security.py"
        self.check_score(10, security_file.exists(), "security",
                        "安全模块已实现", "缺少安全模块")
        
        # 检查敏感文件是否被忽略
        gitignore = self.project_root / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            sensitive_patterns = [".env", "*.key", "secrets", "__pycache__"]
            ignored_patterns = sum(1 for pattern in sensitive_patterns if pattern in content)
            
            self.check_score(5, ignored_patterns >= 3, "security",
                           "敏感文件已被Git忽略", "部分敏感文件可能未被忽略")
        else:
            self.add_issue("security", "缺少 .gitignore 文件")
        
        # 检查硬编码密钥
        self.check_hardcoded_secrets()
        
        return {"score": 15, "max_score": 15}
    
    def check_hardcoded_secrets(self):
        """检查硬编码密钥"""
        secret_patterns = [
            r"sk-[a-zA-Z0-9]{48}",  # OpenAI API keys
            r"['\"][a-zA-Z0-9]{32,}['\"]",  # Generic long strings
            r"password\s*=\s*['\"][^'\"]+['\"]",  # Passwords
        ]
        
        python_files = list(self.project_root.rglob("*.py"))
        issues_found = 0
        
        for file_path in python_files:
            if "test" in str(file_path) or "__pycache__" in str(file_path):
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8')
                for pattern in secret_patterns:
                    import re
                    if re.search(pattern, content):
                        issues_found += 1
                        self.add_warning("security", f"可能的硬编码密钥: {file_path}")
                        break
            except:
                continue
        
        self.check_score(5, issues_found == 0, "security",
                        "未发现硬编码密钥", f"发现 {issues_found} 个可能的硬编码密钥")
    
    def check_error_handling(self) -> Dict[str, Any]:
        """检查错误处理"""
        print("\n🛡️ 检查错误处理...")
        
        # 检查异常处理模块
        exception_file = self.project_root / "tradingagents/core/exceptions.py"
        self.check_score(10, exception_file.exists(), "error_handling",
                        "异常处理模块已实现", "缺少异常处理模块")
        
        # 检查装饰器
        decorator_file = self.project_root / "tradingagents/core/decorators.py"
        self.check_score(5, decorator_file.exists(), "error_handling",
                        "错误处理装饰器已实现", "缺少错误处理装饰器")
        
        # 检查日志配置
        logging_file = self.project_root / "tradingagents/core/logging_config.py"
        self.check_score(5, logging_file.exists(), "error_handling",
                        "日志配置已实现", "缺少日志配置")
        
        return {"score": 20, "max_score": 20}
    
    def check_monitoring(self) -> Dict[str, Any]:
        """检查监控能力"""
        print("\n📊 检查监控能力...")
        
        # 检查监控模块
        monitoring_file = self.project_root / "tradingagents/core/monitoring.py"
        self.check_score(10, monitoring_file.exists(), "monitoring",
                        "监控模块已实现", "缺少监控模块")
        
        # 检查性能监控
        performance_file = self.project_root / "tradingagents/core/performance.py"
        self.check_score(5, performance_file.exists(), "monitoring",
                        "性能监控已实现", "缺少性能监控")
        
        return {"score": 15, "max_score": 15}
    
    def check_testing(self) -> Dict[str, Any]:
        """检查测试覆盖"""
        print("\n🧪 检查测试覆盖...")
        
        # 检查测试目录
        test_dir = self.project_root / "tests"
        self.check_score(5, test_dir.exists(), "testing",
                        "测试目录存在", "缺少测试目录")
        
        # 检查测试文件
        if test_dir.exists():
            test_files = list(test_dir.glob("test_*.py"))
            self.check_score(10, len(test_files) >= 3, "testing",
                           f"测试文件充足 ({len(test_files)} 个)", "测试文件不足")
        
        # 运行测试
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", "--tb=short", "-v"
            ], cwd=self.project_root, capture_output=True, text=True, timeout=60)
            
            self.check_score(10, result.returncode == 0, "testing",
                           "所有测试通过", "部分测试失败")
        except:
            self.add_warning("testing", "无法运行pytest，尝试手动测试")
            # 尝试运行我们的测试框架
            try:
                result = subprocess.run([
                    sys.executable, "tests/test_framework.py"
                ], cwd=self.project_root, capture_output=True, text=True, timeout=60)
                
                self.check_score(10, result.returncode == 0, "testing",
                               "测试框架运行成功", "测试框架运行失败")
            except:
                self.add_issue("testing", "无法运行测试")
        
        return {"score": 25, "max_score": 25}
    
    def check_documentation(self) -> Dict[str, Any]:
        """检查文档"""
        print("\n📚 检查文档...")
        
        # 检查README
        readme_files = ["README.md", "README.rst", "README.txt"]
        has_readme = any((self.project_root / f).exists() for f in readme_files)
        self.check_score(5, has_readme, "documentation",
                        "README文件存在", "缺少README文件")
        
        # 检查API文档
        docs_dir = self.project_root / "docs"
        self.check_score(3, docs_dir.exists(), "documentation",
                        "文档目录存在", "建议添加docs目录")
        
        # 检查代码注释
        python_files = list(self.project_root.rglob("*.py"))
        documented_files = 0
        
        for file_path in python_files:
            if "test" in str(file_path) or "__pycache__" in str(file_path):
                continue
            try:
                content = file_path.read_text(encoding='utf-8')
                if '"""' in content or "'''" in content:
                    documented_files += 1
            except:
                continue
        
        doc_ratio = documented_files / max(len(python_files), 1)
        self.check_score(7, doc_ratio >= 0.5, "documentation",
                        f"代码文档充足 ({doc_ratio:.1%})", f"代码文档不足 ({doc_ratio:.1%})")
        
        return {"score": 15, "max_score": 15}
    
    def check_deployment_files(self) -> Dict[str, Any]:
        """检查部署文件"""
        print("\n🚀 检查部署文件...")
        
        # 检查Docker支持
        dockerfile = self.project_root / "Dockerfile"
        docker_compose = self.project_root / "docker-compose.yml"
        
        has_docker = dockerfile.exists() or docker_compose.exists()
        if has_docker:
            self.check_score(5, True, "deployment", "Docker配置存在", "")
        else:
            self.add_recommendation("deployment", "建议添加Docker配置以简化部署")
        
        # 检查启动脚本
        startup_scripts = ["start.sh", "run.py", "main.py", "app.py"]
        has_startup = any((self.project_root / f).exists() for f in startup_scripts)
        self.check_score(5, has_startup, "deployment",
                        "启动脚本存在", "缺少启动脚本")
        
        # 检查健康检查端点
        health_files = list(self.project_root.rglob("*health*"))
        has_health_check = len(health_files) > 0
        if has_health_check:
            self.check_score(3, True, "deployment", "健康检查已实现", "")
        else:
            self.add_recommendation("deployment", "建议添加健康检查端点")
        
        return {"score": 10, "max_score": 13}
    
    def check_scalability(self) -> Dict[str, Any]:
        """检查可扩展性"""
        print("\n📈 检查可扩展性...")
        
        # 检查异步支持
        async_files = []
        for file_path in self.project_root.rglob("*.py"):
            try:
                content = file_path.read_text(encoding='utf-8')
                if "async def" in content or "await " in content:
                    async_files.append(file_path)
            except:
                continue
        
        self.check_score(5, len(async_files) > 0, "scalability",
                        f"异步支持已实现 ({len(async_files)} 个文件)", "缺少异步支持")
        
        # 检查缓存机制
        cache_files = list(self.project_root.rglob("*cache*"))
        self.check_score(5, len(cache_files) > 0, "scalability",
                        "缓存机制已实现", "缺少缓存机制")
        
        # 检查数据库连接池
        db_files = list(self.project_root.rglob("*database*")) + list(self.project_root.rglob("*db*"))
        if db_files:
            self.check_score(3, True, "scalability", "数据库支持已实现", "")
        else:
            self.add_recommendation("scalability", "考虑添加数据库支持以提高可扩展性")
        
        return {"score": 10, "max_score": 13}
    
    def check_production_readiness(self) -> Dict[str, Any]:
        """检查生产就绪性"""
        print("\n🏭 检查生产就绪性...")
        
        # 检查环境区分
        config_files = list(self.project_root.rglob("*config*"))
        has_env_config = any("env" in str(f).lower() for f in config_files)
        self.check_score(5, has_env_config, "production",
                        "环境配置已区分", "缺少环境配置区分")
        
        # 检查资源限制
        resource_files = list(self.project_root.rglob("*resource*")) + list(self.project_root.rglob("*limit*"))
        if resource_files:
            self.check_score(3, True, "production", "资源限制已配置", "")
        else:
            self.add_recommendation("production", "建议配置资源限制")
        
        # 检查优雅关闭
        signal_handling = False
        for file_path in self.project_root.rglob("*.py"):
            try:
                content = file_path.read_text(encoding='utf-8')
                if "signal" in content and ("SIGTERM" in content or "SIGINT" in content):
                    signal_handling = True
                    break
            except:
                continue
        
        if signal_handling:
            self.check_score(2, True, "production", "优雅关闭已实现", "")
        else:
            self.add_recommendation("production", "建议实现优雅关闭机制")
        
        return {"score": 7, "max_score": 10}
    
    def generate_report(self) -> Dict[str, Any]:
        """生成检查报告"""
        print(f"\n📊 部署就绪性评估完成")
        print("=" * 60)
        
        # 计算总分
        total_score = self.score
        total_max_score = self.max_score
        percentage = (total_score / total_max_score * 100) if total_max_score > 0 else 0
        
        # 确定就绪等级
        if percentage >= 90:
            readiness_level = "生产就绪"
            readiness_color = "🟢"
        elif percentage >= 80:
            readiness_level = "基本就绪"
            readiness_color = "🟡"
        elif percentage >= 60:
            readiness_level = "需要改进"
            readiness_color = "🟠"
        else:
            readiness_level = "不建议部署"
            readiness_color = "🔴"
        
        print(f"总体评分: {total_score}/{total_max_score} ({percentage:.1f}%)")
        print(f"就绪等级: {readiness_color} {readiness_level}")
        
        # 统计问题
        critical_issues = [i for i in self.issues if i["severity"] == "high"]
        medium_issues = [i for i in self.issues if i["severity"] == "medium"]
        
        print(f"\n问题统计:")
        print(f"  严重问题: {len(critical_issues)} 个")
        print(f"  一般问题: {len(medium_issues)} 个")
        print(f"  警告: {len(self.warnings)} 个")
        print(f"  建议: {len(self.recommendations)} 个")
        
        # 生成报告数据
        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_score": total_score,
            "max_score": total_max_score,
            "percentage": percentage,
            "readiness_level": readiness_level,
            "issues": self.issues,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "deployment_ready": percentage >= 80
        }
        
        return report
    
    def run_full_check(self) -> Dict[str, Any]:
        """运行完整检查"""
        print("🔍 开始TradingAgents-CN部署就绪性检查...")
        print("=" * 60)
        
        # 执行各项检查
        self.check_dependencies()
        self.check_configuration()
        self.check_security()
        self.check_error_handling()
        self.check_monitoring()
        self.check_testing()
        self.check_documentation()
        self.check_deployment_files()
        self.check_scalability()
        self.check_production_readiness()
        
        # 生成报告
        return self.generate_report()


def main():
    """主函数"""
    checker = DeploymentChecker()
    report = checker.run_full_check()
    
    # 保存报告
    report_file = project_root / "deployment_readiness_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 详细报告已保存: {report_file}")
    
    # 输出关键问题
    if report["issues"]:
        print(f"\n❌ 需要解决的问题:")
        for issue in report["issues"]:
            print(f"  [{issue['category']}] {issue['message']}")
    
    if report["warnings"]:
        print(f"\n⚠️ 警告:")
        for warning in report["warnings"]:
            print(f"  [{warning['category']}] {warning['message']}")
    
    if report["recommendations"]:
        print(f"\n💡 建议:")
        for rec in report["recommendations"]:
            print(f"  [{rec['category']}] {rec['message']}")
    
    return report["deployment_ready"]


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
