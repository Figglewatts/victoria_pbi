"""cli.py

This is the module that contains the Click CLI for the PBI plugin.

Author:
    Sam Gibson <sgibson@glasswallsolutions.com
"""
import logging
from typing import List

import click

from .config import PBIConfig
from .pbi import AzureDevOpsAPI, AzureDevOpsServiceError


@click.group()
@click.pass_obj
def pbi(cfg: PBIConfig):
    """Manipulate Azure DevOps PBIs."""
    pass


@pbi.command()
@click.argument('id', nargs=-1, type=int, required=True)
@click.pass_obj
def get(cfg: PBIConfig, id: List[int]):
    """Get work item(s) by ID."""
    conn = AzureDevOpsAPI(cfg)
    for work_item in conn.get_work_items(id):
        print(work_item)


@pbi.command()
@click.argument('user', nargs=1, type=str, required=False, default=None)
@click.pass_obj
def ls(cfg: PBIConfig, user: str):
    """List work items. Optionally specify USER to get work items for."""
    if user is None:
        # if no user is specified, use the one in the config
        user = cfg.email
    elif user.find("@") == -1:
        # if the user specified wasn't an email, add the domain from the config
        user += "@" + cfg.email.split("@")[1]

    conn = AzureDevOpsAPI(cfg)
    for work_item in conn.get_user_pbis(user):
        print(work_item)


@pbi.command()
@click.argument('board', nargs=1, type=str, required=True)
@click.pass_obj
def columns(cfg: PBIConfig, board: str):
    """List BOARD columns."""
    conn = AzureDevOpsAPI(cfg)
    try:
        for col in conn.get_board_states(board):
            print(col)
    except AzureDevOpsServiceError:
        print("\tTry running 'victoria pbi boards' to view all boards.")


@pbi.command()
@click.pass_obj
def boards(cfg: PBIConfig):
    """List boards."""
    conn = AzureDevOpsAPI(cfg)
    try:
        for board in conn.get_boards():
            print(board)
    except AzureDevOpsServiceError:
        return


@pbi.command()
@click.argument('id', nargs=-1, type=int, required=True)
@click.argument('user', nargs=1, type=str, required=True)
@click.pass_obj
def assign(cfg: PBIConfig, id: List[int], user: str):
    """Assign work item(s) to someone by IDs and USER."""
    if user.find("@") == -1:
        # if the user specified wasn't an email, add the domain from the config
        user += "@" + cfg.email.split("@")[1]

    conn = AzureDevOpsAPI(cfg)
    for pbi_id in id:
        conn.assign_work_item(pbi_id, user)


@pbi.command()
@click.argument('id', nargs=-1, type=int, required=True)
@click.argument('column', nargs=1, type=str, required=True)
@click.pass_obj
def mv(cfg: PBIConfig, id: List[int], column: str):
    """Move work item(s) by IDs to a different COLUMN."""
    conn = AzureDevOpsAPI(cfg)
    try:
        for pbi_id in id:
            conn.move_work_item(pbi_id, column)
    except AzureDevOpsServiceError as err:
        if err.message.startswith("TF401320"):
            logging.error(
                f"Could not move work item: column '{column}' did not exist")
        else:
            logging.error(err)