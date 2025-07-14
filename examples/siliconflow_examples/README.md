# 硅基流动 (SiliconFlow) 集成示例

## 📋 概述

硅基流动是一个提供多种顶级AI模型统一API接口的平台，支持 DeepSeek、Qwen、Claude、GPT 等多种模型。本目录包含了在 TradingAgents-CN 中使用硅基流动的完整示例。

## 🌟 硅基流动优势

### 🎯 多模型支持
- **DeepSeek 系列**: 成本效益高，推理能力强
- **通义千问 系列**: 中文优化，阿里巴巴出品  
- **Claude 系列**: 安全性高，长文本处理
- **GPT 系列**: 通用能力强，多模态支持

### 💰 成本优化
- 统一计费，透明定价
- 支持多种模型的成本对比
- 灵活的用量控制

### 🔧 技术优势
- OpenAI 兼容 API
- 高可用性和稳定性
- 快速响应时间

## 🚀 快速开始

### 1. 获取API密钥

1. 访问 [硅基流动官网](https://siliconflow.cn)
2. 注册账号并完成认证
3. 在控制台获取API密钥

### 2. 设置环境变量

```bash
export SILICONFLOW_API_KEY=your_api_key_here
```

### 3. 基础使用

```python
from tradingagents.llm_adapters.siliconflow_adapter import create_siliconflow_llm
from langchain_core.messages import HumanMessage

# 创建模型实例
llm = create_siliconflow_llm(model="deepseek-chat")

# 发送消息
response = llm.invoke([HumanMessage(content="分析苹果公司的投资价值")])
print(response.content)
```

## 📊 支持的模型

### DeepSeek 系列
- `deepseek-chat`: 通用对话模型，成本效益高
- `deepseek-coder`: 代码专用模型

### 通义千问 系列  
- `qwen-turbo`: 快速响应，适合简单任务
- `qwen-plus`: 平衡性能，适合复杂分析
- `qwen-max`: 最强性能，适合专业分析

### Claude 系列
- `claude-3-haiku`: 快速响应
- `claude-3-sonnet`: 平衡性能和安全性

### GPT 系列
- `gpt-3.5-turbo`: 经典模型，成本优化
- `gpt-4o-mini`: 轻量级版本
- `gpt-4o`: 最新多模态模型

## 📁 示例文件

### `simple_test.py`
基础功能测试，包括：
- 基本对话测试
- 金融分析测试
- 模型对比测试
- 工具调用测试

```bash
python examples/siliconflow_examples/simple_test.py
```

### `demo_siliconflow.py`
完整的股票分析演示，包括：
- 多模型选择
- 股票分析流程
- 实时交互界面

```bash
python examples/siliconflow_examples/demo_siliconflow.py
```

## 🎯 推荐配置

### 成本优化配置
```python
config = {
    "llm_provider": "siliconflow",
    "deep_think_llm": "deepseek-chat",
    "quick_think_llm": "deepseek-chat",
}
```

### 中文优化配置
```python
config = {
    "llm_provider": "siliconflow", 
    "deep_think_llm": "qwen-plus",
    "quick_think_llm": "qwen-turbo",
}
```

### 高质量配置
```python
config = {
    "llm_provider": "siliconflow",
    "deep_think_llm": "claude-3-sonnet", 
    "quick_think_llm": "claude-3-haiku",
}
```

### 多模态配置
```python
config = {
    "llm_provider": "siliconflow",
    "deep_think_llm": "gpt-4o",
    "quick_think_llm": "gpt-4o-mini",
}
```

## 🔧 在TradingAgents中使用

### 基础配置
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 创建硅基流动配置
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "siliconflow"
config["deep_think_llm"] = "deepseek-chat"
config["quick_think_llm"] = "deepseek-chat"

# 初始化TradingAgents
ta = TradingAgentsGraph(debug=True, config=config)

# 运行股票分析
state, decision = ta.propagate("AAPL", "2024-12-20")
print(decision)
```

### 高级配置
```python
# 自定义分析师组合和参数
config = DEFAULT_CONFIG.copy()
config.update({
    "llm_provider": "siliconflow",
    "deep_think_llm": "qwen-plus",
    "quick_think_llm": "qwen-turbo", 
    "max_debate_rounds": 1,  # 减少辩论轮次以降低成本
    "online_tools": True,
})

# 选择特定的分析师
ta = TradingAgentsGraph(
    selected_analysts=["market", "fundamentals"],  # 减少分析师数量
    debug=True,
    config=config
)
```

## 💡 最佳实践

### 1. 模型选择策略
- **成本敏感**: 优先选择 DeepSeek 系列
- **中文场景**: 优先选择 Qwen 系列
- **安全要求**: 优先选择 Claude 系列
- **多模态**: 优先选择 GPT-4o 系列

### 2. 性能优化
```python
# 减少API调用次数
config["max_debate_rounds"] = 1
config["max_risk_discuss_rounds"] = 1

# 选择合适的分析师组合
selected_analysts = ["market", "fundamentals"]
```

### 3. 错误处理
```python
try:
    ta = TradingAgentsGraph(config=config)
    state, decision = ta.propagate("AAPL", "2024-12-20")
except ValueError as e:
    if "SILICONFLOW_API_KEY" in str(e):
        print("请设置硅基流动API密钥")
    else:
        print(f"配置错误: {e}")
```

## 🧪 测试和验证

### 运行集成测试
```bash
python tests/test_siliconflow_integration.py
```

### 运行简单测试
```bash
python examples/siliconflow_examples/simple_test.py
```

### 运行完整演示
```bash
python examples/siliconflow_examples/demo_siliconflow.py
```

## 🔍 故障排除

### 常见问题

1. **API密钥错误**
   ```
   ValueError: 硅基流动 API密钥未找到
   ```
   **解决方案**: 检查环境变量 `SILICONFLOW_API_KEY`

2. **模型不支持**
   ```
   Error: Model not found
   ```
   **解决方案**: 检查模型名称，参考支持的模型列表

3. **网络连接问题**
   ```
   ConnectionError: Failed to connect
   ```
   **解决方案**: 检查网络连接和API服务状态

### 调试模式
```python
# 启用调试模式查看详细信息
config["debug"] = True

# 查看详细日志
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 相关文档

- [硅基流动配置指南](../../docs/configuration/siliconflow-config.md)
- [TradingAgents-CN 文档](../../README.md)
- [硅基流动官方文档](https://docs.siliconflow.cn)

## 🔗 相关链接

- [硅基流动官网](https://siliconflow.cn)
- [API 文档](https://docs.siliconflow.cn)
- [模型定价](https://siliconflow.cn/pricing)
- [GitHub 仓库](https://github.com/hsliuping/TradingAgents-CN)
