from loguru import logger

from src.tools.time_tools import current_time_tool


def test_current_time_tool_returns_string():
    result = current_time_tool.run("")
    logger.info(result)

