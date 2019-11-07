from collections import namedtuple

import pytest

import victoria_pbi.pbi

from conftest import WorkItem, create_work_item_container, \
    generate_work_item, WorkItemQueryResult


def test_api_connection(mock_api):
    assert mock_api.connection is not None
    assert mock_api.credentials is not None
    assert mock_api.work_item_client is not None
    assert mock_api.work_client is not None
    assert mock_api.core_client is not None


def test_find_column_field_name(mock_api):
    result = mock_api._find_column_field_name(
        WorkItem({"test_Kanban.Column": "Name"}, 0))
    assert result == "test_Kanban.Column"


def test_get_work_item(mock_api):
    result = mock_api.get_work_item(100000)
    expected = create_work_item_container(generate_work_item(100000))
    assert result == expected


def test_get_unassigned_work_item(mock_api, monkeypatch):
    # patch the client to return an unassigned work item
    def get_unassigned_work_item(*args, **kwargs):
        return generate_work_item(100000, assigned=False)

    monkeypatch.setattr(mock_api.work_item_client, "get_work_item",
                        get_unassigned_work_item)

    result = mock_api.get_work_item(100000)
    expected = create_work_item_container(
        generate_work_item(100000, assigned=False))
    assert result == expected


def test_get_bad_type_work_item(mock_api, monkeypatch):
    # patch the client to return a work item with a bad type
    def get_bad_type_work_item(*args, **kwargs):
        return generate_work_item(100000, work_item_type="Task")

    monkeypatch.setattr(mock_api.work_item_client, "get_work_item",
                        get_bad_type_work_item)

    result = mock_api.get_work_item(100000)
    assert result == None


def test_get_work_items(mock_api):
    result = list(mock_api.get_work_items([1, 2, 3, 4]))
    expected = list([
        create_work_item_container(generate_work_item(number))
        for number in range(100000, 100005)
    ])
    assert len(result) == len(expected)
    for i in range(0, len(result)):
        assert result[i] == expected[i]


def test_get_no_work_items(mock_api):
    result = list(mock_api.get_work_items([]))
    assert len(result) == 0


def test_get_bad_type_work_items(mock_api, monkeypatch):
    # patch the client to return a work item with a bad type
    def get_bad_type_work_items(*args, **kwargs):
        return [generate_work_item(100000, work_item_type="Task")]

    monkeypatch.setattr(mock_api.work_item_client, "get_work_items_batch",
                        get_bad_type_work_items)

    result = list(mock_api.get_work_items([1]))
    assert len(result) == 0


def test_get_user_pbis(mock_api):
    result = list(mock_api.get_user_pbis("email@test.com"))
    expected = list([
        create_work_item_container(generate_work_item(number))
        for number in range(100000, 100005)
    ])
    assert len(result) == len(expected)
    for i in range(0, len(result)):
        assert result[i] == expected[i]


def test_get_user_pbis_none(mock_api, monkeypatch, capsys):
    # patch the client to return no work items
    def get_no_work_items(*args, **kwargs):
        return WorkItemQueryResult([])

    monkeypatch.setattr(mock_api.work_item_client, "query_by_wiql",
                        get_no_work_items)

    result = list(mock_api.get_user_pbis("email@test.com"))
    assert len(result) == 0

    captured = capsys.readouterr()
    assert captured.out == "Could not find any work items for user " \
        "'email@test.com'. Did the user exist?\n"


def test_get_boards(mock_api):
    result = list(mock_api.get_boards())
    assert result == ["DevOps", "QA", "Product"]


def test_get_board_states(mock_api):
    result = list(mock_api.get_board_states("DevOps Team"))
    assert result == ["New", "Approved", "In Dev", "Done"]


def test_move_work_item(mock_api):
    result = mock_api.move_work_item(100000, "In Dev")
    expected = generate_work_item(100000, kanban_column="In Dev")
    assert result.work_item == expected


def test_assign_work_item(mock_api):
    result = mock_api.assign_work_item(100000, "test123@email.com")
    expected = generate_work_item(100000, assigned_to="test123@email.com")
    assert result.work_item == expected