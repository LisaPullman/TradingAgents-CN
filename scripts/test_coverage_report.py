#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试覆盖率报告生成器
分析代码覆盖率并生成详细报告
"""

import os
import sys
import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Any
from dataclasses import dataclass, asdict


@dataclass
class ModuleCoverage:
    """模块覆盖率信息"""
    name: str
    path: str
    total_functions: int
    tested_functions: int
    total_classes: int
    tested_classes: int
    coverage_percentage: float
    missing_tests: List[str]


@dataclass
class CoverageReport:
    """覆盖率报告"""
    total_modules: int
    tested_modules: int
    overall_coverage: float
    module_coverage: List[ModuleCoverage]
    recommendations: List[str]


class CodeAnalyzer:
    """代码分析器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.source_dirs = [
            "tradingagents/core",
            "tradingagents/agents",
            "tradingagents/dataflows",
            "tradingagents/llm_adapters",
            "tradingagents/graph"
        ]
    
    def analyze_module(self, module_path: Path) -> Dict[str, Any]:
        """分析单个模块"""
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_'):  # 排除私有函数
                        functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                    # 添加类中的公共方法
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and not item.name.startswith('_'):
                            functions.append(f"{node.name}.{item.name}")
            
            return {
                "functions": functions,
                "classes": classes,
                "total_functions": len(functions),
                "total_classes": len(classes)
            }
        
        except Exception as e:
            print(f"分析模块失败 {module_path}: {e}")
            return {
                "functions": [],
                "classes": [],
                "total_functions": 0,
                "total_classes": 0
            }
    
    def find_python_files(self) -> List[Path]:
        """查找Python文件"""
        python_files = []
        
        for source_dir in self.source_dirs:
            dir_path = self.project_root / source_dir
            if dir_path.exists():
                for py_file in dir_path.rglob("*.py"):
                    if py_file.name != "__init__.py":
                        python_files.append(py_file)
        
        return python_files


class TestAnalyzer:
    """测试分析器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_dir = project_root / "tests"
    
    def find_test_files(self) -> List[Path]:
        """查找测试文件"""
        test_files = []
        
        if self.test_dir.exists():
            for test_file in self.test_dir.glob("test_*.py"):
                test_files.append(test_file)
        
        return test_files
    
    def analyze_test_file(self, test_path: Path) -> Dict[str, Any]:
        """分析测试文件"""
        try:
            with open(test_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            test_functions = []
            test_classes = []
            tested_modules = set()
            
            # 查找导入的模块
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith('tradingagents'):
                            tested_modules.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module.startswith('tradingagents'):
                        tested_modules.add(node.module)
                elif isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_'):
                        test_functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    if node.name.startswith('Test'):
                        test_classes.append(node.name)
                        # 添加测试类中的测试方法
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                                test_functions.append(f"{node.name}.{item.name}")
            
            return {
                "test_functions": test_functions,
                "test_classes": test_classes,
                "tested_modules": list(tested_modules),
                "total_tests": len(test_functions)
            }
        
        except Exception as e:
            print(f"分析测试文件失败 {test_path}: {e}")
            return {
                "test_functions": [],
                "test_classes": [],
                "tested_modules": [],
                "total_tests": 0
            }


class CoverageAnalyzer:
    """覆盖率分析器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.code_analyzer = CodeAnalyzer(project_root)
        self.test_analyzer = TestAnalyzer(project_root)
    
    def generate_report(self) -> CoverageReport:
        """生成覆盖率报告"""
        # 分析源代码
        python_files = self.code_analyzer.find_python_files()
        code_analysis = {}
        
        for py_file in python_files:
            relative_path = py_file.relative_to(self.project_root)
            module_name = str(relative_path).replace('/', '.').replace('.py', '')
            code_analysis[module_name] = self.code_analyzer.analyze_module(py_file)
            code_analysis[module_name]['path'] = str(relative_path)
        
        # 分析测试
        test_files = self.test_analyzer.find_test_files()
        test_analysis = {}
        all_tested_modules = set()
        
        for test_file in test_files:
            test_name = test_file.stem
            test_analysis[test_name] = self.test_analyzer.analyze_test_file(test_file)
            all_tested_modules.update(test_analysis[test_name]['tested_modules'])
        
        # 计算覆盖率
        module_coverage = []
        total_functions = 0
        tested_functions = 0
        
        for module_name, analysis in code_analysis.items():
            is_tested = any(module_name in tested_modules for tested_modules in all_tested_modules)
            
            # 简单的启发式：如果模块被导入，假设50%的函数被测试
            tested_func_count = int(analysis['total_functions'] * 0.5) if is_tested else 0
            tested_class_count = int(analysis['total_classes'] * 0.5) if is_tested else 0
            
            coverage_pct = (tested_func_count / analysis['total_functions'] * 100) if analysis['total_functions'] > 0 else 100
            
            missing_tests = []
            if not is_tested:
                missing_tests.append(f"整个模块 {module_name} 缺少测试")
            elif coverage_pct < 80:
                missing_tests.append(f"模块 {module_name} 测试覆盖率不足")
            
            module_cov = ModuleCoverage(
                name=module_name,
                path=analysis['path'],
                total_functions=analysis['total_functions'],
                tested_functions=tested_func_count,
                total_classes=analysis['total_classes'],
                tested_classes=tested_class_count,
                coverage_percentage=coverage_pct,
                missing_tests=missing_tests
            )
            
            module_coverage.append(module_cov)
            total_functions += analysis['total_functions']
            tested_functions += tested_func_count
        
        # 计算整体覆盖率
        overall_coverage = (tested_functions / total_functions * 100) if total_functions > 0 else 0
        tested_modules_count = sum(1 for mc in module_coverage if mc.tested_functions > 0)
        
        # 生成建议
        recommendations = self._generate_recommendations(module_coverage, test_analysis)
        
        return CoverageReport(
            total_modules=len(module_coverage),
            tested_modules=tested_modules_count,
            overall_coverage=overall_coverage,
            module_coverage=module_coverage,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, module_coverage: List[ModuleCoverage], test_analysis: Dict) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 检查未测试的模块
        untested_modules = [mc for mc in module_coverage if mc.tested_functions == 0]
        if untested_modules:
            recommendations.append(f"创建测试文件覆盖 {len(untested_modules)} 个未测试模块")
        
        # 检查覆盖率低的模块
        low_coverage_modules = [mc for mc in module_coverage if 0 < mc.coverage_percentage < 50]
        if low_coverage_modules:
            recommendations.append(f"提高 {len(low_coverage_modules)} 个模块的测试覆盖率")
        
        # 检查测试文件数量
        if len(test_analysis) < 5:
            recommendations.append("增加更多测试文件以提高覆盖率")
        
        # 检查核心模块
        core_modules = [mc for mc in module_coverage if 'core' in mc.name]
        untested_core = [mc for mc in core_modules if mc.tested_functions == 0]
        if untested_core:
            recommendations.append("优先为核心模块添加测试")
        
        return recommendations


