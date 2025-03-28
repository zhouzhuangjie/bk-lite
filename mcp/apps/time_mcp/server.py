from mcp.server.fastmcp import FastMCP
import mcp.types as types
from pydantic import AnyUrl
import datetime
import zoneinfo

mcp = FastMCP("Time MCP", port=7000)


@mcp.tool()
def current_time() -> str:
    """
    这是一个获取当前时间的工具,可以获取当前的时间
    :return:
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@mcp.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri=AnyUrl(f"datetime://{timezone}/now"),
            name=f"Current time in {timezone}",
            description=f"The current time in {timezone}, as reported by the system clock",
            mimeType="text/plain",
        )
        for timezone in zoneinfo.available_timezones()
    ]


@mcp.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    if uri.scheme == "datetime":
        assert uri.host is not None
        assert uri.path is not None

        resource = uri.unicode_string()
        time = resource.split("/")[-1]

        if time == "now":
            tz = uri.unicode_string().removeprefix("datetime://").removesuffix("/now")
            dt = datetime.datetime.now(zoneinfo.ZoneInfo(tz))
        else:
            # TODO: perhaps we should use templates to allow the client to use time values other then "now"
            raise ValueError(f"Unsupported time: {time}")

        return f"YYYY-MM-DD HH:MM:SS {dt.strftime("%Y-%m-%d %H:%M:%S")}"

    raise ValueError(f"Unsupported URI scheme: {uri.scheme}")


@mcp.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="get-current-time",
            description="Get the current time in the configured local timezone",
            inputSchema={"type": "object"},
        )
    ]


@mcp.call_tool()
async def handle_call_tool(
        name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    if name == "get-current-time":
        return [
            types.TextContent(
                type="text",
                text=f"The current time is {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            )
        ]

    raise ValueError(f"Unknown tool: {name}")


if __name__ == "__main__":
    mcp.run(transport="sse")
