from src.tools.time_tools import current_time_tool


class ToolsLoader:
    @staticmethod
    def load_tools(tools_protocol: str):
        tools_name = tools_protocol.split(":")[1]
        # langchain:current_time
        if tools_name == "current_time":
            return [current_time_tool]
        return []
