#!/usr/bin/env python3
"""
阿里云CVE爬虫安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

# 读取requirements文件
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="AliyunCVE_Crawler",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="阿里云漏洞库CVE数据爬虫工具",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/vistaminc/AliyunCVE_Crawler",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "isort>=5.12.0",
        ],
        "monitoring": [
            "schedule>=1.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "aliyuncve-crawler=main:main",
        ],
    },
    keywords="cve, vulnerability, security, crawler, aliyun",
    project_urls={
        "Bug Reports": "https://github.com/vistaminc/AliyunCVE_Crawler/issues",
        "Source": "https://github.com/vistaminc/AliyunCVE_Crawler",
        "Documentation": "https://github.com/vistaminc/AliyunCVE_Crawler/blob/main/docs/",
    },
)
