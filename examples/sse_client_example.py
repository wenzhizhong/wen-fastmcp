"""SSE 传输模式客户端调用示例

演示如何使用 SSE 传输模式调用 MCP 服务器。
包括两种方式：
1. 使用 mcp.client.sse 模块的 sse_client 函数（推荐）
2. 直接调用 /mcp/messages 端点（需要手动管理 session_id）

注意：SSE 是长连接模式，客户端会持续运行。
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx

from mcp.client.sse import sse_client
from mcp import ClientSession


async def main():
    """主函数"""
    print("=" * 50)
    print("MCP SSE Client Example")
    print("=" * 50)
    print()

    base_url = "http://localhost:8003"
    token = "123456"

    headers = {'Authorization': f'Bearer {token}'}

    print(f"Connecting to {base_url}/sse...")

    try:
        async with sse_client(
            url=f'{base_url}/mcp/sse',
            headers=headers
        ) as (read_stream, write_stream):
            print("SSE connected! Creating session...")

            async with ClientSession(read_stream, write_stream) as session:
                print("Session created! Initializing...")

                # 初始化连接
                await session.initialize()
                print("Initialized!")
                print()

                # 列出工具
                print("Listing tools...")
                result = await session.list_tools()
                print(f"Tools: {[t.name for t in result.tools]}")
                print()

                # 调用工具
                print("Calling 'add' tool...")
                result = await session.call_tool("add", {"a": 10, "b": 5})
                print(f"Result: {result.content[0].text if result.content else result}")
                print()

                print("Calling 'reverse_text' tool...")
                result = await session.call_tool("reverse_text", {"text": "Hello MCP"})
                print(f"Result: {result.content[0].text if result.content else result}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    print()
    print("Done!")


async def messages_endpoint_example():
    """直接使用 /mcp/messages 端点的示例

    SSE 传输需要完整会话流程：
    1. GET /mcp/sse 建立 SSE 连接（保持连接以接收响应）
    2. POST /mcp/messages 发送消息（响应通过 SSE 流返回）
    """
    print("=" * 50)
    print("MCP Messages Endpoint Example")
    print("=" * 50)
    print()

    base_url = "http://localhost:8003"
    token = "123456"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'
    }

    print(f"Server URL: {base_url}")
    print()

    try:
        # 使用两个客户端：一个用于 SSE（接收响应），一个用于 POST（发送请求）
        async with httpx.AsyncClient() as sse_client, httpx.AsyncClient() as post_client:
            # 步骤1: 建立 SSE 连接（后台任务，持续读取响应）
            print("步骤1: 建立 SSE 连接...")

            sse_response_text = ""

            async def read_sse_responses():
                nonlocal sse_response_text
                try:
                    async with sse_client.stream(
                        "GET",
                        f"{base_url}/mcp/sse",
                        headers=headers,
                        timeout=60.0
                    ) as response:
                        print(f"  SSE Status: {response.status_code}")

                        async for chunk in response.aiter_bytes():
                            sse_response_text += chunk.decode('utf-8')
                except Exception as e:
                    pass  # 预期会超时或中断

            # 启动 SSE 读取任务
            sse_task = asyncio.create_task(read_sse_responses())

            # 等待 SSE 连接建立并获取 session_id（增加等待时间）
            await asyncio.sleep(2.0)

            # 从 SSE 响应中提取 session_id
            import re
            # 查找 session_id
            session_match = re.search(r'session_id=([a-f0-9]+)', sse_response_text)
            if session_match:
                session_id = session_match.group(1)
                messages_url = f"{base_url}/mcp/messages/?session_id={session_id}"
                print(f"  Session ID: {session_id}")
                print(f"  Messages URL: {messages_url}")
            else:
                print("  Failed to get session_id from SSE")
                sse_task.cancel()
                return

            print()
            print("步骤2: 发送消息到 /mcp/messages...")
            print()

            # 发送初始化请求
            print("  Sending: initialize")
            resp = await post_client.post(
                messages_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "sse-client-example", "version": "1.0.0"}
                    }
                },
                headers=headers,
                timeout=10.0
            )
            print(f"  Status: {resp.status_code}")
            await asyncio.sleep(0.5)

            # 发送 initialized 通知（通知消息没有 id）
            print("  Sending: notifications/initialized")
            resp = await post_client.post(
                messages_url,
                json={"jsonrpc": "2.0", "method": "notifications/initialized"},
                headers=headers,
                timeout=10.0
            )
            print(f"  Status: {resp.status_code}")
            await asyncio.sleep(0.5)

            # 列出工具
            print("  Sending: tools/list")
            resp = await post_client.post(
                messages_url,
                json={"jsonrpc": "2.0", "id": 3, "method": "tools/list", "params": {}},
                headers=headers,
                timeout=10.0
            )
            print(f"  Status: {resp.status_code}")
            await asyncio.sleep(0.5)

            # 调用工具
            print("  Sending: tools/call (add)")
            resp = await post_client.post(
                messages_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {"name": "add", "arguments": {"a": 100, "b": 200}}
                },
                headers=headers,
                timeout=10.0
            )
            print(f"  Status: {resp.status_code}")
            await asyncio.sleep(0.5)

            print("  Sending: tools/call (reverse_text)")
            resp = await post_client.post(
                messages_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 5,
                    "method": "tools/call",
                    "params": {"name": "reverse_text", "arguments": {"text": "Hello MCP Messages Endpoint"}}
                },
                headers=headers,
                timeout=10.0
            )
            print(f"  Status: {resp.status_code}")
            await asyncio.sleep(0.5)

            # 等待 SSE 响应
            await asyncio.sleep(1.0)

            # 打印 SSE 响应
            if sse_response_text:
                print()
                print("  SSE Responses received:")
                print("-" * 40)
                print(sse_response_text[:2000])
                if len(sse_response_text) > 2000:
                    print(f"  ... (truncated, total {len(sse_response_text)} chars)")
                print("-" * 40)

            # 取消 SSE 任务
            sse_task.cancel()

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    print()
    print("Done!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MCP SSE Client Example")
    parser.add_argument(
        "--method",
        choices=["sse", "messages", "both"],
        default="both",
        help="Which method to use: 'sse' for sse_client, 'messages' for messages endpoint, 'both' for both (default)"
    )
    args = parser.parse_args()

    print("Starting MCP SSE client example...")
    print()
    print("Make sure the server is running:")
    print("  .venv/Scripts/python.exe -c \"from src.app import create_app; import uvicorn; app = create_app(); uvicorn.run(app, host='0.0.0.0', port=8003)\"")
    print()

    if args.method in ["sse", "both"]:
        asyncio.run(main())

    if args.method in ["messages", "both"]:
        if args.method == "both":
            print()
            print("#" * 50)
            print()
        asyncio.run(messages_endpoint_example())
