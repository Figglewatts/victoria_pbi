from collections import namedtuple

import azure.devops.connection
import msrest.authentication
import pytest

import victoria_pbi
from victoria_pbi.pbi import WorkItemContainer

WorkItem = namedtuple("WorkItem", ["fields", "id"])


def generate_work_item(number,
                       assigned=True,
                       assigned_to="email@test.com",
                       work_item_type="Product Backlog Item",
                       kanban_column="New"):
    wi = WorkItem(
        {
            "System.Id": number,
            "System.WorkItemType": work_item_type,
            "System.State": "In Development",
            "System.AssignedTo": {
                "uniqueName": assigned_to
            },
            "System.Title": "This is a work item",
            "System.BoardColumn": "In Development",
            "_Kanban.Column": kanban_column
        }, number)
    if not assigned:
        del wi.fields["System.AssignedTo"]
    return wi


def create_work_item_container(work_item):
    expected = WorkItemContainer.__new__(WorkItemContainer)
    expected.id_number = work_item.id
    expected.title = work_item.fields["System.Title"]
    expected.work_type = work_item.fields["System.WorkItemType"]
    if work_item.fields.get("System.AssignedTo") is None:
        expected.assigned_to = "Unassigned"
    else:
        expected.assigned_to = work_item.fields["System.AssignedTo"][
            "uniqueName"]
    expected.state = work_item.fields["System.State"]
    expected.board_column = work_item.fields["System.BoardColumn"]
    expected.work_item = work_item
    return expected


WorkItemQueryResult = namedtuple("WorkItemQueryResult", ["work_items"])

BoardColumn = namedtuple("BoardColumn", ["name"])

WebApiTeam = namedtuple("WebApiTeam", ["name"])


class MockBasicAuthentication:
    def __init__(self, *args, **kwargs):
        pass


class MockClients:
    def get_work_item_tracking_client(self):
        return MockWorkItemClient()

    def get_work_client(self):
        return MockWorkClient()

    def get_core_client(self):
        return MockCoreClient()


class MockWorkItemClient:
    def get_work_item(self, number):
        return generate_work_item(number)

    def get_work_items_batch(self, request):
        return [generate_work_item(number) for number in range(100000, 100005)]

    def query_by_wiql(self, wiql):
        return WorkItemQueryResult(
            [generate_work_item(number) for number in range(100000, 100005)])

    def update_work_item(self, ops, number):
        # we only ever use one operation, so grab the 1st
        op = ops[0]
        wi = generate_work_item(number)

        # if it's an email we need to set uniqueName
        if "@" in op.value:
            # snip off the "/fields/" part of the path given
            wi.fields[op.path[8:]] = {"uniqueName": op.value}
        else:
            wi.fields[op.path[8:]] = op.value
        return wi


class MockWorkClient:
    def get_board_columns(self, team_ctx, board):
        return [
            BoardColumn(name)
            for name in ["New", "Approved", "In Dev", "Done"]
        ]


class MockCoreClient:
    def get_teams(self, project):
        return [WebApiTeam(name) for name in ["DevOps", "QA", "Product"]]


class MockConnection:
    clients = MockClients()

    def __init__(self, *args, **kwargs):
        pass


class MockConfig:
    project = "mocked_project"
    access_token = "mocked_access_token"
    organisation = "mocked_organisation"


def create_mock_api(monkeypatch):
    monkeypatch.setattr(victoria_pbi.pbi, "Connection", MockConnection)
    monkeypatch.setattr(victoria_pbi.pbi, "BasicAuthentication",
                        MockBasicAuthentication)

    return victoria_pbi.pbi.AzureDevOpsAPI(MockConfig())


@pytest.fixture
def mock_api(monkeypatch):
    return create_mock_api(monkeypatch)