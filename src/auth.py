"""
认证模块 - 支持Bearer Token认证
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from fastmcp.server.auth import StaticTokenVerifier, TokenVerifier


AUTH_TOKEN_ENV = "MCP_AUTH_TOKEN"


@dataclass
class BearerToken:
    """Bearer Token配置"""
    token: str
    scopes: list[str] = field(default_factory=list)


@dataclass
class AuthConfig:
    """
    认证配置类
    
    示例:
        # 从环境变量加载token
        config = AuthConfig.from_env()
        
        # 启用Bearer Token认证
        config = AuthConfig(
            enabled=True,
            tokens=["secret-token-1", "secret-token-2"]
        )
        
        # 从配置文件加载
        config = AuthConfig.from_file("config.json")
    """
    enabled: bool = True
    tokens: List[str] = field(default_factory=list)
    require_auth: bool = True
    
    @classmethod
    def from_env(cls, env_var: str = AUTH_TOKEN_ENV) -> "AuthConfig":
        """
        从环境变量加载认证配置
        
        环境变量支持:
        - MCP_AUTH_TOKEN: 单个token
        - MCP_AUTH_TOKENS: 逗号分隔的多个token
        """
        token = os.environ.get(env_var)
        tokens_str = os.environ.get(f"{env_var}S", "")
        
        tokens: List[str] = []
        if token:
            tokens.append(token)
        if tokens_str:
            tokens.extend([t.strip() for t in tokens_str.split(",") if t.strip()])
        
        enabled = bool(tokens)
        return cls(enabled=enabled, tokens=tokens)
    
    @classmethod
    def from_file(cls, path: str) -> "AuthConfig":
        """从JSON文件加载认证配置"""
        import json
        try:
            with open(path, "r") as f:
                data = json.load(f)
            return cls(
                enabled=data.get("enabled", True),
                tokens=data.get("tokens", []),
                require_auth=data.get("require_auth", True)
            )
        except FileNotFoundError:
            return cls(enabled=False)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in {path}")
    
    @classmethod
    def disabled(cls) -> "AuthConfig":
        """返回禁用认证的配置"""
        return cls(enabled=False, require_auth=False)
    
    def save_to_file(self, path: str):
        """保存配置到JSON文件"""
        import json
        data = {
            "enabled": self.enabled,
            "tokens": self.tokens,
            "require_auth": self.require_auth
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    
    def add_token(self, token: str, scopes: list[str] = None):
        """添加一个token"""
        if scopes is None:
            scopes = []
        self.tokens.append(token)
    
    def validate(self) -> bool:
        """验证配置是否有效"""
        if self.require_auth and self.enabled and not self.tokens:
            return False
        return True
    
    def _create_verifier(self) -> Optional[TokenVerifier]:
        """创建Token验证器"""
        if not self.enabled or not self.tokens:
            if self.require_auth:
                raise ValueError("Authentication is required but no tokens configured")
            return None
        
        token_map: Dict[str, Dict[str, Any]] = {
            token: {"scopes": []} for token in self.tokens
        }
        return StaticTokenVerifier(tokens=token_map)


def create_auth(config: AuthConfig) -> Optional[TokenVerifier]:
    """创建认证实例"""
    if not config.validate():
        raise ValueError("Invalid auth configuration")
    return config._create_verifier()
