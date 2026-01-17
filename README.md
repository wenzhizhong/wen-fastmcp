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

            # List tools
            tools = await session.list_tools()
            print(f"Tools: {[t.name for t in tools]}")

            # Call tool
            result = await session.call_tool("add", {"a": 5, "b": 3})
            print(f"Result: {result.content[0].text}")


asyncio.run(main())
```

For a complete example, see [examples/stdio_client_example.py](examples/stdio_client_example.py).

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
python main.py --transport sse --host 0.0.0.0 --port 8000
```

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

When running with SSE transport:

- `GET /` - Root endpoint with available routes
- `GET /health` - Health check
- `GET /mcp/sse` - SSE endpoint
- `POST /mcp/message` - Message endpoint

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
