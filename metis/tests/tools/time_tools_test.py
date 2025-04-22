import pytest
from loguru import logger
from datetime import datetime
from unittest.mock import patch

from src.tools.time_tools import current_time_tool


def test_current_time_tool_returns_string():
    result = current_time_tool.run("")
    logger.info(result)

