"""
FastAPI MCP Server with STDIO and SSE support.

This example demonstrates how to create an MCP server that can:
1. Run with STDIO transport (default)
2. Run with HTTP/SSE transport via FastAPI
"""

import argparse
import asyncio
from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP


mcp = FastMCP("FastAPI MCP Demo Server")


@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


@mcp.tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


@mcp.tool
def get_weather(city: str) -> dict:
    """Get weather information for a city."""
    return {
        "city": city,
        "temperature": 22,
        "condition": "Sunny",
        "humidity": 65,
    }


@mcp.tool
def reverse_text(text: str) -> str:
    """Reverse the input text."""
    return text[::-1]


@mcp.resource("config://app-info")
def get_app_info() -> dict:
    """Return application information."""
    return {
        "name": "FastAPI MCP Demo",
        "version": "1.0.0",
        "description": "A demo MCP server with FastAPI integration",
    }


app_state = {"server": None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    mcp_app = mcp.http_app(path="/mcp")
    app_state["server"] = mcp_app
    yield
    app_state["server"] = None


def create_fastapi_app() -> FastAPI:
    """Create FastAPI app with MCP mounted."""
    mcp_app = mcp.http_app(path="/mcp")
    
    fastapi_app = FastAPI(
        title="FastAPI MCP Server",
        description="MCP server with stdio and HTTP/SSE transport support",
        lifespan=lifespan,
    )
    
    fastapi_app.mount("/mcp", mcp_app)
    
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @fastapi_app.get("/health")
    async def health_check():
        return {"status": "healthy", "server": "fastapi-mcp"}
    
    @fastapi_app.get("/")
    async def root():
        return {
            "name": "FastAPI MCP Server",
            "endpoints": {
                "health": "/health",
                "mcp_sse": "/mcp/sse",
                "mcp_message": "/mcp/message",
            },
        }
    
    return fastapi_app


def run_stdio():
    """Run MCP server with STDIO transport."""
    print("Starting MCP server with STDIO transport...")
    mcp.run()


def run_sse(host: str = "0.0.0.0", port: int = 8000):
    """Run MCP server with HTTP/SSE transport via FastAPI."""
    print(f"Starting MCP server with HTTP/SSE transport on {host}:{port}")
    app = create_fastapi_app()
    uvicorn.run(app, host=host, port=port)


def main():
    parser = argparse.ArgumentParser(description="FastAPI MCP Server")
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport mode (stdio or sse)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host for SSE transport",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for SSE transport",
    )
    
    args = parser.parse_args()
    
    if args.transport == "stdio":
        run_stdio()
    else:
        run_sse(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
