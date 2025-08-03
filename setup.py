#!/usr/bin/env python3
"""
Setup script pour El Programming Language
"""

from setuptools import setup, find_packages
import os

# Lire le répertoire actuel
current_dir = os.path.dirname(os.path.abspath(__file__))

setup(
    name="el-language",
    version="1.0.2",
    description="El Programming Language",
    author="AHMED HAFDI",
    author_email="ahmed.hafdi.contact@gmail.com",
    packages=find_packages(),
    py_modules=["el_cli"],  # Inclure explicitement el_cli.py
    entry_points={
        "console_scripts": [
            "el=el_cli:main",
        ],
    },
    python_requires=">=3.8",
    install_requires=[],
    include_package_data=True,
)
