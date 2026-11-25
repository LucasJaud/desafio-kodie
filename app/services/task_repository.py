import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator

from app.schemas.task import (
    Priority,
    StoredTaskResponse,
    TaskResponse,
    TaskStatus,
    TaskUpdate,
)

logger = logging.getLogger(__name__)


class TaskRepositoryError(Exception):
    """Falha controlada ao ler ou gravar tarefas persistidas."""


class TaskRepository:
    """Repositório SQLite para solicitações organizadas."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        try:
            self.database_path.parent.mkdir(parents=True, exist_ok=True)
            self._initialize()
        except OSError as exc:
            logger.exception("Não foi possível preparar o armazenamento de tarefas.")
            raise TaskRepositoryError("Falha ao preparar o armazenamento.") from exc

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        try:
            connection = sqlite3.connect(self.database_path, timeout=10)
            connection.row_factory = sqlite3.Row
            try:
                with connection:
                    yield connection
            finally:
                connection.close()
        except sqlite3.Error as exc:
            logger.exception("Falha SQLite no armazenamento de tarefas.")
            raise TaskRepositoryError("Falha ao acessar o armazenamento.") from exc

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_text TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    priority TEXT NOT NULL CHECK (
                        priority IN ('critica', 'alta', 'media', 'baixa')
                    ),
                    category TEXT NOT NULL CHECK (
                        category IN (
                            'incidente', 'correcao', 'funcionalidade',
                            'melhoria', 'administrativa', 'outro'
                        )
                    ),
                    reason TEXT NOT NULL,
                    suggested_next_step TEXT NOT NULL,
                    due_date TEXT,
                    needs_human_review INTEGER NOT NULL CHECK (
                        needs_human_review IN (0, 1)
                    ),
                    status TEXT NOT NULL DEFAULT 'todo' CHECK (
                        status IN ('todo', 'in_progress', 'done')
                    ),
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_status_created "
                "ON tasks(status, created_at DESC)"
            )

    def health_check(self) -> None:
        with self._connection() as connection:
            connection.execute("SELECT 1").fetchone()

    def create(
        self, request_text: str, task: TaskResponse
    ) -> StoredTaskResponse:
        task_data = task.model_dump(mode="json")
        now = datetime.now(timezone.utc).isoformat()
        with self._connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO tasks (
                    request_text, title, description, priority, category, reason,
                    suggested_next_step, due_date, needs_human_review, status,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request_text,
                    task_data["title"],
                    task_data["description"],
                    task_data["priority"],
                    task_data["category"],
                    task_data["reason"],
                    task_data["suggested_next_step"],
                    task_data["due_date"],
                    int(task_data["needs_human_review"]),
                    TaskStatus.TODO.value,
                    now,
                    now,
                ),
            )
            row = connection.execute(
                "SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
        return self._to_task(row)

    def list_tasks(
        self,
        status: TaskStatus | None = None,
        priority: Priority | None = None,
    ) -> list[StoredTaskResponse]:
        conditions: list[str] = []
        values: list[str] = []
        if status is not None:
            conditions.append("status = ?")
            values.append(status.value)
        if priority is not None:
            conditions.append("priority = ?")
            values.append(priority.value)
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        with self._connection() as connection:
            rows = connection.execute(
                f"SELECT * FROM tasks {where} ORDER BY created_at DESC, id DESC",
                values,
            ).fetchall()
        return [self._to_task(row) for row in rows]

    def get(self, task_id: int) -> StoredTaskResponse | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
        return self._to_task(row) if row is not None else None

    def update(
        self, task_id: int, update: TaskUpdate
    ) -> StoredTaskResponse | None:
        changes = update.model_dump(mode="json", exclude_none=True)
        changes["updated_at"] = datetime.now(timezone.utc).isoformat()
        assignments = ", ".join(f"{column} = ?" for column in changes)
        values = [*changes.values(), task_id]
        with self._connection() as connection:
            cursor = connection.execute(
                f"UPDATE tasks SET {assignments} WHERE id = ?", values
            )
            if cursor.rowcount == 0:
                return None
            row = connection.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
        return self._to_task(row)

    def delete(self, task_id: int) -> bool:
        with self._connection() as connection:
            cursor = connection.execute(
                "DELETE FROM tasks WHERE id = ?", (task_id,)
            )
        return cursor.rowcount > 0

    @staticmethod
    def _to_task(row: sqlite3.Row) -> StoredTaskResponse:
        values = dict(row)
        values["needs_human_review"] = bool(values["needs_human_review"])
        return StoredTaskResponse.model_validate(values)
