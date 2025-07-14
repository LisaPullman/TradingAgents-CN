# 硅基流动 (SiliconFlow) 配置指南

## 📋 概述

硅基流动是一个提供多种顶级AI模型统一API接口的平台，支持 DeepSeek、Qwen、Claude、GPT 等多种模型。本指南将帮助您在 TradingAgents-CN 中配置和使用硅基流动。

## 🌟 硅基流动优势

### 🎯 多模型支持
- **DeepSeek 系列**: 成本效益高，推理能力强（V3、R1等）
- **通义千问 系列**: 中文优化，阿里巴巴出品（Qwen2.5系列）
- **GLM 系列**: 清华大学开源模型，中文友好
- **Llama 系列**: Meta开源模型，长文本处理能力强

**注意**: 硅基流动主要支持开源模型，不包括Claude和GPT等闭源模型

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
4. 设置环境变量

```bash
export SILICONFLOW_API_KEY=your_api_key_here
```

### 2. 基础配置

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 创建硅基流动配置
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "siliconflow"
config["deep_think_llm"] = "deepseek-ai/DeepSeek-V3"      # 深度思考模型
config["quick_think_llm"] = "deepseek-ai/DeepSeek-V3"     # 快速任务模型

# 初始化
ta = TradingAgentsGraph(debug=True, config=config)

# 运行分析
state, decision = ta.propagate("AAPL", "2024-12-20")
print(decision)
```

## 🎯 模型选择指南

### 推荐配置组合

#### 1. 成本优化配置
```python
config = {
    "llm_provider": "siliconflow",
    "deep_think_llm": "deepseek-ai/DeepSeek-V3",
    "quick_think_llm": "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
    "max_debate_rounds": 1,
}
```
- **适用场景**: 日常分析，成本敏感
- **特点**: 高性价比，推理能力强

#### 2. 中文优化配置
```python
config = {
    "llm_provider": "siliconflow",
    "deep_think_llm": "Qwen/Qwen2.5-72B-Instruct",
    "quick_think_llm": "Qwen/Qwen2.5-32B-Instruct",
    "max_debate_rounds": 2,
}
```
- **适用场景**: A股分析，中文内容处理
- **特点**: 中文理解优秀，响应快速

#### 3. 推理专用配置
```python
config = {
    "llm_provider": "siliconflow",
    "deep_think_llm": "deepseek-ai/DeepSeek-R1",
    "quick_think_llm": "deepseek-ai/DeepSeek-V3",
    "max_debate_rounds": 2,
}
```
- **适用场景**: 复杂推理，数学计算
- **特点**: 推理能力强，逻辑分析优秀

#### 4. 长文本配置
```python
config = {
    "llm_provider": "siliconflow",
    "deep_think_llm": "meta-llama/Llama-3.1-70B-Instruct",
    "quick_think_llm": "meta-llama/Llama-3.1-8B-Instruct",
    "max_debate_rounds": 2,
}
```
- **适用场景**: 长文本分析，复杂文档处理
- **特点**: 长上下文支持，文本理解能力强

## 📊 支持的模型列表

### DeepSeek 系列
| 模型名称 | 上下文长度 | 工具调用 | 推荐用途 |
|---------|-----------|---------|----------|
| deepseek-ai/DeepSeek-V3 | 64K | ✅ | 通用对话、金融分析、代码分析 |
| deepseek-ai/DeepSeek-R1 | 64K | ✅ | 复杂推理、数学计算、逻辑分析 |
| deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B | 32K | ✅ | 快速推理、成本优化 |

### 通义千问 系列
| 模型名称 | 上下文长度 | 工具调用 | 推荐用途 |
|---------|-----------|---------|----------|
| Qwen/QwQ-32B-Preview | 32K | ✅ | 问答任务、知识查询 |
| Qwen/Qwen2.5-72B-Instruct | 32K | ✅ | 复杂指令、专业任务 |
| Qwen/Qwen2.5-32B-Instruct | 32K | ✅ | 日常任务、中等复杂度分析 |
| Qwen/Qwen2.5-14B-Instruct | 32K | ✅ | 快速任务、成本优化 |

### GLM 系列
| 模型名称 | 上下文长度 | 工具调用 | 推荐用途 |
|---------|-----------|---------|----------|
| THUDM/GLM-4-9B-Chat | 32K | ✅ | 中文对话、学术分析 |

### Meta Llama 系列
| 模型名称 | 上下文长度 | 工具调用 | 推荐用途 |
|---------|-----------|---------|----------|
| meta-llama/Llama-3.1-70B-Instruct | 128K | ✅ | 长文本处理、复杂推理 |
| meta-llama/Llama-3.1-8B-Instruct | 128K | ✅ | 快速任务、资源受限环境 |

## 🔧 高级配置

### 环境变量配置

```bash
# 必需配置
export SILICONFLOW_API_KEY=your_api_key

