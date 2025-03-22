from langgraph.constants import START
from langgraph.graph import StateGraph, END
from loguru import logger
from typing import Any

from apps.chat_service.graph.state import ChatState
from apps.chat_service.graph.nodes import create_execute_tools_node, create_invoke_simple_chain_node


def build_chat_graph(driver: Any):
    """
    构建聊天处理图
    
    Args:
        driver: OpenAIDriver实例
        
    Returns:
        构建好的LangGraph图
    """
    # 验证驱动类型
    if hasattr(driver, 'is_streaming') and driver.is_streaming():
        logger.warning("使用流式驱动构建图可能导致意外行为，建议使用常规驱动")

    # 创建节点函数，以闭包方式访问driver
    execute_tools = create_execute_tools_node(driver)
    invoke_simple_chain = create_invoke_simple_chain_node(driver)

    # 定义图
    builder = StateGraph(ChatState)

    # 添加节点
    builder.add_node("execute_tools", execute_tools)
    builder.add_node("invoke_simple_chain", invoke_simple_chain)

    # 设置节点流转
    builder.add_edge(START, "execute_tools")
    builder.add_edge("execute_tools", "invoke_simple_chain")
    builder.add_edge("invoke_simple_chain", END)

    # 编译并返回图
    return builder.compile()
