"""
EasySQL – setup.py
"""

from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="HandySQL",
    version="1.0.0",
    author="EasySQL Team",
    author_email="easysql@example.com",
    description="A simple and powerful SQL library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/easysql/easysql",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[],          # SQLite ships with Python
    extras_require={
        "mysql":      ["mysql-connector-python>=8.0.0"],
        "postgresql": ["psycopg2-binary>=2.9.0"],
        "all":        ["mysql-connector-python>=8.0.0", "psycopg2-binary>=2.9.0"],
        "dev":        ["pytest>=7.0", "pytest-cov", "black", "flake8", "mypy"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Database",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="sql database sqlite mysql postgresql orm query-builder",
)
