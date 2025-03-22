from loguru import logger
from typing import Dict, Callable, Any, TYPE_CHECKING

from apps.chat_service.graph.state import ChatState
from apps.chat_service.types.base_types import IOpenAIDriver

def create_execute_tools_node(driver: IOpenAIDriver) -> Callable:
    """
    创建执行工具调用节点
    
    Args:
        driver: OpenAIDriver实例
        
    Returns:
        节点函数
    """
    # 验证驱动类型，确保使用正确的驱动类型
    if hasattr(driver, 'is_streaming') and driver.is_streaming():
        logger.warning("在图节点中使用了流式驱动，工具执行可能不稳定")
        
    async def execute_tools(state: ChatState) -> ChatState:
        """
        执行工具调用节点
        
        Args:
            state: 当前状态
            
        Returns:
            更新后的状态
        """
        if not state["mcp_servers"]:
            return state
            
        try:
            rag_content, tool_prompt_tokens, tool_completion_tokens = await driver.execute_with_tools(
                state["user_message"],
                state["message_history"],
                state["system_prompt"],
                state["rag_content"],
                state["mcp_servers"]
            )
            logger.info(f"工具执行结果: 输入tokens: {tool_prompt_tokens}, 输出tokens: {tool_completion_tokens}")
            
            state["rag_content"] = rag_content
            state["input_tokens"] = tool_prompt_tokens
            state["output_tokens"] = tool_completion_tokens
        except Exception as e:
            logger.error(f"工具执行失败: {str(e)}")
            # 失败时不更新状态，继续执行流程
            
        return state
        
    return execute_tools


def create_invoke_simple_chain_node(driver: IOpenAIDriver) -> Callable:
    """
    创建执行简单对话链节点
    
    Args:
        driver: OpenAIDriver实例
        
    Returns:
        节点函数
    """
    # 验证驱动类型，确保使用正确的驱动类型
    if hasattr(driver, 'is_streaming') and driver.is_streaming():
        logger.warning("在图节点中使用了流式驱动，这可能导致非预期行为")
        
    def invoke_simple_chain(state: ChatState) -> Dict:
        """
        执行简单对话链节点
        
        Args:
            state: 当前状态
            
        Returns:
            对话结果
        """
        result = driver.invoke_simple_chain(
            state["user_message"],
            state["message_history"],
            state["system_prompt"],
            state["rag_content"],
            state["trace_id"],
            state["image_data"]
        )
        
        # 合并工具调用的token计数
        result["input_tokens"] += state.get("input_tokens", 0)
        
        return {
            "result": result["content"], 
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"]
        }
        
    return invoke_simple_chain
