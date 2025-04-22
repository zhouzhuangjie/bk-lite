from src.tools.search_tools import duckduckgo_search
from src.tools.time_tools import get_current_time

ToolsMap = {
    'current_time': get_current_time,
    'duckduckgo': duckduckgo_search
}


class ToolsLoader:

    @staticmethod
    def load_tools(tools_protocol: str):
        tools_name = tools_protocol.split(":")[1]
        return ToolsMap[tools_name]
