"""pbi.py

This module contains the wrapper functions for interacting with the Azure
DevOps API.

Author:
    Sam Gibson <sgibson@glasswallsolutions.com>
"""

import json
import logging
from typing import Generator, List
from urllib.parse import quote

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.released.work_item_tracking import WorkItemTrackingClient
from azure.devops.v5_1.work_item_tracking import WorkItem, WorkItemQueryResult,\
    Wiql, WorkItemBatchGetRequest
from azure.devops.v5_1.work_item_tracking.models import JsonPatchOperation
from azure.devops.released.work import WorkClient
from azure.devops.v5_1.work import TeamContext
from azure.devops.exceptions import AzureDevOpsServiceError

from .config import PBIConfig

AZURE_DEVOPS_URL = "https://dev.azure.com/{0}/"
"""The URL of Azure DevOps to substitute the organisation into."""

ALLOWED_WORK_ITEM_TYPES = ["Product Backlog Item", "Bug"]
"""Which work item types do we allow the user to get. Some of them might be
missing fields which we need, so instead of putting a bunch of messy handling
code in we'll just stop the user from getting them."""


class WorkItemContainer:
    """WorkItemContainer is used as a wrapper for an Azure DevOps work item.

    Attributes:
        id_number (int): The ID number of the work item.
        title (str): The title of the work item.
        work_type (str): The type of the work item.
        assigned_to (str): The unique name of who the work item is assigned to.
            This is usually their email.
        state (str): The current state of the work item.
        board_column (str): Which board column the work item is in.
        work_item (WorkItem): The Azure DevOps work item used to generate this.
    """
    def __init__(self, work_item: WorkItem) -> None:
        """Create a WorkItemContainer from an Azure DevOps WorkItem.

        Args:
            work_item (WorkItem): The WorkItem to create this container from.
        """
        self.id_number = work_item.id
        self.title = work_item.fields["System.Title"]
        self.work_type = work_item.fields["System.WorkItemType"]

        # if the work item is unassigned the field will not be present
        if work_item.fields.get("System.AssignedTo") is not None:
            self.assigned_to = work_item.fields["System.AssignedTo"][
                "uniqueName"]
        else:
            self.assigned_to = "Unassigned"

        self.state = work_item.fields["System.State"]
        self.board_column = work_item.fields["System.BoardColumn"]
        self.work_item = work_item

    def __str__(self):
        return f"#{self.id_number} ({self.work_type}):" + \
            f" {self.title}, {self.assigned_to} => {self.board_column}"

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.id_number == other.id_number \
                and self.title == other.title \
                and self.work_type == other.work_type \
                and self.assigned_to == other.assigned_to \
                and self.state == other.state \
                and self.board_column == other.board_column \
                and self.work_item == other.work_item
        return False


