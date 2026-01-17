# FastAPI MCP 演示

一个演示 MCP（Model Context Protocol）服务器与 FastAPI 集成的项目，支持 STDIO 和 SSE 两种传输模式。

[English](README.md) | 简体中文

## 安装

```bash
uv pip install -e .
```

## 使用方法

### STDIO 传输（默认）

使用 STDIO 传输模式运行 MCP 服务器：

```bash
# 不使用认证
python main.py --transport stdio

# 使用认证（单个token）
python main.py --transport stdio --token "your-secret-token"

# 使用认证（多个token）
python main.py --transport stdio --token "token1" --token "token2"
```

#### Python 客户端调用示例

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["main.py", "--transport", "stdio", "--token", "your-token"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 列出工具
            tools = await session.list_tools()
            print(f"工具列表: {[t.name for t in tools]}")

            # 调用工具
            result = await session.call_tool("add", {"a": 5, "b": 3})
            print(f"结果: {result.content[0].text}")


asyncio.run(main())
```

完整示例请查看 [examples/stdio_client_example.py](examples/stdio_client_example.py)。

#### Claude Desktop 配置

在 Claude Desktop 配置文件中添加：

```json
{
  "mcpServers": {
    "fastapi-mcp": {
      "command": "python",
      "args": [
        "D:/path/to/fastapi_mcp2/main.py",
        "--transport",
        "stdio",
        "--token",
        "your-secret-token"
      ]
    }
  }
}
```

### SSE/HTTP 传输

使用 FastAPI 通过 SSE/HTTP 传输模式运行 MCP 服务器：

```bash
python main.py --transport sse --host 0.0.0.0 --port 8000
```

## 认证

默认启用认证。有多种方式配置 token：

### 命令行参数

```bash
# 单个token
python main.py --transport stdio --token "your-secret-token"
python main.py --transport sse --token "your-secret-token"

# 多个token
python main.py --transport stdio --token "token1" --token "token2" --token "token3"
```

### 环境变量

```bash
# 单个token
set MCP_AUTH_TOKEN=your-secret-token

# 多个token（逗号分隔）
set MCP_AUTH_TOKENS=token1,token2,token3
```

### 禁用认证

```bash
python main.py --transport stdio --no-auth
python main.py --transport sse --no-auth
```

**注意：** 当启用认证但未提供 token 时，服务器会立即退出并显示错误信息。

### 配置文件

创建 `config.json` 文件：

```json
{
  "enabled": true,
  "tokens": ["your-secret-token"],
  "require_auth": true
}
```

通过代码加载：

```python
from src.auth import AuthConfig
config = AuthConfig.from_file("config.json")
```

## 可用工具

- `add(a, b)` - 加法运算
- `multiply(a, b)` - 乘法运算
- `get_weather(city)` - 获取城市天气
- `reverse_text(text)` - 翻转文本

## 可用资源

- `config://app-info` - 应用信息

## API 端点

使用 SSE 传输模式时：

- `GET /` - 根端点，显示可用路由
- `GET /health` - 健康检查
- `GET /mcp/sse` - SSE 端点
- `POST /mcp/message` - 消息端点

## 项目结构

```
src/
├── server.py        # MCP 服务器实例
├── app.py           # FastAPI 应用
├── auth.py          # 认证配置
├── tools/           # 工具实现
│   └── __init__.py
└── resources/       # 资源实现
    └── __init__.py
tests/
├── conftest.py      # Pytest  fixtures
├── test_auth.py     # 认证测试
├── test_server.py   # 服务器测试
└── test_mcp.py      # MCP 测试脚本
examples/
└── stdio_client_example.py  # STDIO 客户端示例
```

## 添加新工具

编辑 `src/tools/__init__.py`：

```python
from ..server import mcp

@mcp.tool
def my_tool(param: str) -> str:
    """我的新工具。"""
    return param.upper()
```

## 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_auth.py::TestAuthConfig::test_default_config -v
```

## 测试 MCP 客户端

```python
import asyncio
from fastmcp import Client
from src.server import mcp


async def test():
    async with Client(mcp) as client:
        tools = await client.list_tools()
        result = await client.call_tool("add", {"a": 5, "b": 3})
        print(f"5 + 3 = {result.data}")


if __name__ == "__main__":
    asyncio.run(test())
```

## 参考资料

- [FastMCP 文档](https://gofastmcp.com/)
- [FastAPI 集成](https://gofastmcp.com/deployment/http#fastapi-integration)
