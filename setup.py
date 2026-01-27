from setuptools import setup, find_packages

setup(
    name="postkit",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
        "pyyaml>=6.0",
        "atproto>=0.0.40",
        "markdown>=3.4.0",
    ],
    entry_points={
        "console_scripts": [
            "postkit=postkit.cli:main",
        ],
    },
)