# TradingAgents/graph/setup.py

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode

from tradingagents.agents import *
from tradingagents.agents.utils.agent_states import AgentState
from tradingagents.agents.utils.agent_utils import Toolkit

from .conditional_logic import ConditionalLogic


class GraphSetup:
    """Handles the setup and configuration of the agent graph."""

    def __init__(
        self,
        quick_thinking_llm: ChatOpenAI,
        deep_thinking_llm: ChatOpenAI,
        toolkit: Toolkit,
        tool_nodes: Dict[str, ToolNode],
        bull_memory,
        bear_memory,
        trader_memory,
        invest_judge_memory,
        risk_manager_memory,
        conditional_logic: ConditionalLogic,
        config: Dict[str, Any] = None,
        react_llm = None,
    ):
        """Initialize with required components."""
        self.quick_thinking_llm = quick_thinking_llm
        self.deep_thinking_llm = deep_thinking_llm
        self.toolkit = toolkit
        self.tool_nodes = tool_nodes
        self.bull_memory = bull_memory
        self.bear_memory = bear_memory
        self.trader_memory = trader_memory
        self.invest_judge_memory = invest_judge_memory
        self.risk_manager_memory = risk_manager_memory
        self.conditional_logic = conditional_logic
        self.config = config or {}
        self.react_llm = react_llm

    def _create_specialized_llm(self, config_key: str):
        """为特定分析师创建专用的LLM实例，失败时回退到DEFAULT_MODEL"""
        import os

        model_name = self.config.get(config_key)
        if not model_name:
            # 如果没有配置专用模型，使用DEFAULT_MODEL
            default_model = os.getenv('DEFAULT_MODEL', 'deepseek-ai/DeepSeek-V3')
            print(f"⚠️ {config_key}未配置，使用默认模型: {default_model}")
            return self._create_fallback_llm(default_model)

        llm_provider = self.config.get("llm_provider", "").lower()

        if "siliconflow" in llm_provider or "硅基流动" in self.config.get("llm_provider", ""):
            # 创建硅基流动专用LLM
            from tradingagents.llm_adapters.siliconflow_adapter import ChatSiliconFlow

            siliconflow_api_key = os.getenv('SILICONFLOW_API_KEY')
            if not siliconflow_api_key:
                default_model = os.getenv('DEFAULT_MODEL', 'deepseek-ai/DeepSeek-V3')
                print(f"⚠️ 硅基流动API密钥未找到，{config_key}回退到默认模型: {default_model}")
                return self._create_fallback_llm(default_model)

            try:
                specialized_llm = ChatSiliconFlow(
                    model=model_name,
                    api_key=siliconflow_api_key,
                    temperature=0.1,
                    max_tokens=2000
                )
                print(f"✅ {config_key}成功创建专用模型: {model_name}")
                return specialized_llm
            except Exception as e:
                default_model = os.getenv('DEFAULT_MODEL', 'deepseek-ai/DeepSeek-V3')
                print(f"❌ {config_key}专用模型创建失败: {e}")
                print(f"🔄 回退到默认模型: {default_model}")
                return self._create_fallback_llm(default_model)
        else:
            # 其他提供商暂时回退到默认模型
            default_model = os.getenv('DEFAULT_MODEL', 'deepseek-ai/DeepSeek-V3')
            print(f"⚠️ 当前LLM提供商不支持专用模型配置，{config_key}回退到默认模型: {default_model}")
            return self._create_fallback_llm(default_model)

    def _create_fallback_llm(self, model_name: str):
        """创建回退LLM实例"""
        import os

        llm_provider = self.config.get("llm_provider", "").lower()

        if "siliconflow" in llm_provider or "硅基流动" in self.config.get("llm_provider", ""):
            # 使用硅基流动创建默认模型
            from tradingagents.llm_adapters.siliconflow_adapter import ChatSiliconFlow

            siliconflow_api_key = os.getenv('SILICONFLOW_API_KEY')
            if siliconflow_api_key:
                try:
                    return ChatSiliconFlow(
                        model=model_name,
                        api_key=siliconflow_api_key,
                        temperature=0.1,
                        max_tokens=2000
                    )
                except Exception as e:
                    print(f"❌ 默认模型{model_name}创建失败: {e}")

        # 最终回退到系统的快速思考模型
        print(f"🔄 最终回退到系统快速思考模型")
        return self.quick_thinking_llm

    def setup_graph(
        self, selected_analysts=["market", "social", "news", "fundamentals"]
    ):
        """Set up and compile the agent workflow graph.

        Args:
            selected_analysts (list): List of analyst types to include. Options are:
                - "market": Market analyst
                - "social": Social media analyst
                - "news": News analyst
                - "fundamentals": Fundamentals analyst
        """
        if len(selected_analysts) == 0:
            raise ValueError("Trading Agents Graph Setup Error: no analysts selected!")

        # Create analyst nodes
        analyst_nodes = {}
        delete_nodes = {}
        tool_nodes = {}

        if "market" in selected_analysts:
            # 为市场分析师创建专用的高性能LLM
            market_llm = self._create_specialized_llm("market_analyst_llm")
            print(f"📈 [DEBUG] 市场分析师使用专用模型: {self.config.get('market_analyst_llm', 'default')}")

            analyst_nodes["market"] = create_market_analyst(
                market_llm, self.toolkit
            )
            delete_nodes["market"] = create_msg_delete()
            tool_nodes["market"] = self.tool_nodes["market"]

        if "social" in selected_analysts:
            # 为社交媒体分析师创建专用的中文优化LLM
            social_llm = self._create_specialized_llm("social_analyst_llm")
            print(f"💭 [DEBUG] 社交媒体分析师使用专用模型: {self.config.get('social_analyst_llm', 'default')}")

            analyst_nodes["social"] = create_social_media_analyst(
                social_llm, self.toolkit
            )
            delete_nodes["social"] = create_msg_delete()
            tool_nodes["social"] = self.tool_nodes["social"]

        if "news" in selected_analysts:
            # 为新闻分析师创建专用的推理优化LLM
            news_llm = self._create_specialized_llm("news_analyst_llm")
            print(f"📰 [DEBUG] 新闻分析师使用专用模型: {self.config.get('news_analyst_llm', 'default')}")

            analyst_nodes["news"] = create_news_analyst(
                news_llm, self.toolkit
            )
            delete_nodes["news"] = create_msg_delete()
            tool_nodes["news"] = self.tool_nodes["news"]

        if "fundamentals" in selected_analysts:
            # 为基本面分析师创建专用的最高性能LLM
            fundamentals_llm = self._create_specialized_llm("fundamentals_analyst_llm")
            print(f"💰 [DEBUG] 基本面分析师使用专用模型: {self.config.get('fundamentals_analyst_llm', 'default')}")

            analyst_nodes["fundamentals"] = create_fundamentals_analyst(
                fundamentals_llm, self.toolkit
            )
            delete_nodes["fundamentals"] = create_msg_delete()
            tool_nodes["fundamentals"] = self.tool_nodes["fundamentals"]

        # Create researcher and manager nodes
        bull_researcher_node = create_bull_researcher(
            self.quick_thinking_llm, self.bull_memory
        )
        bear_researcher_node = create_bear_researcher(
            self.quick_thinking_llm, self.bear_memory
        )
        research_manager_node = create_research_manager(
            self.deep_thinking_llm, self.invest_judge_memory
        )
        trader_node = create_trader(self.quick_thinking_llm, self.trader_memory)

        # Create risk analysis nodes
        risky_analyst = create_risky_debator(self.quick_thinking_llm)
        neutral_analyst = create_neutral_debator(self.quick_thinking_llm)
        safe_analyst = create_safe_debator(self.quick_thinking_llm)
        risk_manager_node = create_risk_manager(
            self.deep_thinking_llm, self.risk_manager_memory
        )

        # Create workflow
        workflow = StateGraph(AgentState)

        # Add analyst nodes to the graph
        for analyst_type, node in analyst_nodes.items():
            workflow.add_node(f"{analyst_type.capitalize()} Analyst", node)
            workflow.add_node(
                f"Msg Clear {analyst_type.capitalize()}", delete_nodes[analyst_type]
            )
            workflow.add_node(f"tools_{analyst_type}", tool_nodes[analyst_type])

        # Add other nodes
        workflow.add_node("Bull Researcher", bull_researcher_node)
        workflow.add_node("Bear Researcher", bear_researcher_node)
        workflow.add_node("Research Manager", research_manager_node)
        workflow.add_node("Trader", trader_node)
        workflow.add_node("Risky Analyst", risky_analyst)
        workflow.add_node("Neutral Analyst", neutral_analyst)
        workflow.add_node("Safe Analyst", safe_analyst)
        workflow.add_node("Risk Judge", risk_manager_node)

        # Define edges
        # Start with the first analyst
        first_analyst = selected_analysts[0]
        workflow.add_edge(START, f"{first_analyst.capitalize()} Analyst")

        # Connect analysts in sequence
        for i, analyst_type in enumerate(selected_analysts):
            current_analyst = f"{analyst_type.capitalize()} Analyst"
            current_tools = f"tools_{analyst_type}"
            current_clear = f"Msg Clear {analyst_type.capitalize()}"

            # Add conditional edges for current analyst
            workflow.add_conditional_edges(
                current_analyst,
                getattr(self.conditional_logic, f"should_continue_{analyst_type}"),
                [current_tools, current_clear],
            )
            workflow.add_edge(current_tools, current_analyst)

            # Connect to next analyst or to Bull Researcher if this is the last analyst
            if i < len(selected_analysts) - 1:
                next_analyst = f"{selected_analysts[i+1].capitalize()} Analyst"
                workflow.add_edge(current_clear, next_analyst)
            else:
                workflow.add_edge(current_clear, "Bull Researcher")

        # Add remaining edges
        workflow.add_conditional_edges(
            "Bull Researcher",
            self.conditional_logic.should_continue_debate,
            {
                "Bear Researcher": "Bear Researcher",
                "Research Manager": "Research Manager",
            },
        )
        workflow.add_conditional_edges(
            "Bear Researcher",
            self.conditional_logic.should_continue_debate,
            {
                "Bull Researcher": "Bull Researcher",
                "Research Manager": "Research Manager",
            },
        )
        workflow.add_edge("Research Manager", "Trader")
        workflow.add_edge("Trader", "Risky Analyst")
        workflow.add_conditional_edges(
            "Risky Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Safe Analyst": "Safe Analyst",
                "Risk Judge": "Risk Judge",
            },
        )
        workflow.add_conditional_edges(
            "Safe Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Neutral Analyst": "Neutral Analyst",
                "Risk Judge": "Risk Judge",
            },
        )
        workflow.add_conditional_edges(
            "Neutral Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Risky Analyst": "Risky Analyst",
                "Risk Judge": "Risk Judge",
            },
        )

        workflow.add_edge("Risk Judge", END)

        # Compile and return
        return workflow.compile()
