"""
Installs packages needed for this program to run on users computer. Done through python installer *pip*

To install: python setup.py install
To build: python setup.py.build
"""
# Always prefer setuptools over distutils
from setuptools import setup, find_packages

setup(
    name = 'Create Products',
    Version = '1.0.0',
    description = 'Update existing products for backgroundtown',
    author = 'feahnthor',
    license = 'MIT',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
    ],
    keywords = 'helium, automation, update',
    packages = find_packages(include=['PySide6','python-json-logger', 'selenium', 'numpy', 'toml']), # necessary for this program to run at all
    install_requires = ['PySide6', 'python-json-logger', 'selenium', 'numpy', 'toml'],
    python_requires = '>=3.6'
    )