"""setup.py

Used for installing victoria_pbi via pip.

Author:
    Sam Gibson <sgibson@glasswallsolutions.com>
"""
from setuptools import setup, find_packages

setup(
    dependency_links=[],
    install_requires=[
        "victoria", "click", "marshmallow", "azure-devops", "tabulate",
        "colorama"
    ],
    name="victoria_pbi",
    version="0.2.0",
    description="Victoria plugin to manipulate Azure DevOps PBIs",
    author="Sam Gibson",
    author_email="sgibson@glasswallsolutions.com",
    packages=find_packages(),
)