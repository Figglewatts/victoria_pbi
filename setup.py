"""setup.py

Used for installing victoria_pbi via pip.

Author:
    Sam Gibson <sgibson@glasswallsolutions.com>
"""

from setuptools import setup, find_packages

setup(
    dependency_links=[],
    install_requires=[
        'azure-devops==5.1.0b4', 'certifi==2019.9.11', 'chardet==3.0.4',
        'click==7.0', 'colorama==0.4.1', 'idna==2.8', 'isodate==0.6.0',
        'marshmallow==3.2.1', 'msrest==0.6.10', 'oauthlib==3.1.0',
        'pyyaml==5.1.2', 'requests==2.22.0', 'requests-oauthlib==1.2.0',
        'six==1.12.0', 'tabulate==0.8.5', 'urllib3==1.25.6', 'victoria==0.1'
    ],
    name="victoria_pbi",
    version="0.1",
    description="Victoria plugin to manipulate Azure DevOps PBIs",
    author="Sam Gibson",
    author_email="sgibson@glasswallsolutions.com",
    packages=find_packages(),
)