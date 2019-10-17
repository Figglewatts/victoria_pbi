"""config.py

A Victoria plugin to manipulate Azure DevOps PBIs.

Author:
    Sam Gibson <sgibson@glasswallsolutions.com>
"""

import click
from victoria.plugin import Plugin
import yaml

from .config import PBIConfigSchema
from . import cli

# this object is loaded by Victoria and used as the plugin entry point
plugin = Plugin(name="pbi", cli=cli.pbi, config_schema=PBIConfigSchema())