# 可选配置
export SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1  # 默认值
export SILICONFLOW_TIMEOUT=30                              # 超时设置
export SILICONFLOW_MAX_RETRIES=3                          # 重试次数
```

### 代码配置

```python
from tradingagents.llm_adapters.siliconflow_adapter import ChatSiliconFlow

# 直接使用适配器
llm = ChatSiliconFlow(
    model="deepseek-chat",
    api_key="your_api_key",
    temperature=0.1,
    max_tokens=2000,
    timeout=30
)

# 使用工厂函数
from tradingagents.llm_adapters.openai_compatible_base import create_openai_compatible_llm

llm = create_openai_compatible_llm(
    provider="siliconflow",
    model="qwen-plus",
    temperature=0.1,
    max_tokens=2000
)
```

## 🧪 测试和验证

### 连接测试

```python
from tradingagents.llm_adapters.siliconflow_adapter import test_siliconflow_connection

# 测试连接
if test_siliconflow_connection():
    print("✅ 硅基流动连接成功")
else:
    print("❌ 硅基流动连接失败")
```

### 模型测试

```python
from tradingagents.llm_adapters.siliconflow_adapter import create_siliconflow_llm
from langchain_core.messages import HumanMessage

# 创建模型实例
llm = create_siliconflow_llm(model="deepseek-ai/DeepSeek-V3")

# 发送测试消息
response = llm.invoke([HumanMessage(content="请分析苹果公司的投资价值")])
print(response.content)
```

## 💡 最佳实践

### 1. 模型选择策略
- **成本敏感**: 优先选择 DeepSeek-R1-Distill 或 GLM-4-9B
- **中文场景**: 优先选择 Qwen2.5 系列
- **推理任务**: 优先选择 DeepSeek-R1 或 QwQ-32B
- **长文本**: 优先选择 Llama-3.1 系列
- **通用任务**: 优先选择 DeepSeek-V3

### 2. 性能优化
```python
# 减少辩论轮次以降低成本
config["max_debate_rounds"] = 1
config["max_risk_discuss_rounds"] = 1

# 选择合适的分析师组合
selected_analysts = ["market", "fundamentals"]  # 减少分析师数量
```

### 3. 错误处理
```python
try:
    ta = TradingAgentsGraph(config=config)
    state, decision = ta.propagate("AAPL", "2024-12-20")
except ValueError as e:
    if "SILICONFLOW_API_KEY" in str(e):
        print("❌ 请设置硅基流动API密钥")
    else:
        print(f"❌ 配置错误: {e}")
except Exception as e:
    print(f"❌ 运行错误: {e}")
```

## 🔍 故障排除

### 常见问题

1. **API密钥错误**
   ```
   ValueError: 硅基流动 API密钥未找到
   ```
   **解决方案**: 检查环境变量 `SILICONFLOW_API_KEY` 是否正确设置

2. **模型不支持**
   ```
   Error: Model not found
   ```
   **解决方案**: 检查模型名称是否正确，参考支持的模型列表

3. **网络连接问题**
   ```
   ConnectionError: Failed to connect
   ```
   **解决方案**: 检查网络连接，确认API服务可访问

### 调试模式

```python
# 启用调试模式
config["debug"] = True

# 查看详细日志
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 示例代码

完整的示例代码请参考：
- `examples/siliconflow_examples/demo_siliconflow.py`
- `examples/siliconflow_examples/model_comparison.py`

## 🔗 相关链接

- [硅基流动官网](https://siliconflow.cn)
- [API 文档](https://docs.siliconflow.cn)
- [模型定价](https://siliconflow.cn/pricing)
- [TradingAgents-CN 文档](../README.md)
