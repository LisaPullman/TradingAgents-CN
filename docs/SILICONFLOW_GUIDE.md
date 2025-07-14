# 🚀 硅基流动集成指南

## 📖 简介

硅基流动是TradingAgents-CN的**首选LLM服务提供商**，提供70+主流模型的统一API接口，具有超高性价比和国内直连优势。

## 🌟 为什么选择硅基流动？

### 💰 成本优势
- **DeepSeek-V3**: ¥0.14/百万tokens (官方价格的1/10)
- **Qwen2.5-72B**: ¥1.26/百万tokens (阿里云的1/5)
- **Claude-3.5-Sonnet**: ¥21/百万tokens (官方价格的30%)
- **GPT-4o**: ¥105/百万tokens (OpenAI官方的50%)

### 🚀 技术优势
- **统一接口**: 一个API密钥访问70+模型
- **国内直连**: 无需科学上网，稳定快速
- **企业级SLA**: 99.9%可用性保障
- **实时监控**: 详细的用量统计和成本分析

### 🎯 模型丰富度
- **推理专用**: DeepSeek-V3, DeepSeek-R1, QwQ-32B
- **通用对话**: Qwen2.5-72B, Llama-3.1-70B
- **代码生成**: DeepSeek-Coder, CodeLlama
- **多模态**: Qwen-VL, LLaVA
- **国际模型**: Claude-3.5, GPT-4o, Gemini

## 🔧 快速开始

### 1. 注册账号