def generate_html_report(report: CoverageReport, output_path: Path):
    """生成HTML报告"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>TradingAgents-CN 测试覆盖率报告</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .summary {{ margin: 20px 0; }}
            .module {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
            .high-coverage {{ background-color: #d4edda; }}
            .medium-coverage {{ background-color: #fff3cd; }}
            .low-coverage {{ background-color: #f8d7da; }}
            .recommendations {{ background-color: #e7f3ff; padding: 15px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>TradingAgents-CN 测试覆盖率报告</h1>
            <p>生成时间: {os.popen('date').read().strip()}</p>
        </div>
        
        <div class="summary">
            <h2>📊 总体统计</h2>
            <p><strong>总模块数:</strong> {report.total_modules}</p>
            <p><strong>已测试模块:</strong> {report.tested_modules}</p>
            <p><strong>整体覆盖率:</strong> {report.overall_coverage:.1f}%</p>
        </div>
        
        <div class="recommendations">
            <h2>💡 改进建议</h2>
            <ul>
    """
    
    for rec in report.recommendations:
        html_content += f"<li>{rec}</li>"
    
    html_content += """
            </ul>
        </div>
        
        <h2>📋 模块详情</h2>
    """
    
    for module in sorted(report.module_coverage, key=lambda x: x.coverage_percentage, reverse=True):
        css_class = "high-coverage" if module.coverage_percentage >= 80 else \
                   "medium-coverage" if module.coverage_percentage >= 50 else "low-coverage"
        
        html_content += f"""
        <div class="module {css_class}">
            <h3>{module.name}</h3>
            <p><strong>路径:</strong> {module.path}</p>
            <p><strong>函数:</strong> {module.tested_functions}/{module.total_functions} 
               ({module.coverage_percentage:.1f}%)</p>
            <p><strong>类:</strong> {module.tested_classes}/{module.total_classes}</p>
        """
        
        if module.missing_tests:
            html_content += "<p><strong>缺失测试:</strong></p><ul>"
            for missing in module.missing_tests:
                html_content += f"<li>{missing}</li>"
            html_content += "</ul>"
        
        html_content += "</div>"
    
    html_content += """
    </body>
    </html>
    """
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def main():
    """主函数"""
    print("📊 生成TradingAgents-CN测试覆盖率报告...")
    
    project_root = Path(__file__).parent.parent
    analyzer = CoverageAnalyzer(project_root)
    
    # 生成报告
    report = analyzer.generate_report()
    
    # 打印控制台报告
    print(f"\n📈 测试覆盖率报告")
    print("=" * 50)
    print(f"总模块数: {report.total_modules}")
    print(f"已测试模块: {report.tested_modules}")
    print(f"整体覆盖率: {report.overall_coverage:.1f}%")
    
    print(f"\n💡 改进建议:")
    for i, rec in enumerate(report.recommendations, 1):
        print(f"  {i}. {rec}")
    
    print(f"\n📋 模块覆盖率详情:")
    for module in sorted(report.module_coverage, key=lambda x: x.coverage_percentage, reverse=True):
        status = "🟢" if module.coverage_percentage >= 80 else \
                "🟡" if module.coverage_percentage >= 50 else "🔴"
        print(f"  {status} {module.name}: {module.coverage_percentage:.1f}% "
              f"({module.tested_functions}/{module.total_functions} 函数)")
    
    # 生成HTML报告
    html_output = project_root / "coverage_report.html"
    generate_html_report(report, html_output)
    print(f"\n📄 HTML报告已生成: {html_output}")
    
    # 生成JSON报告
    json_output = project_root / "coverage_report.json"
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(asdict(report), f, ensure_ascii=False, indent=2)
    print(f"📄 JSON报告已生成: {json_output}")
    
    return report.overall_coverage >= 70  # 70%覆盖率为通过标准


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
