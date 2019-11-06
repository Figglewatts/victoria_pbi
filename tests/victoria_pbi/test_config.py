import pytest

from victoria_pbi.config import PBIConfigSchema, PBIConfig

CONFIG_SCHEMA = PBIConfigSchema()


def test_create_pbiconfig():
    result = CONFIG_SCHEMA.load({
        "access_token": "test",
        "organisation": "test",
        "project": "test",
        "email": "test@test.com"
    })
    assert result == PBIConfig("test", "test", "test", "test@test.com")
