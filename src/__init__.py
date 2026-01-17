"""
MCP包 - 项目源代码入口
"""

from .server import mcp, get_server, configure_auth
from .app import create_app
from .auth import AuthConfig, create_auth

__all__ = ["mcp", "get_server", "configure_auth", "create_app", "AuthConfig"]
