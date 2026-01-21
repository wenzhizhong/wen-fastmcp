# FastAPI MCP Demo

A demonstration of MCP (Model Context Protocol) server with FastAPI integration, supporting both STDIO and SSE transports.

[English](README.md) | [简体中文](README_CN.md)

## Installation

```bash
uv pip install -e .
```

## Usage

### STDIO Transport (Default)

Run the MCP server using STDIO transport:

```bash
# Without authentication
python main.py --transport stdio

# With authentication (single token)
python main.py --transport stdio --token "your-secret-token"

# With authentication (multiple tokens)
python main.py --transport stdio --token "token1" --token "token2"
```

#### Client Usage (Python)

**Streamable-HTTP Mode (Recommended):**

```python
from fastmcp import Client

async def main():
    # 直接传递 URL 和 token
    async with Client("http://localhost:8001/mcp", None, auth="your-token") as client:
        tools = await client.list_tools()
        print(f"Tools: {[t.name for t in tools]}")

        result = await client.call_tool("add", {"a": 5, "b": 3})
        print(f"Result: {result.data}")

asyncio.run(main())
```

**SSE Mode:**

```python
from mcp.client.sse import sse_client
from mcp import ClientSession
import asyncio

async def main():
    async with sse_client(url="http://localhost:8000/mcp/sse", headers={"Authorization": "Bearer your-token"}) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print(f"Tools: {[t.name for t in tools.tools]}")

            result = await session.call_tool("add", {"a": 5, "b": 3})
            print(f"Result: {result.content[0].text}")

asyncio.run(main())
```

For a complete example, see [examples/streamable_http_client_example.py](examples/streamable_http_client_example.py) and [examples/sse_client_example.py](examples/sse_client_example.py).

#### Claude Desktop Configuration

Add to your Claude Desktop config:

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

### SSE/HTTP Transport

Run the MCP server using SSE/HTTP transport via FastAPI:

```bash
# Using SSE transport (direct FastMCP)
python main.py --transport sse --host 0.0.0.0 --port 8000
```

#### API Endpoints

**SSE Mode (port 8000):**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mcp/sse` | GET | SSE stream endpoint |
| `/mcp/messages` | POST | Message endpoint (JSON-RPC) |

**Note:** SSE transport requires a complete session flow:
1. Client establishes SSE connection first (GET `/mcp/sse`), gets `session_id`
2. Subsequent requests carry `session_id` header (`X-Mcp-Session-Id`)
3. Responses are returned via SSE stream

## Authentication

Authentication is enabled by default. Tokens can be configured in multiple ways:

### Command Line

```bash
# Single token
python main.py --transport stdio --token "your-secret-token"
python main.py --transport sse --token "your-secret-token"

# Multiple tokens
python main.py --transport stdio --token "token1" --token "token2" --token "token3"
```

### Environment Variables

```bash
# Single token
set MCP_AUTH_TOKEN=your-secret-token

# Multiple tokens (comma-separated)
set MCP_AUTH_TOKENS=token1,token2,token3
```

### Disable Authentication

```bash
python main.py --transport stdio --no-auth
python main.py --transport sse --no-auth
```

**Note:** When authentication is enabled but no token is provided, the server will exit immediately with an error message.

### Config File

Create a `config.json` file:

```json
{
  "enabled": true,
  "tokens": ["your-secret-token"],
  "require_auth": true
}
```

Load it programmatically:

```python
from src.auth import AuthConfig
config = AuthConfig.from_file("config.json")
```

## Available Tools

- `add(a, b)` - Add two numbers
- `multiply(a, b)` - Multiply two numbers
- `get_weather(city)` - Get weather for a city
- `reverse_text(text)` - Reverse input text

## Available Resources

- `config://app-info` - Application information

## API Endpoints

When running with SSE transport via FastAPI:

- `GET /` - Root endpoint with available routes
- `GET /health` - Health check
- `GET /mcp/sse` - SSE stream endpoint
- `POST /mcp/messages` - JSON-RPC message endpoint

## Project Structure

```
src/
├── server.py        # MCP server instance
├── app.py           # FastAPI application
├── auth.py          # Authentication config
├── tools/           # Tool implementations
│   └── __init__.py
└── resources/       # Resource implementations
    └── __init__.py
tests/
├── conftest.py      # Pytest fixtures
├── test_auth.py     # Auth tests
└── test_server.py   # Server tests
```

## Adding New Tools

Edit `src/tools/__init__.py`:

```python
from ..server import mcp

@mcp.tool
def my_tool(param: str) -> str:
    """My new tool."""
    return param.upper()
```

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_auth.py::TestAuthConfig::test_default_config -v
```

## Testing with MCP Client

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

## References

- [FastMCP Documentation](https://gofastmcp.com/)
- [FastAPI Integration](https://gofastmcp.com/deployment/http#fastapi-integration)
