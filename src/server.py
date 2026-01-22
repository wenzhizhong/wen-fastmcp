"""
MCP服务器模块 - 统一的MCP服务器实例
"""

from fastmcp import FastMCP
from typing import Optional
from .auth import AuthConfig, create_auth, AUTH_TOKEN_ENV

import os

_auth_config: Optional[AuthConfig] = None
_mcp_instance: Optional[FastMCP] = None


def configure_auth(config: AuthConfig):
    """配置认证"""
    global _auth_config, _mcp_instance
    if not config.validate():
        raise ValueError("Invalid auth configuration")
    _auth_config = config
    _mcp_instance = None


def get_server(name: str = "FastAPI MCP Demo Server", auth_config: AuthConfig = None) -> FastMCP:
    """获取MCP服务器实例"""
    global _mcp_instance, _auth_config
    
    config = auth_config or _auth_config
    
    if config is None:
        config = AuthConfig.from_env()
        if not config.enabled:
            config = AuthConfig.disabled()
    
    if _mcp_instance is None:
        auth = create_auth(config)
        _mcp_instance = FastMCP(name, auth=auth)
        _auth_config = config
    
    return _mcp_instance


mcp = get_server()

from . import tools  # noqa: F401
from . import resources  # noqa: F401
from . import prompts  # noqa: F401
