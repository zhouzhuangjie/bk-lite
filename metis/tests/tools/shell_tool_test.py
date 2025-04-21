import pytest
from loguru import logger

from src.tools.shell_tool_ex import ShelToolEx


def test_shell_tool_ex():
    tools = ShelToolEx()
    tools.run({"commands": ["date"]})