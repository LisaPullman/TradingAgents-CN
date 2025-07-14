# LLM Adapters for TradingAgents

# 使用try-except来处理可选依赖
try:
    from .dashscope_adapter import ChatDashScope
    DASHSCOPE_AVAILABLE = True
except ImportError:
    ChatDashScope = None
    DASHSCOPE_AVAILABLE = False

try:
    from .dashscope_openai_adapter import ChatDashScopeOpenAI
    DASHSCOPE_OPENAI_AVAILABLE = True
except ImportError:
    ChatDashScopeOpenAI = None
    DASHSCOPE_OPENAI_AVAILABLE = False

try:
    from .siliconflow_adapter import ChatSiliconFlow
    SILICONFLOW_AVAILABLE = True
except ImportError:
    ChatSiliconFlow = None
    SILICONFLOW_AVAILABLE = False

# 只导出可用的适配器
__all__ = []
if DASHSCOPE_AVAILABLE:
    __all__.append("ChatDashScope")
if DASHSCOPE_OPENAI_AVAILABLE:
    __all__.append("ChatDashScopeOpenAI")
if SILICONFLOW_AVAILABLE:
    __all__.append("ChatSiliconFlow")
