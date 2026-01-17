"""
Pytest配置文件
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pytest_plugins = ["pytest_asyncio"]


@pytest.fixture(scope="session")
def event_loop_policy():
    """使用默认的事件循环策略"""
    import asyncio
    return asyncio.DefaultEventLoopPolicy()