class AzureDevOpsAPI:
    """A connection to the Azure DevOps API.

    Parameters:
        credentials (BasicAuthentication): The credentials used to connect.
        connection (Connection): The actual connection to the API.
        work_item_client (WorkItemTrackingClient): A client for work item tracking.
        work_client (WorkClient): A client for work tracking.
    """
    def __init__(self, cfg: PBIConfig) -> None:
        """Connect to the Azure DevOps API using the PBI config.

        Args:
            project (str): The Azure DevOps project to use.
            cfg (PBIConfig): The config to use to connect to the API.
        """
        self.project = cfg.project
        self._connect(cfg.access_token, cfg.organisation)

    def _connect(self, access_token: str, organisation: str):
        """Connect to the Azure DevOps API.

        Args:
            access_token (str): The access token to authenticate with.
            organisation (str): The Azure DevOps organisation to use.
        """
        self.credentials = BasicAuthentication("", access_token)
        self.connection = Connection(
            base_url=AZURE_DEVOPS_URL.format(organisation),
            creds=self.credentials)
        self.work_item_client = self.connection.clients\
            .get_work_item_tracking_client()
        self.work_client = self.connection.clients.get_work_client()
        self.core_client = self.connection.clients.get_core_client()

    def _find_column_field_name(self, work_item: WorkItem) -> str:
        """The field on a work item that stores which Kanban column it's in
        has a weird name that changes. This function is used to extract the name
        of that field for any work item so we can change it.

        Args:
            work_item (WorkItem): The work item to get the field name from.

        Returns:
            str: The name of the field on this work item.
        """
        for field in work_item.fields.keys():
            if field.endswith("_Kanban.Column"):
                return field

    def get_work_item(self, number: int) -> WorkItemContainer:
        """Get a work item by ID.

        Args:
            number (int): The ID number of the work item.
            client (WorkItemTrackingClient): The 
        """
        work_item = self.work_item_client.get_work_item(number)
        if work_item.fields["System.WorkItemType"] \
                not in ALLOWED_WORK_ITEM_TYPES:
            logging.error(f"Work item #{number} was not a PBI or a Bug")
            return None
        return WorkItemContainer(work_item)

    def get_work_items(self, numbers: List[int]
                       ) -> Generator[WorkItemContainer, None, None]:
        """Get multiple work items by ID.

        Args:
            numbers (List[int]): The list of IDs to get.

        Yields:
            WorkItemContainer: Work items.
        """
        if len(numbers) == 0:
            return

        try:
            result = self.work_item_client.get_work_items_batch(
                WorkItemBatchGetRequest(ids=numbers,
                                        fields=[
                                            "System.Id", "System.Title",
                                            "System.WorkItemType",
                                            "System.AssignedTo",
                                            "System.State",
                                            "System.BoardColumn"
                                        ]))
            for work_item in result:
                if work_item.fields["System.WorkItemType"] \
                        not in ALLOWED_WORK_ITEM_TYPES:
                    logging.error(
                        f"Work item #{work_item.id} was not a PBI or a Bug")
                    continue
                yield WorkItemContainer(work_item)
        except AzureDevOpsServiceError as err:
            logging.error(err)

    def get_user_pbis(self,
                      email: str) -> Generator[WorkItemContainer, None, None]:
        """Get all of the PBIs assigned to a user.

        Args:
            email (str): The email of the user whose PBIs to get.

        Yields:
            WorkItemContainer: Work items assigned to the user.
        """
        result = self.work_item_client.query_by_wiql(
            Wiql(f"""SELECT [System.ID], [System.Title] 
                    FROM workitems 
                    WHERE [System.AssignedTo]='{email}' 
                    AND [System.State]<>'Done' 
                    AND [System.State]<>'Removed'
                    AND ([System.WorkItemType]='Product Backlog Item'
                        OR [System.WorkitemType]='Bug')"""))
        if len(result.work_items) == 0:
            print(f"Could not find any work items for user '{email}'."
                  " Did the user exist?")

        return self.get_work_items([item.id for item in result.work_items])

    def get_boards(self) -> Generator[str, None, None]:
        """Get all boards from the organisation.

        Yields:
            str: Board names.

        Raises:
            AzureDevOpsServiceError: If there was some error getting the boards.
        """
        try:
            for board in self.core_client.get_teams(self.project):
                yield board.name
        except AzureDevOpsServiceError as err:
            logging.error(err)
            raise

    def get_board_states(self, board: str) -> Generator[str, None, None]:
        """Get all possible states of the board.

        Args:
            board (str): The board to get states for.

        Yields:
            str: Board states of the board.

        Raises:
            AzureDevOpsServiceError: If there was some error getting the states.
        """
        try:
            result = self.work_client.get_board_columns(
                TeamContext(project=self.project, team=board), "Backlog items")
            for column in result:
                yield column.name
        except AzureDevOpsServiceError as err:
            logging.error(err)
            raise

    def move_work_item(self, number: int, state: str) -> WorkItemContainer:
        """Move a work item to a given board column.

        Args:
            number (int): The ID of the work item.
            state (str): The board column to move it to.

        Returns:
            WorkItemContainer: The moved work item.
        """
        field_name = self._find_column_field_name(
            self.get_work_item(number).work_item)

        op = JsonPatchOperation(op="add",
                                path=f"/fields/{field_name}",
                                value=state)
        result = self.work_item_client.update_work_item([op], number)
        return WorkItemContainer(result)

    def assign_work_item(self, number: int, email: str):
        """Assign a work item to a user by email.

        Args:
            number (int): The work item ID.
            email (str): The email of the user to assign the item to.

        Returns:
            WorkItemContainer: The assigned work item.
        """
        op = JsonPatchOperation(op="add",
                                path="/fields/System.AssignedTo",
                                value=email)
        try:
            result = self.work_item_client.update_work_item([op], number)
        except AzureDevOpsServiceError as err:
            logging.error(err)
            return None
        return WorkItemContainer(result)