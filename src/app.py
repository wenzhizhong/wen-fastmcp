"""
FastAPI应用模块 - HTTP/SSE传输支持
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP

from .server import mcp


@asynccontextmanager
async def lifespan(app: FastAPI):
    mcp_app = mcp.http_app(path="/mcp")
    app.state.mcp_app = mcp_app
    yield
    app.state.mcp_app = None


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    mcp_app = mcp.http_app(path="/mcp")
    
    app = FastAPI(
        title="FastAPI MCP Server",
        description="MCP server with stdio and HTTP/SSE transport support",
        lifespan=lifespan,
    )
    
    app.mount("/mcp", mcp_app)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "server": "fastapi-mcp"}
    
    @app.get("/")
    async def root():
        return {
            "name": "FastAPI MCP Server",
            "version": "1.0.0",
            "endpoints": {
                "health": "/health",
                "mcp_sse": "/mcp/sse",
                "mcp_message": "/mcp/message",
            },
        }
    
    return app
