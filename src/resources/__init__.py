"""
资源模块 - 在此目录下添加新的资源文件
每个资源应该是一个函数，使用 @mcp.resource 装饰器
"""

from ..server import mcp


@mcp.resource("config://app-info")
def get_app_info() -> dict:
    """Return application information."""
    return {
        "name": "FastAPI MCP Demo",
        "version": "1.0.0",
        "description": "A demo MCP server with FastAPI integration",
    }
