from click.testing import CliRunner
import pytest

import victoria_pbi.cli
from victoria_pbi.cli import pbi
from victoria_pbi.config import PBIConfig

from conftest import create_mock_api


@pytest.fixture
def cfg_file():
    return PBIConfig("access_token", "organisation", "project",
                     "email@test.com")


@pytest.fixture
def mock_cli(monkeypatch):
    def create_api(*args, **kwargs):
        return create_mock_api(monkeypatch)

    monkeypatch.setattr(victoria_pbi.cli, "AzureDevOpsAPI", create_api)


def test_pbi_cli(cfg_file, mock_cli):
    """Test to see if the CLI runs fine with no args."""
    runner = CliRunner()
    result = runner.invoke(pbi, obj=cfg_file)
    assert result.exit_code == 0


def test_pbi_cli_get(cfg_file, mock_cli):
    """Test to see if we can get a work item."""
    runner = CliRunner()
    result = runner.invoke(pbi, ["get", "100000"], obj=cfg_file)
    assert result.exit_code == 0


def test_pbi_cli_ls(cfg_file, mock_cli):
    """Test to see if we can list work items assigned to a user."""
    runner = CliRunner()
    result = runner.invoke(pbi, ["ls"], obj=cfg_file)
    assert result.exit_code == 0


def test_pbi_cli_ls_user(cfg_file, mock_cli):
    """Test to see if we can list work items assigned to a user."""
    runner = CliRunner()
    result = runner.invoke(pbi, ["ls", "email"], obj=cfg_file)
    assert result.exit_code == 0


def test_pbi_cli_ls_email(cfg_file, mock_cli):
    """Test to see if we can list work items assigned to a user."""
    runner = CliRunner()
    result = runner.invoke(pbi, ["ls", "email@test.com"], obj=cfg_file)
    assert result.exit_code == 0


def test_pbi_cli_columns(cfg_file, mock_cli):
    """Test to see if we can get the columns."""
    runner = CliRunner()
    result = runner.invoke(pbi, ["columns", "DevOps Team"], obj=cfg_file)
    assert result.exit_code == 0


def test_pbi_cli_boards(cfg_file, mock_cli):
    """Test to see if we can list boards."""
    runner = CliRunner()
    result = runner.invoke(pbi, ["boards"], obj=cfg_file)
    assert result.exit_code == 0


def test_pbi_cli_assign_email(cfg_file, mock_cli):
    """Test to see if we can assign a PBI to someone."""
    runner = CliRunner()
    result = runner.invoke(pbi, ["assign", "100000", "test@email.com"],
                           obj=cfg_file)
    assert result.exit_code == 0


def test_pbi_cli_assign_user(cfg_file, mock_cli):
    """Test to see if we can assign a PBI to a user."""
    runner = CliRunner()
    result = runner.invoke(pbi, ["assign", "100000", "test"], obj=cfg_file)
    assert result.exit_code == 0


def test_pbi_cli_mv(cfg_file, mock_cli):
    """Test to see if we can move a PBI."""
    runner = CliRunner()
    result = runner.invoke(pbi, ["mv", "100000", "In Development"],
                           obj=cfg_file)
    assert result.exit_code == 0