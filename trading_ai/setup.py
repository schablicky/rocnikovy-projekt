# trading_ai/setup.py
from setuptools import setup, find_packages

setup(
    name="trading_ai",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'tensorflow',
        'numpy',
        'pandas',
        'metaapi-cloud-sdk',
        'tf-agents'
    ]
)