1. 访问 [硅基流动官网](https://siliconflow.cn/)
2. 点击"立即注册"
3. 使用手机号或邮箱注册
4. 完成手机验证

### 2. 实名认证

1. 登录控制台
2. 进入"账户设置" -> "实名认证"
3. 选择个人或企业认证
4. 上传身份证件照片
5. 等待审核（通常1-2小时）

### 3. 获取API密钥

1. 进入"API管理" -> "密钥管理"
2. 点击"创建新密钥"
3. 设置密钥名称和权限
4. 复制生成的API密钥
5. **妥善保存密钥**（只显示一次）

### 4. 充值账户

1. 进入"财务管理" -> "充值"
2. 选择充值金额（最低10元）
3. 支持微信、支付宝、银行卡
4. 充值后即可使用API

## ⚙️ 配置TradingAgents-CN

### 环境变量配置

编辑 `.env` 文件：

```bash
# 硅基流动API配置（必需）
SILICONFLOW_API_KEY=sk-your-siliconflow-api-key-here

# 推荐的模型配置
DEFAULT_MODEL=deepseek-ai/DeepSeek-V3              # 默认模型：超高性价比
MARKET_ANALYST_LLM=Qwen/Qwen2.5-72B-Instruct      # 市场分析：推理能力强
NEWS_ANALYST_LLM=deepseek-ai/DeepSeek-R1           # 新闻分析：逻辑推理专用
TECHNICAL_ANALYST_LLM=Qwen/Qwen2.5-72B-Instruct   # 技术分析：数据分析能力强
FUNDAMENTALS_ANALYST_LLM=Qwen/Qwen2.5-72B-Instruct # 基本面：综合分析能力
RISK_MANAGER_LLM=deepseek-ai/DeepSeek-V3           # 风险管理：成本控制

# LLM提供商优先级
LLM_PROVIDER=siliconflow
```

### 模型选择建议

#### 🏆 推荐配置（性价比最高）

```bash
# 经济型配置 - 成本最低
DEFAULT_MODEL=deepseek-ai/DeepSeek-V3
MARKET_ANALYST_LLM=deepseek-ai/DeepSeek-V3
NEWS_ANALYST_LLM=deepseek-ai/DeepSeek-V3
TECHNICAL_ANALYST_LLM=deepseek-ai/DeepSeek-V3
FUNDAMENTALS_ANALYST_LLM=deepseek-ai/DeepSeek-V3
RISK_MANAGER_LLM=deepseek-ai/DeepSeek-V3

# 预估成本：¥0.01-0.05/次分析
```

#### 🎯 平衡配置（推理能力强）

```bash
# 平衡型配置 - 性能与成本兼顾
DEFAULT_MODEL=Qwen/Qwen2.5-72B-Instruct
MARKET_ANALYST_LLM=Qwen/Qwen2.5-72B-Instruct
NEWS_ANALYST_LLM=deepseek-ai/DeepSeek-R1
TECHNICAL_ANALYST_LLM=Qwen/Qwen2.5-72B-Instruct
FUNDAMENTALS_ANALYST_LLM=Qwen/Qwen2.5-72B-Instruct
RISK_MANAGER_LLM=deepseek-ai/DeepSeek-V3

# 预估成本：¥0.05-0.15/次分析
```

#### 🚀 高性能配置（效果最佳）

```bash
# 高性能配置 - 最佳分析效果
DEFAULT_MODEL=anthropic/claude-3-5-sonnet-20241022
MARKET_ANALYST_LLM=anthropic/claude-3-5-sonnet-20241022
NEWS_ANALYST_LLM=deepseek-ai/DeepSeek-R1
TECHNICAL_ANALYST_LLM=Qwen/Qwen2.5-72B-Instruct
FUNDAMENTALS_ANALYST_LLM=anthropic/claude-3-5-sonnet-20241022
RISK_MANAGER_LLM=deepseek-ai/DeepSeek-V3

# 预估成本：¥0.10-0.30/次分析
```

## 📊 成本控制

### 用量监控

1. **实时监控**: 控制台查看实时用量
2. **成本预警**: 设置余额预警阈值
3. **用量统计**: 按模型、按时间查看详细用量
4. **账单导出**: 支持Excel格式账单导出

### 成本优化建议

1. **选择合适模型**: 根据任务复杂度选择模型
2. **批量处理**: 合并多个请求减少调用次数
3. **缓存结果**: 相同查询使用缓存结果
4. **设置限额**: 设置每日/每月用量上限
5. **定期清理**: 清理不必要的API调用

### 典型成本分析

| 使用场景 | 推荐模型 | 单次成本 | 月度成本(100次) |
|----------|----------|----------|-----------------|
| 个人投资者 | DeepSeek-V3 | ¥0.02 | ¥2 |
| 专业分析师 | Qwen2.5-72B | ¥0.08 | ¥8 |
| 机构用户 | Claude-3.5 | ¥0.20 | ¥20 |

## 🔧 高级配置

### 模型参数调优

```python
# 在 default_config.py 中配置
SILICONFLOW_CONFIG = {
    "temperature": 0.1,      # 降低随机性，提高一致性
    "max_tokens": 4000,      # 控制输出长度
    "top_p": 0.9,           # 核采样参数
    "frequency_penalty": 0,  # 频率惩罚
    "presence_penalty": 0    # 存在惩罚
}
```

### 错误处理配置

```python
# 重试配置
SILICONFLOW_RETRY_CONFIG = {
    "max_retries": 3,        # 最大重试次数
    "retry_delay": 1,        # 重试延迟（秒）
    "backoff_factor": 2,     # 退避因子
    "timeout": 30            # 请求超时（秒）
}
```

### 负载均衡配置

```python
# 多模型负载均衡
MODEL_POOL = [
    "deepseek-ai/DeepSeek-V3",
    "Qwen/Qwen2.5-72B-Instruct",
    "meta-llama/Llama-3.1-70B-Instruct"
]
```

## 🚨 常见问题

### Q: API密钥无效怎么办？
A: 检查密钥是否正确复制，确保没有多余的空格或换行符。

### Q: 余额不足如何充值？
A: 登录控制台，进入"财务管理" -> "充值"，支持多种支付方式。

### Q: 模型调用失败怎么处理？
A: 检查网络连接，确认模型名称正确，查看控制台错误日志。

### Q: 如何查看详细用量？
A: 控制台"用量统计"页面可查看详细的调用记录和费用明细。

### Q: 支持哪些模型？
A: 支持70+主流模型，包括Qwen、DeepSeek、Claude、GPT、Llama等系列。

## 📞 技术支持

- **官方文档**: [https://docs.siliconflow.cn/](https://docs.siliconflow.cn/)
- **API文档**: [https://docs.siliconflow.cn/api-reference](https://docs.siliconflow.cn/api-reference)
- **技术交流群**: 扫描官网二维码加入
- **工单系统**: 控制台提交技术工单
- **邮箱支持**: support@siliconflow.cn

## 🎉 新用户福利

- **注册即送**: 免费额度体验所有功能
- **首充优惠**: 首次充值享受额外赠送
- **推荐奖励**: 推荐好友注册获得奖励
- **企业优惠**: 企业用户享受批量折扣

---

**开始使用硅基流动，体验最高性价比的AI模型服务！** 🚀
