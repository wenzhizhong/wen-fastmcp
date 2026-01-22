"""Prompt 组件调用示例

演示如何使用 MCP 的 Prompt 功能。
Prompt 不是直接调用的，而是返回提示词模板供 LLM 使用。
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.server import mcp


async def main():
    """主函数 - 演示 Prompt 用法"""
    print("=" * 50)
    print("MCP Prompt Example")
    print("=" * 50)
    print()

    try:
        print("Listing prompts...")
        prompts = await mcp.get_prompts()
        print(f"Prompts: {list(prompts.keys())}")
        print()

        print("Using 'summarize_text' prompt...")
        detail = prompts.get("summarize_text")
        if detail:
            result = await detail.render(arguments={
                "text": "Machine Context Protocol (MCP) is an emerging standard for AI assistants to communicate with external tools and data sources. It provides a unified interface for AI models to access tools, resources, and prompts in a consistent manner.",
                "max_length": 50
            })
            if result:
                content = result[0].content
                text = content.text if hasattr(content, "text") else str(content)
                print(f"Rendered prompt:\n{text}")
            print()

        print("Using 'generate_questions' prompt...")
        detail = prompts.get("generate_questions")
        if detail:
            result = await detail.render(arguments={
                "topic": "Python programming",
                "num_questions": 2
            })
            if result:
                content = result[0].content
                text = content.text if hasattr(content, "text") else str(content)
                print(f"Rendered prompt:\n{text}")
            print()

        print("Using 'create_essay_outline' prompt...")
        detail = prompts.get("create_essay_outline")
        if detail:
            result = await detail.render(arguments={
                "topic": "Artificial Intelligence",
                "essay_type": "informative"
            })
            if result:
                content = result[0].content
                text = content.text if hasattr(content, "text") else str(content)
                print(f"Rendered prompt:\n{text}")
            print()

        print("Using 'analyze_code' prompt...")
        detail = prompts.get("analyze_code")
        if detail:
            result = await detail.render(arguments={
                "code": "def fib(n):\n    if n <= 1:\n        return n\n    return fib(n-1) + fib(n-2)",
                "language": "python"
            })
            if result:
                content = result[0].content
                text = content.text if hasattr(content, "text") else str(content)
                print(f"Rendered prompt:\n{text}")
            print()

        print("Using 'translate_text' prompt...")
        detail = prompts.get("translate_text")
        if detail:
            result = await detail.render(arguments={
                "text": "你好，世界！",
                "target_language": "English"
            })
            if result:
                content = result[0].content
                text = content.text if hasattr(content, "text") else str(content)
                print(f"Rendered prompt:\n{text}")
            print()

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    print()
    print("Done!")


if __name__ == "__main__":
    print("Starting MCP prompt example...")
    print()
    asyncio.run(main())
