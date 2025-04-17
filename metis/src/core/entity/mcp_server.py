from pydantic import BaseModel


class MCPServer(BaseModel):
    name: str
    url: str
