from datetime import datetime

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Time MCP", port=7000)


@mcp.tool()
def current_time() -> str:
    """
    这是一个获取当前时间的工具,可以获取当前的时间
    :return:
    """
    # 获取当前时区
    tz = datetime.now().astimezone().tzinfo

    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    mcp.run(transport="sse")
