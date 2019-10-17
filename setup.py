"""setup.py

Used for installing victoria_pbi via pip.

Author:
    Sam Gibson <sgibson@glasswallsolutions.com>
"""

from setuptools import setup, find_packages

setup(
    dependency_links=[],
    install_requires=[
        "click==7.0", "marshmallow==3.2.1", "azure-devops==5.1.0b4"
    ],
    name="victoria_pbi",
    version="0.1",
    description="Victoria plugin to manipulate Azure DevOps PBIs",
    author="Sam Gibson",
    author_email="sgibson@glasswallsolutions.com",
    packages=find_packages(),
)
