"""
认证模块测试
"""

import os
import pytest
import tempfile
from src.auth import AuthConfig, create_auth, AUTH_TOKEN_ENV


class TestAuthConfig:
    """AuthConfig测试类"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = AuthConfig()
        assert config.enabled is True
        assert config.tokens == []
        assert config.require_auth is True
    
    def test_config_with_tokens(self):
        """测试带token的配置"""
        config = AuthConfig(enabled=True, tokens=["token1", "token2"])
        assert len(config.tokens) == 2
        assert "token1" in config.tokens
        assert "token2" in config.tokens
    
    def test_add_token(self):
        """测试添加token"""
        config = AuthConfig(enabled=True)
        config.add_token("my-token")
        config.add_token("another-token", scopes=["read", "write"])
        assert len(config.tokens) == 2
        assert "my-token" in config.tokens
    
    def test_validate_valid(self):
        """测试有效配置验证"""
        config = AuthConfig(enabled=True, tokens=["token"])
        assert config.validate() is True
        
        config = AuthConfig(enabled=False)
        assert config.validate() is True
    
    def test_validate_invalid(self):
        """测试无效配置验证"""
        config = AuthConfig(enabled=True, tokens=[], require_auth=True)
        assert config.validate() is False
    
    def test_disabled_config(self):
        """测试禁用认证配置"""
        config = AuthConfig.disabled()
        assert config.enabled is False
        assert config.require_auth is False
    
    def test_create_auth_disabled(self):
        """测试创建禁用状态的认证"""
        config = AuthConfig.disabled()
        auth = create_auth(config)
        assert auth is None
    
    def test_create_auth_enabled(self):
        """测试创建启用状态的认证"""
        config = AuthConfig(enabled=True, tokens=["test-token"])
        auth = create_auth(config)
        assert auth is not None
        assert auth.__class__.__name__ == "StaticTokenVerifier"
    
    def test_create_auth_invalid(self):
        """测试创建无效认证"""
        config = AuthConfig(enabled=True, tokens=[], require_auth=True)
        with pytest.raises(ValueError):
            create_auth(config)
    
    def test_from_env_single_token(self, monkeypatch):
        """测试从环境变量加载单个token"""
        monkeypatch.setenv(AUTH_TOKEN_ENV, "env-token")
        config = AuthConfig.from_env()
        assert config.enabled is True
        assert "env-token" in config.tokens
    
    def test_from_env_multiple_tokens(self, monkeypatch):
        """测试从环境变量加载多个token"""
        os.environ[f"{AUTH_TOKEN_ENV}S"] = "token1, token2, token3"
        config = AuthConfig.from_env()
        assert len(config.tokens) == 3
        del os.environ[f"{AUTH_TOKEN_ENV}S"]
    
    def test_from_env_no_token(self, monkeypatch):
        """测试无环境变量时加载"""
        monkeypatch.delenv(AUTH_TOKEN_ENV, raising=False)
        config = AuthConfig.from_env()
        assert config.enabled is False
        assert config.tokens == []
    
    def test_from_file(self):
        """测试从文件加载配置"""
        import json
        config_data = {
            "enabled": True,
            "tokens": ["file-token-1", "file-token-2"],
            "require_auth": True
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            f.flush()
            f_name = f.name
        
        try:
            config = AuthConfig.from_file(f_name)
            assert config.enabled is True
            assert len(config.tokens) == 2
        finally:
            try:
                os.unlink(f_name)
            except PermissionError:
                pass
    
    def test_save_to_file(self):
        """测试保存配置到文件"""
        config = AuthConfig(enabled=True, tokens=["save-token"])
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name
        
        try:
            config.save_to_file(path)
            
            import json
            with open(path, "r") as f:
                data = json.load(f)
            
            assert data["enabled"] is True
            assert "save-token" in data["tokens"]
        finally:
            os.unlink(path)
    
    def test_from_file_not_found(self):
        """测试文件不存在时加载"""
        config = AuthConfig.from_file("/nonexistent/path.json")
        assert config.enabled is False


class TestCreateAuth:
    """create_auth函数测试"""
    
    def test_create_auth_with_scopes(self):
        """测试创建带scopes的认证"""
        config = AuthConfig(enabled=True)
        config.add_token("token", scopes=["read", "write"])
        auth = create_auth(config)
        assert auth is not None


class TestMainExit:
    """main.py退出行为测试"""

    def test_main_no_token_exits(self, monkeypatch, capsys):
        """测试启用了认证但没有token时程序退出"""
        import subprocess
        import sys
        
        # 不设置任何token环境变量
        monkeypatch.delenv("MCP_AUTH_TOKEN", raising=False)
        monkeypatch.delenv("MCP_AUTH_TOKENS", raising=False)
        
        # 运行main.py，不传递token参数
        result = subprocess.run(
            [sys.executable, "main.py", "--transport", "stdio"],
            capture_output=True,
            text=True,
            env={}  # 不传递任何环境变量
        )
        
        # 应该返回非零退出码
        assert result.returncode != 0
        assert "ERROR" in result.stdout or "ERROR" in result.stderr

    def test_main_with_token_succeeds(self, monkeypatch, tmp_path):
        """测试提供了token时程序正常启动"""
        import subprocess
        import sys
        
        # 设置token
        env = {"MCP_AUTH_TOKEN": "test-token"}
        
        # 使用超时进程测试
        result = subprocess.run(
            [sys.executable, "main.py", "--transport", "stdio"],
            capture_output=True,
            text=True,
            env={**os.environ, **env},
            timeout=3
        )
        
        # 应该正常启动
        assert "Authentication enabled" in result.stdout

    def test_main_no_auth_succeeds(self, monkeypatch, tmp_path):
        """测试禁用认证时程序正常启动"""
        import subprocess
        import sys
        
        result = subprocess.run(
            [sys.executable, "main.py", "--transport", "stdio", "--no-auth"],
            capture_output=True,
            text=True,
            timeout=3
        )
        
        # 应该正常启动
        assert "Authentication disabled" in result.stdout
