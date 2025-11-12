from setuptools import setup, find_packages

setup(
    name="claudes_deep_coding",
    version="0.1.0",
    description="Hierarchical AI agents with planning, persistence, and subagent delegation",
    author="AssetOverflow",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "langchain>=0.1.0",
        "langchain-anthropic>=0.1.0",
        "langgraph>=0.0.20",
        "aiosqlite>=0.19.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
        ]
    },
)
