#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腾讯云部署配置更新脚本
帮助用户配置部署参数
"""

import os
import sys
from pathlib import Path

def get_user_input(prompt, default=None):
    """获取用户输入"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()

def update_deploy_script():
    """更新部署脚本配置"""
    print("🔧 配置腾讯云部署参数...")
    print("=" * 50)
    
    # 获取用户输入
    server_ip = get_user_input("腾讯云服务器IP地址")
    server_user = get_user_input("服务器用户名", "root")
    server_path = get_user_input("服务器部署路径", "/opt/TradingAgents-CN")
    
    # 读取部署脚本
    script_path = Path(__file__).parent / "deploy_to_tencent_cloud.sh"
    
    if not script_path.exists():
        print("❌ 部署脚本不存在")
        return False
    
    content = script_path.read_text()
    
    # 替换配置变量
    content = content.replace('SERVER_IP="your-server-ip"', f'SERVER_IP="{server_ip}"')
    content = content.replace('SERVER_USER="your-username"', f'SERVER_USER="{server_user}"')
    content = content.replace('SERVER_PATH="/path/to/TradingAgents-CN"', f'SERVER_PATH="{server_path}"')
    
    # 写回文件
    script_path.write_text(content)
    
    # 设置执行权限
    os.chmod(script_path, 0o755)
    
    print(f"✅ 部署脚本配置完成")
    print(f"   服务器IP: {server_ip}")
    print(f"   用户名: {server_user}")
    print(f"   部署路径: {server_path}")
    
    return True

def create_env_template():
    """创建环境变量模板"""
    print("\n🔧 创建环境变量配置...")
    
    env_template = """# TradingAgents-CN 生产环境配置
# 请根据实际情况修改以下配置

# 运行环境
TRADINGAGENTS_ENV=production
TRADINGAGENTS_LOG_LEVEL=INFO
TRADINGAGENTS_LOG_DIR=./logs

# LLM API配置
OPENAI_API_KEY=your-openai-api-key
SILICONFLOW_API_KEY=your-siliconflow-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
DASHSCOPE_API_KEY=your-dashscope-api-key

# 默认模型配置
DEFAULT_MODEL=deepseek-ai/DeepSeek-V3
MARKET_ANALYST_LLM=deepseek-ai/DeepSeek-V3
NEWS_ANALYST_LLM=deepseek-ai/DeepSeek-V3
TECHNICAL_ANALYST_LLM=deepseek-ai/DeepSeek-V3

# 数据库配置（可选）
TRADINGAGENTS_MONGODB_URL=mongodb://localhost:27017/tradingagents
TRADINGAGENTS_REDIS_URL=redis://localhost:6379

# 缓存配置
TRADINGAGENTS_CACHE_TYPE=memory
TRADINGAGENTS_CACHE_TTL=3600

# 安全配置
TRADINGAGENTS_SECRET_KEY=your-secret-key-here
TRADINGAGENTS_ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Streamlit配置
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
"""
    
    env_file = Path(".env.production")
    env_file.write_text(env_template)
    
    print(f"✅ 环境变量模板已创建: {env_file}")
    print("   请编辑此文件并配置您的API密钥")
    
    return True

def create_deployment_checklist():
    """创建部署检查清单"""
    checklist = """# 🚀 TradingAgents-CN 腾讯云部署检查清单

## 部署前准备

### 1. 服务器环境
- [ ] Python 3.8+ 已安装
- [ ] pip 已安装并更新到最新版本
- [ ] Git 已安装（如果使用Git部署）
- [ ] 防火墙已配置（开放8501端口）

### 2. 依赖服务（可选）
- [ ] Redis 已安装并运行（如果使用Redis缓存）
- [ ] MongoDB 已安装并运行（如果使用数据库）
- [ ] Nginx 已配置（如果使用反向代理）

### 3. 配置文件
- [ ] .env.production 已配置
- [ ] API密钥已设置
- [ ] 数据库连接已配置
- [ ] 日志目录权限已设置

## 部署步骤

### 1. 配置部署脚本
```bash
python scripts/update_deployment_config.py
```

### 2. 运行部署
```bash
chmod +x scripts/deploy_to_tencent_cloud.sh
./scripts/deploy_to_tencent_cloud.sh
```

### 3. 验证部署
- [ ] 访问 http://your-server-ip:8501
- [ ] 检查健康状态
- [ ] 查看应用日志
- [ ] 测试核心功能

## 部署后维护

### 监控检查
- [ ] 系统资源使用率
- [ ] 应用响应时间
- [ ] 错误日志监控
- [ ] API调用频率

### 定期维护
- [ ] 日志文件清理
- [ ] 系统更新
- [ ] 备份数据
- [ ] 性能优化

## 故障排除

### 常见问题
1. **端口被占用**: `netstat -tlnp | grep 8501`
2. **权限问题**: 检查文件和目录权限
3. **依赖缺失**: `pip install -r requirements.txt`
4. **配置错误**: 检查.env文件配置

### 日志位置
- 应用日志: `./logs/tradingagents.log`
- 错误日志: `./logs/tradingagents_error.log`
- 系统日志: `/var/log/syslog`

### 重启服务
```bash
# 停止服务
pkill -f "python.*streamlit"

# 启动服务
nohup python start_production.py > logs/app.log 2>&1 &
```
"""
    
    checklist_file = Path("DEPLOYMENT_CHECKLIST.md")
    checklist_file.write_text(checklist)
    
    print(f"✅ 部署检查清单已创建: {checklist_file}")
    
    return True

def main():
    """主函数"""
    print("🚀 TradingAgents-CN 腾讯云部署配置工具")
    print("=" * 60)
    
    try:
        # 1. 更新部署脚本
        if not update_deploy_script():
            return False
        
        # 2. 创建环境变量模板
        if not create_env_template():
            return False
        
        # 3. 创建部署检查清单
        if not create_deployment_checklist():
            return False
        
        print("\n🎉 配置完成！")
        print("\n📋 下一步操作:")
        print("1. 编辑 .env.production 文件，配置您的API密钥")
        print("2. 确保服务器SSH连接正常")
        print("3. 运行部署脚本: ./scripts/deploy_to_tencent_cloud.sh")
        print("4. 参考 DEPLOYMENT_CHECKLIST.md 进行部署验证")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置失败: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
