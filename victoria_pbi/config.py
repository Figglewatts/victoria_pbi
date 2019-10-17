"""config.py

Config defines the config for the PBI plugin and a marshmallow schema for
validating the config.

Author:
    Sam Gibson <sgibson@glasswallsolutions.com>
"""

from marshmallow import Schema, fields, post_load


class PBIConfigSchema(Schema):
    """Marshmallow schema for the PBI plugin config."""
    access_token = fields.Str()
    organisation = fields.Str()
    project = fields.Str()
    email = fields.Email()

    @post_load
    def create_pbi_config(self, data, **kwargs):
        return PBIConfig(**data)


class PBIConfig:
    """PBIConfig is the config for the PBI plugin.

    Attributes:
        access_token (str): The access token for the Azure DevOps API.
        organisation (str): The Azure DevOps organisation to use.
        project (str): The Azure DevOps plugin to use.
        email (str): The email the user uses with Azure DevOps.
    """
    def __init__(self, access_token: str, organisation: str, project: str,
                 email: str) -> None:
        self.access_token = access_token
        self.organisation = organisation
        self.project = project
        self.email = email