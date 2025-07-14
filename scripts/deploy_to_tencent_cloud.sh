#!/bin/bash
# TradingAgents-CN 腾讯云部署更新脚本

set -e  # 遇到错误立即退出

# 配置变量（请根据实际情况修改）
SERVER_IP="your-server-ip"
SERVER_USER="your-username"
SERVER_PATH="/path/to/TradingAgents-CN"
LOCAL_PATH="."

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 开始部署TradingAgents-CN到腾讯云...${NC}"

# 1. 检查本地环境
echo -e "${YELLOW}📋 检查本地环境...${NC}"
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ 未找到requirements.txt文件${NC}"
    exit 1
fi

if [ ! -d "tradingagents" ]; then
    echo -e "${RED}❌ 未找到tradingagents目录${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 本地环境检查通过${NC}"

# 2. 运行本地测试
echo -e "${YELLOW}🧪 运行本地测试...${NC}"
if command -v python3 &> /dev/null; then
    python3 scripts/deployment_readiness_check.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 部署就绪性检查失败${NC}"
        read -p "是否继续部署？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}⚠️ 未找到python3，跳过本地测试${NC}"
fi

# 3. 备份服务器当前版本
echo -e "${YELLOW}💾 备份服务器当前版本...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} "
    cd ${SERVER_PATH}
    if [ -d '.git' ]; then
        git stash push -m 'Auto backup before deployment $(date)'
        echo '✅ Git备份完成'
    else
        cp -r . ../TradingAgents-CN-backup-$(date +%Y%m%d-%H%M%S)
        echo '✅ 文件备份完成'
    fi
"

# 4. 停止当前服务
echo -e "${YELLOW}⏹️ 停止当前服务...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} "
    cd ${SERVER_PATH}
    # 查找并停止Python进程
    pkill -f 'python.*streamlit' || true
    pkill -f 'python.*start_production' || true
    pkill -f 'python.*app.py' || true
    
    # 如果使用Docker
    if [ -f 'docker-compose.yml' ]; then
        docker-compose down || true
    fi
    
    echo '✅ 服务已停止'
"

# 5. 同步代码文件
echo -e "${YELLOW}📤 同步代码文件...${NC}"

# 使用rsync同步，排除不必要的文件
rsync -avz --progress \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='logs/' \
    --exclude='data/' \
    --exclude='cache/' \
    --exclude='.env' \
    --exclude='*.log' \
    --exclude='coverage_report.*' \
    --exclude='system_optimization_report.*' \
    --exclude='deployment_readiness_report.*' \
    ${LOCAL_PATH}/ ${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}/

echo -e "${GREEN}✅ 代码同步完成${NC}"

# 6. 更新服务器环境
echo -e "${YELLOW}🔧 更新服务器环境...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} "
    cd ${SERVER_PATH}
    
    # 更新Python依赖
    echo '📦 更新Python依赖...'
    pip3 install -r requirements.txt
    
    # 创建必要的目录
    mkdir -p logs data cache
    
    # 设置权限
    chmod +x start_production.py
    chmod +x scripts/*.py
    
    echo '✅ 环境更新完成'
"

# 7. 运行部署后检查
echo -e "${YELLOW}🔍 运行部署后检查...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} "
    cd ${SERVER_PATH}
    
    # 检查Python语法
    python3 -m py_compile start_production.py
    
    # 运行部署就绪性检查
    if [ -f 'scripts/deployment_readiness_check.py' ]; then
        python3 scripts/deployment_readiness_check.py
    fi
    
    echo '✅ 部署后检查完成'
"

# 8. 启动服务
echo -e "${YELLOW}🚀 启动服务...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} "
    cd ${SERVER_PATH}
    
    # 方式1: 使用Docker Compose（如果存在）
    if [ -f 'docker-compose.yml' ]; then
        echo '🐳 使用Docker Compose启动...'
        docker-compose up -d
    else
        # 方式2: 直接启动Python应用
        echo '🐍 直接启动Python应用...'
        nohup python3 start_production.py > logs/app.log 2>&1 &
        echo \$! > app.pid
    fi
    
    echo '✅ 服务启动完成'
"

# 9. 健康检查
echo -e "${YELLOW}🏥 进行健康检查...${NC}"
sleep 10  # 等待服务启动

ssh ${SERVER_USER}@${SERVER_IP} "
    cd ${SERVER_PATH}
    
    # 检查进程是否运行
    if [ -f 'app.pid' ]; then
        PID=\$(cat app.pid)
        if ps -p \$PID > /dev/null; then
            echo '✅ 应用进程正在运行 (PID: '\$PID')'
        else
            echo '❌ 应用进程未运行'
            exit 1
        fi
    fi
    
    # 检查端口是否监听
    if netstat -tlnp | grep -q ':8501'; then
        echo '✅ Streamlit端口8501正在监听'
    else
        echo '⚠️ Streamlit端口8501未监听'
    fi
    
    # 如果有健康检查端点，测试它
    if command -v curl &> /dev/null; then
        if curl -f http://localhost:8501 > /dev/null 2>&1; then
            echo '✅ 健康检查通过'
        else
            echo '⚠️ 健康检查失败，但服务可能仍在启动中'
        fi
    fi
"

# 10. 显示部署结果
echo -e "${GREEN}🎉 部署完成！${NC}"
echo -e "${YELLOW}📊 部署摘要:${NC}"
echo "- 服务器: ${SERVER_IP}"
echo "- 部署路径: ${SERVER_PATH}"
echo "- 访问地址: http://${SERVER_IP}:8501"
echo ""
echo -e "${YELLOW}📋 后续操作:${NC}"
echo "1. 访问应用检查功能是否正常"
echo "2. 查看日志: ssh ${SERVER_USER}@${SERVER_IP} 'tail -f ${SERVER_PATH}/logs/app.log'"
echo "3. 监控系统状态"
echo ""
echo -e "${GREEN}✅ 部署脚本执行完成${NC}"
