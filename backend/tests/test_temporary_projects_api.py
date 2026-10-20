"""Temporary-task filing preserves identity and deterministically numbers projects."""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from tests.conftest import profile_today
from tests.test_sessions_api import snapshot
from tests.test_tasks_api import auth_header, register_user


async def create(client: AsyncClient, token: str, title: str, **fields) -> dict:
    response = await client.post("/api/v1/tasks", headers=auth_header(token), json={
        "title": title, "node_type": "TASK", "estimated_seconds": 1800, **fields,
    })
    assert response.status_code == 201, response.text
    return response.json()


async def promote(client: AsyncClient, token: str, task: dict) -> dict:
    response = await client.post(
        f"/api/v1/tasks/{task['id']}/create-project", headers=auth_header(token),
    )
    assert response.status_code == 200, response.text
    return response.json()


async def test_filing_preserves_completion_time_and_is_idempotent(client: AsyncClient):
    token, _ = await register_user(client)
    task = await create(client, token, "阅读")
    started = datetime.now(UTC) - timedelta(minutes=10)
    ended = started + timedelta(minutes=5)
    session_id = str(uuid4())
    response = await client.put(
        f"/api/v1/sessions/{session_id}", headers=auth_header(token),
        json=snapshot(task["id"], str(uuid4()), "COMPLETED", started, ended, 300,
                      ended_at=ended),
    )
    assert response.status_code == 200
    response = await client.patch(
        f"/api/v1/tasks/{task['id']}", headers=auth_header(token), json={"status": "DONE"},
    )
    completed_at = response.json()["completed_at"]
    first = await promote(client, token, task)
    retry = await promote(client, token, task)
    assert first["project_id"] == retry["project_id"]
    nodes = {row["id"]: row for row in retry["tasks"]}
    project = nodes[first["project_id"]]
    original = nodes[task["id"]]
    assert project["title"] == "阅读"
    assert project["status"] == "TODO"  # Visible even when its child is done.
    assert project["actual_seconds"] == original["actual_seconds"] == 300
    assert project["planned_seconds"] == original["estimated_seconds"] == 1800
    assert original["parent_id"] == project["id"]
    assert original["status"] == "DONE"
    assert original["completed_at"] == completed_at
    assert original["created_at"] == task["created_at"]
    assert original["title"] == task["title"]
    assert len(nodes) == 3  # Holding project + original task + one new project.


async def test_duplicate_numbering_uses_source_creation_not_filing_order(
    client: AsyncClient, db_session: AsyncSession,
):
    token, _ = await register_user(client)
    older = await create(client, token, "阅读")
    newer = await create(client, token, "阅读")
    row = await db_session.get(Task, UUID(older["id"]))
    row.created_at = datetime.now(UTC) - timedelta(days=1)
    await db_session.commit()
    second = await promote(client, token, newer)
    first = await promote(client, token, older)
    titles = {row["id"]: row["title"] for row in first["tasks"]}
    assert titles[first["project_id"]] == "阅读（1）"
    assert titles[second["project_id"]] == "阅读（2）"
    third = await create(client, token, "阅读")
    last = await promote(client, token, third)
    titles = {row["id"]: row["title"] for row in last["tasks"]}
    assert titles[last["project_id"]] == "阅读（3）"


async def test_existing_project_and_daily_snapshot_renames(
    client: AsyncClient, db_session: AsyncSession,
):
    token, _ = await register_user(client)
    existing = await create(client, token, "阅读", node_type="PROJECT")
    row = await db_session.get(Task, UUID(existing["id"]))
    row.created_at = datetime.now(UTC) - timedelta(days=2)
    await db_session.commit()
    task = await create(client, token, "阅读")
    item_ids = []
    for offset in [-1, 0, 1]:
        day = (profile_today() + timedelta(days=offset)).isoformat()
        plan = await client.post(
            "/api/v1/daily-plans", headers=auth_header(token), json={"plan_date": day},
        )
        item = await client.post(
            f"/api/v1/daily-plans/{plan.json()['id']}/items", headers=auth_header(token),
            json={"task_id": task["id"], "title": "阅读", "estimated_seconds": 1800},
        )
        assert item.status_code == 201, item.text
        item_ids.append((day, item.json()["id"]))
    result = await promote(client, token, task)
    nodes = {row["id"]: row for row in result["tasks"]}
    assert nodes[existing["id"]]["title"] == "阅读（1）"
    assert nodes[result["project_id"]]["title"] == "阅读（2）"
    for index, (day, item_id) in enumerate(item_ids):
        plan = await client.get(
            f"/api/v1/daily-plans/by-date/{day}", headers=auth_header(token),
        )
        item = next(row for row in plan.json()["items"] if row["id"] == item_id)
        assert item["title"] == ("阅读" if index == 0 else "阅读（2）/阅读")
        assert item["task_id"] == task["id"]


async def test_owner_isolation_and_already_filed_rejection(client: AsyncClient):
    token, _ = await register_user(client, "one")
    other, _ = await register_user(client, "two")
    task = await create(client, token, "阅读")
    hidden = await client.post(
        f"/api/v1/tasks/{task['id']}/create-project", headers=auth_header(other),
    )
    assert hidden.status_code == 404
    other_task = await create(client, other, "阅读")
    await promote(client, other, other_task)
    result = await promote(client, token, task)
    assert next(row for row in result["tasks"]
                if row["id"] == result["project_id"])["title"] == "阅读"
    filed = await create(client, token, "已归类", parent_id=result["project_id"])
    rejected = await client.post(
        f"/api/v1/tasks/{filed['id']}/create-project", headers=auth_header(token),
    )
    assert rejected.status_code == 409


@pytest.mark.parametrize("title", ["临时任务", "字" * 200, "阅读（1）"])
async def test_reserved_and_long_titles_remain_visible_and_unique(client: AsyncClient, title: str):
    token, _ = await register_user(client)
    one = await create(client, token, title)
    two = await create(client, token, title)
    first = await promote(client, token, one)
    second = await promote(client, token, two)
    projects = [row for row in second["tasks"]
                if row["id"] in [first["project_id"], second["project_id"]]]
    assert len({row["title"] for row in projects}) == 2
    assert all(len(row["title"]) <= 200 and row["title"] != "临时任务" for row in projects)
