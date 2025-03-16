from mcp.server.fastmcp import FastMCP
from duckduckgo_search import DDGS
from typing import Optional

mcp = FastMCP("Web Search", port=8001)


@mcp.tool(description="这是DuckDuckGo的搜索工具，帮助用户在DuckDuckGo上搜索信息,获取互联网信息")
def duckduckgo_search(query: str, max_results: Optional[int] = 5) -> str:
    """
    使用DuckDuckGo搜索引擎搜索信息

    参数:
        query: 搜索查询字符串
        max_results: 返回的最大结果数量，默认为5

    返回:
        搜索结果的格式化字符串
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return "未找到相关搜索结果。"

        formatted_results = []
        for i, result in enumerate(results, 1):
            title = result.get('title', '无标题')
            body = result.get('body', '无内容')
            href = result.get('href', '无链接')
            formatted_results.append(f"{i}. {title}\n   {body}\n   链接: {href}\n")

        return "\n".join(formatted_results)
    except Exception as e:
        return f"搜索过程中出现错误: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="sse")
