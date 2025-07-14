#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里API到硅基流动API迁移脚本
自动化迁移配置和设置
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Dict, List, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class SiliconFlowMigrator:
    """硅基流动迁移器"""
    
    def __init__(self):
        self.project_root = project_root
        self.backup_dir = self.project_root / "backup_before_migration"
        self.migration_log = []
        
    def log(self, message: str, level: str = "INFO"):
        """记录迁移日志"""
        log_entry = f"[{level}] {message}"
        self.migration_log.append(log_entry)
        print(log_entry)
    
    def backup_files(self, files: List[Path]):
        """备份文件"""
        self.log("🔄 开始备份原始文件...")
        
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)
        
        for file_path in files:
            if file_path.exists():
                backup_path = self.backup_dir / file_path.name
                shutil.copy2(file_path, backup_path)
                self.log(f"✅ 已备份: {file_path.name}")
    
    def check_prerequisites(self) -> bool:
        """检查迁移前提条件"""
        self.log("🔍 检查迁移前提条件...")
        
        # 检查硅基流动API密钥
        siliconflow_key = os.getenv('SILICONFLOW_API_KEY')
        if not siliconflow_key:
            self.log("❌ 未找到 SILICONFLOW_API_KEY 环境变量", "ERROR")
            self.log("💡 请先设置: export SILICONFLOW_API_KEY=your_api_key", "INFO")
            return False
        
        self.log(f"✅ 硅基流动API密钥: {siliconflow_key[:10]}...")
        
        # 检查项目文件
        required_files = [
            self.project_root / "tradingagents" / "default_config.py",
            self.project_root / "cli" / "utils.py",
            self.project_root / "config" / "tushare_config.example.env"
        ]
        
        for file_path in required_files:
            if not file_path.exists():
                self.log(f"❌ 缺少必需文件: {file_path}", "ERROR")
                return False
        
        self.log("✅ 所有必需文件存在")
        return True
    
    def migrate_env_file(self):
        """迁移环境变量文件"""
        self.log("🔄 迁移环境变量文件...")
        
        env_file = self.project_root / ".env"
        env_example = self.project_root / "config" / "tushare_config.example.env"
        
        if env_file.exists():
            # 读取现有.env文件
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 添加硅基流动配置
            if 'SILICONFLOW_API_KEY' not in content:
                siliconflow_key = os.getenv('SILICONFLOW_API_KEY', '')
                content += f"\n# 硅基流动API密钥\nSILICONFLOW_API_KEY={siliconflow_key}\n"
            
            # 更新默认提供商
            content = content.replace(
                'DEFAULT_LLM_PROVIDER=dashscope',
                'DEFAULT_LLM_PROVIDER=siliconflow'
            )
            
            # 写回文件
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log("✅ 已更新 .env 文件")
        else:
            self.log("⚠️ 未找到 .env 文件，请手动创建")
    
    def test_siliconflow_connection(self) -> bool:
        """测试硅基流动连接"""
        self.log("🧪 测试硅基流动连接...")
        
        try:
            from tradingagents.llm_adapters.siliconflow_adapter import test_siliconflow_connection
            
            if test_siliconflow_connection():
                self.log("✅ 硅基流动连接测试成功")
                return True
            else:
                self.log("❌ 硅基流动连接测试失败", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ 连接测试异常: {e}", "ERROR")
            return False
    
    def update_user_configs(self):
        """更新用户配置文件"""
        self.log("🔄 更新用户配置文件...")
        
        # 查找用户配置目录
        config_dirs = [
            Path.home() / ".tradingagents",
            Path.home() / "Documents" / "TradingAgents" / "config",
            self.project_root / "user_configs"
        ]
        
        for config_dir in config_dirs:
            if config_dir.exists():
                config_files = list(config_dir.glob("*.json")) + list(config_dir.glob("*.yaml"))
                for config_file in config_files:
                    try:
                        content = config_file.read_text(encoding='utf-8')
                        
                        # 替换配置
                        content = content.replace('"llm_provider": "dashscope"', '"llm_provider": "siliconflow"')
                        content = content.replace('"deep_think_llm": "qwen-plus"', '"deep_think_llm": "deepseek-ai/DeepSeek-V3"')
                        content = content.replace('"quick_think_llm": "qwen-turbo"', '"quick_think_llm": "deepseek-ai/DeepSeek-V3"')
                        
                        config_file.write_text(content, encoding='utf-8')
                        self.log(f"✅ 已更新配置文件: {config_file.name}")
                    except Exception as e:
                        self.log(f"⚠️ 更新配置文件失败 {config_file.name}: {e}", "WARN")
    
    def generate_migration_report(self):
        """生成迁移报告"""
        self.log("📊 生成迁移报告...")
        
        report_content = f"""
# 硅基流动迁移报告

## 迁移时间
{os.popen('date').read().strip()}

## 迁移日志
"""
        
        for log_entry in self.migration_log:
            report_content += f"{log_entry}\n"
        
        report_content += """

## 迁移后配置

### 推荐模型配置
- **通用分析**: deepseek-ai/DeepSeek-V3
- **中文优化**: Qwen/Qwen2.5-72B-Instruct
- **成本优化**: deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B
- **推理任务**: deepseek-ai/DeepSeek-R1

### 使用示例
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 使用硅基流动配置
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "siliconflow"
config["deep_think_llm"] = "deepseek-ai/DeepSeek-V3"
config["quick_think_llm"] = "deepseek-ai/DeepSeek-V3"

# 运行分析
ta = TradingAgentsGraph(debug=True, config=config)
state, decision = ta.propagate("AAPL", "2024-12-20")
```

## 验证步骤
1. 运行测试: `python examples/siliconflow_examples/simple_test.py`
2. 检查配置: `python -c "from tradingagents.default_config import DEFAULT_CONFIG; print(DEFAULT_CONFIG['llm_provider'])"`
3. 运行分析: 使用CLI或Web界面进行股票分析

## 回滚方法
如需回滚到阿里API，请：
1. 恢复备份文件: `cp backup_before_migration/* .`
2. 设置环境变量: `export DEFAULT_LLM_PROVIDER=dashscope`
3. 重启应用

## 支持
如遇问题，请查看:
- 硅基流动配置指南: docs/configuration/siliconflow-config.md
- 示例代码: examples/siliconflow_examples/
- 测试脚本: tests/test_siliconflow_integration.py
"""
        
        report_file = self.project_root / "migration_report.md"
        report_file.write_text(report_content, encoding='utf-8')
        self.log(f"✅ 迁移报告已生成: {report_file}")
    
    def run_migration(self):
        """执行完整迁移"""
        self.log("🚀 开始硅基流动迁移...")
        self.log("=" * 60)
        
        # 检查前提条件
        if not self.check_prerequisites():
            self.log("❌ 迁移前提条件不满足，终止迁移", "ERROR")
            return False
        
        # 备份重要文件
        files_to_backup = [
            self.project_root / ".env",
            self.project_root / "tradingagents" / "default_config.py",
            self.project_root / "cli" / "utils.py"
        ]
        self.backup_files(files_to_backup)
        
        # 测试硅基流动连接
        if not self.test_siliconflow_connection():
            self.log("❌ 硅基流动连接失败，终止迁移", "ERROR")
            return False
        
        # 执行迁移步骤
        self.migrate_env_file()
        self.update_user_configs()
        
        # 生成报告
        self.generate_migration_report()
        
        self.log("=" * 60)
        self.log("🎉 硅基流动迁移完成！")
        self.log("💡 建议运行测试验证: python examples/siliconflow_examples/simple_test.py")
        
        return True


def main():
    """主函数"""
    print("🌟 TradingAgents-CN 硅基流动迁移工具")
    print("=" * 60)
    print("此工具将帮助您从阿里API迁移到硅基流动API")
    print("=" * 60)
    
    # 确认迁移
    confirm = input("\n是否继续迁移？(y/N): ").strip().lower()
    if confirm not in ['y', 'yes', '是']:
        print("❌ 迁移已取消")
        return
    
    # 执行迁移
    migrator = SiliconFlowMigrator()
    success = migrator.run_migration()
    
    if success:
        print("\n🎉 迁移成功完成！")
        print("📋 请查看 migration_report.md 了解详细信息")
    else:
        print("\n❌ 迁移失败，请检查错误信息")
        print("🔄 可以从 backup_before_migration/ 目录恢复原始文件")


if __name__ == "__main__":
    main()
