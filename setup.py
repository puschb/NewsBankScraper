#!/usr/bin/env python3
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="newsbank-scraper",
    version="0.1.0",
    author="User",
    author_email="user@example.com",
    description="A scraper for NewsBank articles",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/user/newsbank-scraper",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "newsbank-scraper=NewsbankScraper.main:main",
        ],
    },
    # Include sample configs in the package
    package_data={
        '': ['Configs/*.json'],
    },
)