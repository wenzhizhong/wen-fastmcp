"""
工具模块 - 在此目录下添加新的工具文件
每个工具应该是一个函数，使用 @mcp.tool 装饰器
"""

from ..server import mcp


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
