"""
项目入口文件 - 支持stdio、sse和http三种传输模式
"""

import argparse
import os
import sys
import uvicorn
from src import mcp, configure_auth, create_app, AuthConfig


def run_stdio():
    """Run MCP server with STDIO transport."""
    print("Starting MCP server with STDIO transport...")
    mcp.run()


def run_sse(host: str = "0.0.0.0", port: int = 8000):
    """Run MCP server with HTTP/SSE transport via FastAPI."""
    print(f"Starting MCP server with HTTP/SSE transport on {host}:{port}")
    app = create_app()
    uvicorn.run(app, host=host, port=port)


def run_http(host: str = "0.0.0.0", port: int = 8000):
    """Run MCP server with Streamable-HTTP transport."""
    print(f"Starting MCP server with Streamable-HTTP transport on {host}:{port}")
    mcp.run(transport="streamable-http", host=host, port=port)


def main():
    parser = argparse.ArgumentParser(description="FastAPI MCP Server")
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "sse", "http"],
        default="stdio",
        help="Transport mode (stdio, sse, or http)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host for HTTP/SSE transport",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP/SSE transport",
    )
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="Authentication token (can be used multiple times)",
        dest="tokens",
        action="append",
    )
    parser.add_argument(
        "--no-auth",
        action="store_true",
        help="Disable authentication (not recommended)",
    )
    parser.add_argument(
        "--env-file",
        type=str,
        default=".env",
        help="Path to .env file for loading MCP_AUTH_TOKEN",
    )

    args = parser.parse_args()

    if args.no_auth:
        config = AuthConfig.disabled()
        configure_auth(config)
        print("Authentication disabled")
    else:
        tokens = args.tokens or []
        if not tokens:
            tokens = os.environ.get("MCP_AUTH_TOKEN", "").split(",")
            tokens = [t.strip() for t in tokens if t.strip()]

        if tokens:
            config = AuthConfig(enabled=True, tokens=tokens)
            configure_auth(config)
            print(f"Authentication enabled with {len(tokens)} token(s)")
        else:
            print("ERROR: Authentication is enabled but no token provided!")
            print("Please set --token or MCP_AUTH_TOKEN environment variable")
            sys.exit(1)

    if args.transport == "stdio":
        run_stdio()
    elif args.transport == "http":
        run_http(host=args.host, port=args.port)
    else:
        run_sse(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
