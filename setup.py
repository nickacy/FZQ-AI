from setuptools import setup, find_packages

setup(
    name="fzq_ai_agent",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pydantic>=2.0",
        "fastapi",
        "uvicorn",
        "requests",
        "aiohttp",
        "feedparser",
        "pyyaml",
        "python-dotenv",
    ],
)
