"""cli.py

This is the module that contains the Click CLI for the PBI plugin.

Author:
    Sam Gibson <sgibson@glasswallsolutions.com
"""
import logging
from typing import List, Iterable

import click
import colorama
from tabulate import tabulate

from .config import PBIConfig
from .pbi import AzureDevOpsAPI, AzureDevOpsServiceError, WorkItemContainer


@click.group()
@click.pass_obj
def pbi(cfg: PBIConfig):
    """Manipulate Azure DevOps PBIs."""
    colorama.init()


@pbi.command()
@click.argument('id', nargs=-1, type=int, required=True)
@click.pass_obj
def get(cfg: PBIConfig, id: List[int]):
    """Get work item(s) by ID."""
    conn = AzureDevOpsAPI(cfg)
    print_work_items(conn.get_work_items(id))


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
    print_work_items(conn.get_user_pbis(user))


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


def print_work_items(work_items: Iterable[WorkItemContainer]):
    headers = ["ID", "Type", "Title", "State", "Assignee"]
    table = []
    for work_item in work_items:
        item_type = "PBI" if work_item.work_type == "Product Backlog Item" \
            else work_item.work_type

        # figure out which colour to print the state as
        state_colour = colorama.Fore.WHITE
        if work_item.state == "New" or work_item.state == "Approved":
            state_colour = colorama.Fore.LIGHTWHITE_EX
        elif work_item.board_column == "On Hold":
            state_colour = colorama.Fore.RED
        elif work_item.state == "In Development":
            state_colour = colorama.Fore.YELLOW
        elif work_item.state == "Validation":
            state_colour = colorama.Fore.BLUE
        elif work_item.state == "Done":
            state_colour = colorama.Fore.GREEN
        state = f"{state_colour}● {colorama.Style.RESET_ALL}{work_item.board_column}"

        table.append([
            f"#{work_item.id_number}", item_type, work_item.title, state,
            work_item.assigned_to
        ])
    print(tabulate(table, headers, tablefmt="plain"))