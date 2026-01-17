"""测试脚本"""

import asyncio
from fastmcp import Client
from src.server import mcp


async def test_mcp_server():
    """测试所有MCP工具"""
    async with Client(mcp) as client:
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")
        print()

        print("Testing add tool:")
        result = await client.call_tool("add", {"a": 10, "b": 5})
        print(f"  add(10, 5) = {result.data}")
        print()

        print("Testing multiply tool:")
        result = await client.call_tool("multiply", {"a": 3.5, "b": 2})
        print(f"  multiply(3.5, 2) = {result.data}")
        print()

        print("Testing get_weather tool:")
        result = await client.call_tool("get_weather", {"city": "Beijing"})
        print(f"  get_weather('Beijing') = {result.data}")
        print()

        print("Testing reverse_text tool:")
        result = await client.call_tool("reverse_text", {"text": "Hello MCP"})
        print(f"  reverse_text('Hello MCP') = {result.data}")
        print()

        resources = await client.list_resources()
        print(f"Available resources: {[r.uri for r in resources]}")
        print()

        if resources:
            print("Testing resource access:")
            content = await client.read_resource("config://app-info")
            print(f"  config://app-info = {content}")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
