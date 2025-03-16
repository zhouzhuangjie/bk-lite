import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("General", port=8002)


@mcp.tool(description="这是一个获取当前时间的工具,可以获取当前的时间")
def current_time() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@mcp.tool(description="用于查询中国节假日信息的工具,帮助用户了解中国的节假日信息")
def chinese_holiday_lookup(year: int) -> str:
    response = requests.get(f"https://api.jiejiariapi.com/v1/holidays/{str(year)}")
    return response.text


if __name__ == "__main__":
    mcp.run(transport="sse")
