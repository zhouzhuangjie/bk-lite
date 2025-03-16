from langserve import CustomUserType


class McpServer(CustomUserType):
    name: str
    url: str
