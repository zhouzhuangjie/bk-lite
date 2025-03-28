import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from datetime import datetime, timezone, timedelta

load_dotenv()
mcp = FastMCP("Time MCP", port=os.getenv("APP_PORT", 7000))


@mcp.tool()
def current_time() -> str:
    """
    这是一个获取当前时间的工具,可以获取当前的时间
    :return:
    """
    # 获取当前时区
    tz = timezone(timedelta(hours=8))  # 中国标准时间 UTC+8

    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    mcp.run(transport="sse")
