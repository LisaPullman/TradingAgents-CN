#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硅基流动 (SiliconFlow) API 适配器
支持多种模型的统一接口，包括 DeepSeek、Qwen、Claude、GPT 等
"""

import os
from typing import Optional, Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.outputs import ChatResult, ChatGeneration

# 避免循环导入，直接继承ChatOpenAI
from langchain_openai import ChatOpenAI


class ChatSiliconFlow(ChatOpenAI):
    """硅基流动 OpenAI 兼容适配器"""
    
    def __init__(
        self,
        model: str = "deepseek-ai/DeepSeek-V3",
        api_key: Optional[str] = None,
        base_url: str = "https://api.siliconflow.cn/v1",
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        初始化硅基流动适配器
        
        Args:
            model: 模型名称，默认为deepseek-chat
            api_key: API密钥，如果不提供则从环境变量SILICONFLOW_API_KEY获取
            base_url: API基础URL
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
        """
        
        # 获取API密钥
        if api_key is None:
            api_key = os.getenv("SILICONFLOW_API_KEY")
            if not api_key:
                raise ValueError("硅基流动 API密钥未找到。请设置SILICONFLOW_API_KEY环境变量或传入api_key参数。")
        
        # 初始化父类 - 直接使用ChatOpenAI的参数
        super().__init__(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        self.model_name = model
        print(f"✅ 硅基流动适配器初始化成功")
        print(f"   模型: {model}")
        print(f"   API Base: {base_url}")


# 支持的硅基流动模型配置（基于实际支持的模型）
SILICONFLOW_MODELS = {
    # DeepSeek 系列 - 硅基流动主要支持的模型
    "deepseek-ai/DeepSeek-V3": {
        "description": "DeepSeek V3 - 最新版本，推理能力强",
        "context_length": 64000,
        "supports_function_calling": True,
        "recommended_for": ["通用对话", "代码分析", "逻辑推理", "金融分析"],
        "provider": "deepseek",
        "alias": "deepseek-chat"
    },
    "deepseek-ai/DeepSeek-R1": {
        "description": "DeepSeek R1 - 推理专用模型",
        "context_length": 64000,
        "supports_function_calling": True,
        "recommended_for": ["复杂推理", "数学计算", "逻辑分析"],
        "provider": "deepseek"
    },
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B": {
        "description": "DeepSeek R1 蒸馏版 - 轻量级推理模型",
        "context_length": 32000,
        "supports_function_calling": True,
        "recommended_for": ["快速推理", "成本优化", "简单分析"],
        "provider": "deepseek"
    },

    # Qwen 系列
    "Qwen/QwQ-32B-Preview": {
        "description": "通义千问 QwQ-32B - 问答专用模型",
        "context_length": 32000,
        "supports_function_calling": True,
        "recommended_for": ["问答任务", "知识查询", "信息检索"],
        "provider": "alibaba"
    },
    "Qwen/Qwen2.5-72B-Instruct": {
        "description": "通义千问 2.5-72B - 指令跟随模型",
        "context_length": 32000,
        "supports_function_calling": True,
        "recommended_for": ["复杂指令", "专业任务", "深度分析"],
        "provider": "alibaba"
    },
    "Qwen/Qwen2.5-32B-Instruct": {
        "description": "通义千问 2.5-32B - 平衡性能模型",
        "context_length": 32000,
        "supports_function_calling": True,
        "recommended_for": ["日常任务", "中等复杂度分析"],
        "provider": "alibaba"
    },
    "Qwen/Qwen2.5-14B-Instruct": {
        "description": "通义千问 2.5-14B - 轻量级模型",
        "context_length": 32000,
        "supports_function_calling": True,
        "recommended_for": ["快速任务", "成本优化"],
        "provider": "alibaba"
    },

    # GLM 系列
    "THUDM/GLM-4-9B-Chat": {
        "description": "GLM-4-9B - 清华大学开源模型",
        "context_length": 32000,
        "supports_function_calling": True,
        "recommended_for": ["中文对话", "学术分析"],
        "provider": "thudm"
    },

    # Meta Llama 系列
    "meta-llama/Llama-3.1-70B-Instruct": {
        "description": "Llama 3.1 70B - Meta开源大模型",
        "context_length": 128000,
        "supports_function_calling": True,
        "recommended_for": ["长文本处理", "复杂推理"],
        "provider": "meta"
    },
    "meta-llama/Llama-3.1-8B-Instruct": {
        "description": "Llama 3.1 8B - 轻量级版本",
        "context_length": 128000,
        "supports_function_calling": True,
        "recommended_for": ["快速任务", "资源受限环境"],
        "provider": "meta"
    }
}


