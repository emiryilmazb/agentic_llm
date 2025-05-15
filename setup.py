"""
Agentic LLM - Setup Script

This script configures the package for installation.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="agentic_llm",
    version="0.1.0",
    author="Agentic LLM Team",
    author_email="example@example.com",
    description="An agentic character chatbot platform with dynamic tool creation capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/agentic_llm",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "agentic_llm=main:main",
        ],
    },
    include_package_data=True,
)