from datetime import datetime

from langchain_core.tools import tool


@tool
def current_time_tool() -> str:
    """
    这个工具可以用于获取当前时间
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
