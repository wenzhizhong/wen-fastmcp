"""
提示词模块 - 在此目录下添加新的提示词
每个提示词应该是一个函数，使用 @mcp.prompt 装饰器
"""

from ..server import mcp


@mcp.prompt
def analyze_code(code: str, language: str = "python") -> str:
    """Analyze code and provide improvements."""
    return f"""Please analyze the following {language} code and provide feedback:

```{language}
{code}
```

Consider:
1. Code structure and readability
2. Potential bugs or issues
3. Performance considerations
4. Best practices
"""


@mcp.prompt
def summarize_text(text: str, max_length: int = 100) -> str:
    """Summarize the given text."""
    return f"""Please summarize the following text in {max_length} words or less:

{text}

Summary:"""


@mcp.prompt
def translate_text(text: str, target_language: str = "English") -> str:
    """Translate text to the target language."""
    return f"""Please translate the following text to {target_language}:

{text}

Translation:"""


@mcp.prompt
def generate_questions(topic: str, num_questions: int = 3) -> str:
    """Generate practice questions about a topic."""
    return f"""Generate {num_questions} practice questions about {topic}. For each question, provide the answer as well.

Questions:"""


@mcp.prompt
def create_essay_outline(topic: str, essay_type: str = "argumentative") -> str:
    """Create an essay outline for a given topic."""
    return f"""Create an outline for a {essay_type} essay about {topic}.

Include:
1. Introduction with thesis statement
2. Main body paragraphs (3-4 points)
3. Counter-arguments (if applicable)
4. Conclusion

Outline:"""
