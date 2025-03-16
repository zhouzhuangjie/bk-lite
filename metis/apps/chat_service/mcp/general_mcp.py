import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("General", port=8002)


@mcp.tool()
def current_time() -> str:
    """
    这是一个获取当前时间的工具,可以获取当前的时间
    :return:
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@mcp.tool()
def chinese_holiday_lookup(year: int) -> str:
    """
    用于查询中国节假日信息的工具,帮助用户了解中国的节假日信息
    :param year: 需要查询的年份
    :return: 返回查询到的节假日信息
    """
    response = requests.get(f"https://api.jiejiariapi.com/v1/holidays/{str(year)}")
    return response.text


if __name__ == "__main__":
    mcp.run(transport="sse")
