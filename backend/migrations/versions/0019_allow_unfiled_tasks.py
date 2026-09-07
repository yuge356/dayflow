"""Allow executable tasks to sit at the top level with no project.

Revision ID: 0019
Revises: 0018

No longer required by the application. "临时任务" are filed under an
auto-created 临时任务 project instead of being stored without a parent, so the
feature works on a database that never ran this revision — which matters
because Vercel deployments do not run Alembic automatically. The revision is
kept so databases that already applied it stay on a known chain; the relaxed
trigger it installs is harmless, as nothing writes a parentless task.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0019"
down_revision: str | None = "0018"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# Unfiled tasks are the quick "临时任务" captured on the Today page before the
# user decides where they belong. They stay leaves: a subtask under one would
# have no project or module above it.
UNFILED_TASK_FUNCTION = """
CREATE OR REPLACE FUNCTION enforce_task_node_hierarchy()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE parent_type text;
DECLARE grandparent_type text;
BEGIN
  IF NEW.node_type = 'PROJECT' THEN
    IF NEW.parent_id IS NOT NULL THEN
      RAISE EXCEPTION 'projects must stay at the top level'
        USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
  END IF;

  IF NEW.parent_id IS NULL THEN
    IF NEW.node_type <> 'TASK' THEN
      RAISE EXCEPTION 'module nodes require a parent'
        USING ERRCODE = '23514';
    END IF;
    IF EXISTS (
      SELECT 1 FROM tasks c
      WHERE c.parent_id = NEW.id AND c.owner_id = NEW.owner_id AND c.deleted_at IS NULL
    ) THEN
      RAISE EXCEPTION 'only leaf tasks can be left unfiled'
        USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
  END IF;
  SELECT node_type INTO parent_type
  FROM tasks
  WHERE id = NEW.parent_id AND owner_id = NEW.owner_id AND deleted_at IS NULL;

  IF NEW.node_type = 'MODULE' THEN
    IF parent_type IS DISTINCT FROM 'PROJECT' THEN
      RAISE EXCEPTION 'module nodes must be placed under project nodes'
        USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
  END IF;

  -- Executable tasks may sit under a project, a module, or one extra
  -- subtask level: the parent task itself must sit directly under a
  -- project or module, and the moved node must stay a leaf.
  IF parent_type NOT IN ('PROJECT', 'MODULE', 'TASK') THEN
    RAISE EXCEPTION 'task nodes must be placed under project or module nodes'
      USING ERRCODE = '23514';
  END IF;
  IF parent_type = 'TASK' THEN
    SELECT p.node_type INTO grandparent_type
    FROM tasks p
    WHERE p.id = (
      SELECT t.parent_id FROM tasks t
      WHERE t.id = NEW.parent_id AND t.owner_id = NEW.owner_id AND t.deleted_at IS NULL
    ) AND p.owner_id = NEW.owner_id AND p.deleted_at IS NULL;
    IF grandparent_type IS NULL OR grandparent_type = 'TASK' THEN
      RAISE EXCEPTION 'subtasks cannot contain further subtasks'
        USING ERRCODE = '23514';
    END IF;
    IF EXISTS (
      SELECT 1 FROM tasks c
      WHERE c.parent_id = NEW.id AND c.owner_id = NEW.owner_id AND c.deleted_at IS NULL
    ) THEN
      RAISE EXCEPTION 'only leaf tasks can become subtasks'
        USING ERRCODE = '23514';
    END IF;
  END IF;
  RETURN NEW;
END
$$;
"""

FILED_TASK_FUNCTION = """
CREATE OR REPLACE FUNCTION enforce_task_node_hierarchy()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE parent_type text;
DECLARE grandparent_type text;
BEGIN
  IF NEW.node_type = 'PROJECT' THEN
    IF NEW.parent_id IS NOT NULL THEN
      RAISE EXCEPTION 'projects must stay at the top level'
        USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
  END IF;

  IF NEW.parent_id IS NULL THEN
    RAISE EXCEPTION 'module and task nodes require a parent'
      USING ERRCODE = '23514';
  END IF;
  SELECT node_type INTO parent_type
  FROM tasks
  WHERE id = NEW.parent_id AND owner_id = NEW.owner_id AND deleted_at IS NULL;

  IF NEW.node_type = 'MODULE' THEN
    IF parent_type IS DISTINCT FROM 'PROJECT' THEN
      RAISE EXCEPTION 'module nodes must be placed under project nodes'
        USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
  END IF;

  IF parent_type NOT IN ('PROJECT', 'MODULE', 'TASK') THEN
    RAISE EXCEPTION 'task nodes must be placed under project or module nodes'
      USING ERRCODE = '23514';
  END IF;
  IF parent_type = 'TASK' THEN
    SELECT p.node_type INTO grandparent_type
    FROM tasks p
    WHERE p.id = (
      SELECT t.parent_id FROM tasks t
      WHERE t.id = NEW.parent_id AND t.owner_id = NEW.owner_id AND t.deleted_at IS NULL
    ) AND p.owner_id = NEW.owner_id AND p.deleted_at IS NULL;
    IF grandparent_type IS NULL OR grandparent_type = 'TASK' THEN
      RAISE EXCEPTION 'subtasks cannot contain further subtasks'
        USING ERRCODE = '23514';
    END IF;
    IF EXISTS (
      SELECT 1 FROM tasks c
      WHERE c.parent_id = NEW.id AND c.owner_id = NEW.owner_id AND c.deleted_at IS NULL
    ) THEN
      RAISE EXCEPTION 'only leaf tasks can become subtasks'
        USING ERRCODE = '23514';
    END IF;
  END IF;
  RETURN NEW;
END
$$;
"""


def upgrade() -> None:
    """Let an executable task exist without a project above it."""

    if op.get_bind().dialect.name != "postgresql":
        return
    op.execute(UNFILED_TASK_FUNCTION)


def downgrade() -> None:
    """Require every task to sit under a project or module again.

    Existing unfiled rows are filed nowhere, so they must be removed before
    this revision can be reversed on a database that already holds them.
    """

    if op.get_bind().dialect.name != "postgresql":
        return
    op.execute(
        """
        UPDATE tasks SET deleted_at = now()
        WHERE parent_id IS NULL AND node_type = 'TASK' AND deleted_at IS NULL
        """
    )
    op.execute(FILED_TASK_FUNCTION)
