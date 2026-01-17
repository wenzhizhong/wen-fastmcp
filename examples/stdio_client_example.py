"""STDIO模式客户端调用示例

演示如何通过stdio transport调用MCP服务器。
需要先启动服务器，然后客户端连接到服务器进行调用。
"""

import asyncio
import subprocess
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# 服务器启动配置
SERVER_SCRIPT = Path(__file__).parent.parent / "main.py"
AUTH_TOKEN = "your-secret-token"


@asynccontextmanager
async def get_mcp_client():
    """创建MCP客户端连接"""

    server_params = StdioServerParameters(
        command="python",
        args=[
            str(SERVER_SCRIPT),
            "--transport", "stdio",
            "--token", AUTH_TOKEN
        ],
        env={
            "PYTHONIOENCODING": "utf-8"
        }
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化连接
            await session.initialize()
            yield session


async def test_stdio_client():
    """测试stdio客户端调用"""

    print("=" * 50)
    print("MCP STDIO Client Example")
    print("=" * 50)
    print()

    async with get_mcp_client() as session:
        # 1. 列出所有可用工具
        print("1. Listing available tools...")
        tools = await session.list_tools()
        tool_names = [t.name for t in tools]
        print(f"   Tools: {tool_names}")
        print()

        # 2. 调用 add 工具
        print("2. Calling 'add' tool...")
        result = await session.call_tool("add", {"a": 10, "b": 5})
        print(f"   add(10, 5) = {result.content[0].text}")
        print()

        # 3. 调用 multiply 工具
        print("3. Calling 'multiply' tool...")
        result = await session.call_tool("multiply", {"a": 3.5, "b": 2})
        print(f"   multiply(3.5, 2) = {result.content[0].text}")
        print()

        # 4. 调用 get_weather 工具
        print("4. Calling 'get_weather' tool...")
        result = await session.call_tool("get_weather", {"city": "Beijing"})
        print(f"   get_weather('Beijing') = {result.content[0].text}")
        print()

        # 5. 调用 reverse_text 工具
        print("5. Calling 'reverse_text' tool...")
        result = await session.call_tool("reverse_text", {"text": "Hello MCP"})
        print(f"   reverse_text('Hello MCP') = {result.content[0].text}")
        print()

        # 6. 列出资源
        print("6. Listing available resources...")
        resources = await session.list_resources()
        resource_uris = [r.uri for r in resources]
        print(f"   Resources: {resource_uris}")
        print()

        # 7. 读取资源
        if resources:
            print("7. Reading resource 'config://app-info'...")
            content = await session.read_resource("config://app-info")
            print(f"   Content: {content.contents[0].text}")


async def test_with_subprocess():
    """使用subprocess手动管理服务器进程"""

    print("=" * 50)
    print("MCP STDIO Client with Subprocess")
    print("=" * 50)
    print()

    # 启动服务器进程
    server_params = StdioServerParameters(
        command="python",
        args=[
            str(SERVER_SCRIPT),
            "--transport", "stdio",
            "--token", AUTH_TOKEN
        ]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 调用工具
            result = await session.call_tool("add", {"a": 100, "b": 200})
            print(f"add(100, 200) = {result.content[0].text}")


if __name__ == "__main__":
    print("Starting MCP STDIO client examples...\n")

    # 运行示例
    asyncio.run(test_stdio_client())

    print("\n" + "=" * 50)
    print("Example completed!")
