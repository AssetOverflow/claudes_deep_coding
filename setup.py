"""Setup script for claudes_deep_coding."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="claudes_deep_coding",
    version="0.1.0",
    author="AssetOverflow",
    description="Deep coding agents based on Claude with ChromaDB for long-term memory and RAG",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AssetOverflow/claudes_deep_coding",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "chromadb>=0.4.22",
        "langchain>=0.1.0",
        "langchain-anthropic>=0.1.0",
        "langchain-community>=0.0.20",
        "anthropic>=0.18.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
        ],
    },
)
