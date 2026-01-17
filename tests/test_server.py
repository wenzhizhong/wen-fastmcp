"""
MCP服务器功能测试
"""

import pytest
import pytest_asyncio
from fastmcp import Client
from src.server import mcp, get_server, configure_auth
from src.auth import AuthConfig


@pytest_asyncio.fixture
async def client():
    """创建测试客户端"""
    async with Client(mcp) as c:
        yield c


@pytest.mark.asyncio
async def test_list_tools(client):
    """测试列出工具"""
    tools = await client.list_tools()
    tool_names = [t.name for t in tools]
    
    assert "add" in tool_names
    assert "multiply" in tool_names
    assert "get_weather" in tool_names
    assert "reverse_text" in tool_names


@pytest.mark.asyncio
async def test_add_tool(client):
    """测试加法工具"""
    result = await client.call_tool("add", {"a": 10, "b": 5})
    assert result.data == 15
    
    result = await client.call_tool("add", {"a": -1, "b": 1})
    assert result.data == 0


@pytest.mark.asyncio
async def test_multiply_tool(client):
    """测试乘法工具"""
    result = await client.call_tool("multiply", {"a": 3.5, "b": 2})
    assert result.data == 7.0


@pytest.mark.asyncio
async def test_get_weather_tool(client):
    """测试天气工具"""
    result = await client.call_tool("get_weather", {"city": "Beijing"})
    assert result.data["city"] == "Beijing"
    assert "temperature" in result.data


@pytest.mark.asyncio
async def test_reverse_text_tool(client):
    """测试反转文本工具"""
    result = await client.call_tool("reverse_text", {"text": "Hello"})
    assert result.data == "olleH"


@pytest.mark.asyncio
async def test_list_resources(client):
    """测试列出资源"""
    resources = await client.list_resources()
    uris = [str(r.uri) for r in resources]
    
    assert "config://app-info" in uris


@pytest.mark.asyncio
async def test_read_resource(client):
    """测试读取资源"""
    content = await client.read_resource("config://app-info")
    assert len(content) > 0
    assert "name" in content[0].text


class TestAuthIntegration:
    """认证集成测试"""
    
    def test_configure_auth(self):
        """测试认证配置"""
        config = AuthConfig(enabled=True, tokens=["test-token"])
        configure_auth(config)
        
        server = get_server()
        assert server.auth is not None
    
    def test_auth_disabled(self):
        """测试禁用认证"""
        config = AuthConfig.disabled()
        configure_auth(config)
        
        server = get_server()
        assert server.auth is None
    
    def test_multiple_tokens(self):
        """测试多个token"""
        config = AuthConfig(enabled=True, tokens=["token1", "token2", "token3"])
        configure_auth(config)
        
        server = get_server()
        assert server.auth is not None
