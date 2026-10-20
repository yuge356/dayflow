"""Atomically file temporary tasks without copying their timing records."""

from datetime import UTC, datetime
from uuid import NAMESPACE_URL, UUID, uuid5

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskNodeType, TaskStatus
from app.models.daily_plan import DailyPlan, DailyPlanItem
from app.models.user import User
from app.services.analytics import resolve_timezone
from app.services.daily_plans import project_prefixed_task_title
from app.services.tasks import get_owned_task

INBOX_TITLE = "临时任务"


def temporary_project_id(owner_id: UUID, task_id: UUID) -> UUID:
    """A stable identity makes retries safe even after a lost HTTP response."""
    return uuid5(NAMESPACE_URL, f"dayflow:temporary-project:{owner_id}:{task_id}")


def numbered_title(title: str, number: int) -> str:
    suffix = f"（{number}）"
    return title[: 200 - len(suffix)] + suffix


async def create_temporary_project(
    db: AsyncSession, owner_id: UUID, task_id: UUID, timezone_name: str,
) -> UUID:
    # Serialize simultaneous promotions for this owner, including from other
    # devices. No schema change or additional provenance table is necessary.
    await db.scalar(select(User.id).where(User.id == owner_id).with_for_update())
    task = await get_owned_task(db, owner_id, task_id)
    project_id = temporary_project_id(owner_id, task_id)
    existing = await db.get(Task, project_id)
    if existing is not None:
        if existing.deleted_at is None and task.parent_id == project_id:
            return project_id
        raise HTTPException(409, "此任务已创建过项目，请在项目页查看或重新归类。")

    owned = list((await db.scalars(select(Task).where(
        Task.owner_id == owner_id, Task.deleted_at.is_(None),
    ))).all())
    by_id = {row.id: row for row in owned}
    old_titles = {row.id: project_prefixed_task_title(row, by_id) for row in owned}
    parent = next((row for row in owned if row.id == task.parent_id), None)
    if task.node_type != TaskNodeType.TASK or (
        task.parent_id is not None
        and not (parent and parent.node_type == TaskNodeType.PROJECT
                 and parent.title == INBOX_TITLE)
    ):
        raise HTTPException(409, "只有尚未归入项目的临时任务可以创建独立项目。")

    project = Task(
        id=project_id,
        owner_id=owner_id,
        node_type=TaskNodeType.PROJECT,
        title=task.title,
        status=TaskStatus.TODO,
        sort_order=max((row.sort_order for row in owned if row.parent_id is None),
                       default=-1) + 1,
    )
    db.add(project)
    await db.flush()
    task.parent_id = project.id
    task.sort_order = 0
    owned.append(project)

    # The original task keeps its name, ID, creation date, status and sessions.
    # Recover each generated project's source by its deterministic identity.
    sources = {
        temporary_project_id(owner_id, row.id): row
        for row in owned if row.node_type == TaskNodeType.TASK
    }
    base = task.title

    def belongs(row: Task) -> bool:
        if row.node_type != TaskNodeType.PROJECT or row.parent_id is not None:
            return False
        if row.title == INBOX_TITLE and row.id != project_id:
            return False
        return row.title == base or any_number(row.title)

    def any_number(title: str) -> bool:
        if not title.endswith("）") or "（" not in title:
            return False
        number = title.rsplit("（", 1)[1][:-1]
        return number.isascii() and number.isdigit() and (
            title == numbered_title(base, int(number))
        )

    family = [row for row in owned if belongs(row)]
    if len(family) > 1 or base == INBOX_TITLE:
        def creation_key(row: Task) -> tuple:
            source = sources.get(row.id)
            original = source if source and source.parent_id == row.id else row
            # SQLite tests use naive datetimes; production Postgres uses UTC.
            return (original.created_at.replace(tzinfo=UTC), str(original.id))

        family.sort(key=creation_key)
        occupied = {row.title for row in owned
                    if row.node_type == TaskNodeType.PROJECT and row not in family}
        number = 1
        for row in family:
            while numbered_title(base, number) in occupied:
                number += 1
            row.title = numbered_title(base, number)
            occupied.add(row.title)
            number += 1
    await db.flush()
    by_id[project.id] = project
    changed_titles = {
        row.id: project_prefixed_task_title(row, by_id)
        for row in owned
        if row.id in old_titles
        and old_titles[row.id] != project_prefixed_task_title(row, by_id)
    }
    if changed_titles:
        today = datetime.now(resolve_timezone(timezone_name)).date()
        items = await db.scalars(select(DailyPlanItem).join(
            DailyPlan, DailyPlan.id == DailyPlanItem.daily_plan_id,
        ).where(
            DailyPlan.owner_id == owner_id,
            DailyPlan.plan_date >= today,
            DailyPlan.deleted_at.is_(None),
            DailyPlanItem.owner_id == owner_id,
            DailyPlanItem.task_id.in_(changed_titles),
            DailyPlanItem.deleted_at.is_(None),
        ))
        for item in items:
            item.title = changed_titles[item.task_id]
        await db.flush()
    return project.id