def get_available_siliconflow_models() -> Dict[str, Dict[str, Any]]:
    """获取可用的硅基流动模型列表"""
    return SILICONFLOW_MODELS


def create_siliconflow_llm(
    model: str = "deepseek-ai/DeepSeek-V3",
    api_key: Optional[str] = None,
    temperature: float = 0.1,
    max_tokens: int = 2000,
    **kwargs
) -> ChatSiliconFlow:
    """创建硅基流动 LLM 实例的便捷函数"""
    
    return ChatSiliconFlow(
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )


def get_model_recommendations(task_type: str = "general") -> List[str]:
    """
    根据任务类型推荐最适合的模型（基于硅基流动实际支持的模型）

    Args:
        task_type: 任务类型 ("general", "coding", "analysis", "fast", "cost_effective", "financial", "chinese", "reasoning")

    Returns:
        推荐的模型列表
    """
    recommendations = {
        "general": ["deepseek-ai/DeepSeek-V3", "Qwen/Qwen2.5-32B-Instruct", "meta-llama/Llama-3.1-70B-Instruct"],
        "coding": ["deepseek-ai/DeepSeek-V3", "deepseek-ai/DeepSeek-R1", "Qwen/Qwen2.5-72B-Instruct"],
        "analysis": ["deepseek-ai/DeepSeek-V3", "Qwen/Qwen2.5-72B-Instruct", "meta-llama/Llama-3.1-70B-Instruct"],
        "fast": ["deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B", "Qwen/Qwen2.5-14B-Instruct", "meta-llama/Llama-3.1-8B-Instruct"],
        "cost_effective": ["deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B", "Qwen/Qwen2.5-14B-Instruct", "THUDM/GLM-4-9B-Chat"],
        "financial": ["deepseek-ai/DeepSeek-V3", "Qwen/Qwen2.5-72B-Instruct", "deepseek-ai/DeepSeek-R1"],
        "chinese": ["Qwen/Qwen2.5-72B-Instruct", "Qwen/Qwen2.5-32B-Instruct", "THUDM/GLM-4-9B-Chat"],
        "reasoning": ["deepseek-ai/DeepSeek-R1", "deepseek-ai/DeepSeek-V3", "Qwen/QwQ-32B-Preview"],
        "qa": ["Qwen/QwQ-32B-Preview", "deepseek-ai/DeepSeek-V3", "Qwen/Qwen2.5-72B-Instruct"]
    }

    return recommendations.get(task_type, recommendations["general"])


def test_siliconflow_connection(api_key: Optional[str] = None) -> bool:
    """
    测试硅基流动连接
    
    Args:
        api_key: API密钥，如果不提供则从环境变量获取
    
    Returns:
        连接是否成功
    """
    try:
        llm = create_siliconflow_llm(
            model="deepseek-ai/DeepSeek-V3",
            api_key=api_key,
            max_tokens=50
        )
        
        # 发送测试消息
        response = llm.invoke([HumanMessage(content="你好，请回复'连接成功'")])
        
        if response and response.content:
            print("✅ 硅基流动连接测试成功")
            return True
        else:
            print("❌ 硅基流动连接测试失败：无响应")
            return False
            
    except Exception as e:
        print(f"❌ 硅基流动连接测试失败: {e}")
        return False


if __name__ == "__main__":
    # 测试硅基流动适配器
    print("🧪 硅基流动适配器测试")
    print("=" * 50)
    
    # 检查API密钥
    api_key = os.getenv('SILICONFLOW_API_KEY')
    if not api_key:
        print("❌ 未找到 SILICONFLOW_API_KEY 环境变量")
        print("💡 请设置环境变量: export SILICONFLOW_API_KEY=your_api_key")
        exit(1)
    
    print(f"✅ API密钥: {api_key[:10]}...")
    
    # 测试连接
    if test_siliconflow_connection():
        print("\n🎉 硅基流动适配器测试通过！")
        
        # 显示可用模型
        print("\n📋 可用模型:")
        models = get_available_siliconflow_models()
        for model_name, info in models.items():
            print(f"  • {model_name}: {info['description']}")
        
        # 显示推荐模型
        print("\n💡 金融分析推荐模型:")
        financial_models = get_model_recommendations("financial")
        for model in financial_models:
            print(f"  • {model}")
    else:
        print("\n❌ 硅基流动适配器测试失败")
