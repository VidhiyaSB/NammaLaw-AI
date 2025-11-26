from setuptools import setup, find_packages

setup(
    name="tamilguardian",
    version="1.0.0",
    description="AI Legal Assistant for Tamil Nadu",
    author="TamilGuardian Team",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "gradio>=4.44.0",
        "fastapi>=0.104.1",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
        "httpx>=0.25.2",
        "openai>=1.3.7",
        "sentence-transformers>=2.2.2",
        "faiss-cpu>=1.7.4",
        "PyPDF2>=3.0.1",
        "python-docx>=1.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "black",
            "flake8",
        ]
    },
    entry_points={
        "console_scripts": [
            "tamilguardian=app:main",
        ],
    },
)