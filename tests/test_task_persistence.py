from fastapi.testclient import TestClient

from app.main import app
from app.schemas.task import TaskStatus
from app.services.task_repository import TaskRepository

client = TestClient(app)
ENDPOINT = "/api/v1/tasks"


def create_task(request_text: str = "Atualizar o relatório mensal.") -> dict:
    response = client.post(
        f"{ENDPOINT}/organize",
        json={"request_text": request_text},
    )
    assert response.status_code == 200
    return response.json()


def test_organized_task_is_persisted_across_repository_instances(
    database_path,
) -> None:
    original_text = "  Preparar a apresentação até sexta-feira.  "
    created = create_task(original_text)

    reopened_repository = TaskRepository(database_path)
    persisted = reopened_repository.get(created["id"])

    assert persisted is not None
    assert persisted.request_text == original_text
    assert persisted.title == created["title"]
    assert persisted.description == original_text.strip()
    assert persisted.status is TaskStatus.TODO
    assert persisted.created_at.isoformat() == created["created_at"]
    assert persisted.updated_at.isoformat() == created["updated_at"]


def test_list_tasks_filters_by_status_and_priority() -> None:
    first = create_task("Tarefa que permanece a fazer.")
    second = create_task("Outra tarefa para concluir.")
    client.patch(f"{ENDPOINT}/{second['id']}", json={"status": "done"})

    response = client.get(f"{ENDPOINT}?status=todo&priority=media")

    assert response.status_code == 200
    assert [task["id"] for task in response.json()] == [first["id"]]


def test_task_can_be_edited_and_moved_between_columns() -> None:
    created = create_task()

    response = client.patch(
        f"{ENDPOINT}/{created['id']}",
        json={
            "title": "Preparar relatório revisado",
            "description": "Conferir os dados antes do envio.",
            "status": "in_progress",
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Preparar relatório revisado"
    assert response.json()["description"] == "Conferir os dados antes do envio."
    assert response.json()["status"] == "in_progress"


def test_patch_requires_at_least_one_editable_field() -> None:
    created = create_task()

    response = client.patch(f"{ENDPOINT}/{created['id']}", json={})

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "INVALID_REQUEST"


def test_delete_removes_task_and_unknown_task_returns_404() -> None:
    created = create_task()

    response = client.delete(f"{ENDPOINT}/{created['id']}")

    assert response.status_code == 204
    assert client.get(f"{ENDPOINT}/{created['id']}").status_code == 404
    assert client.delete(f"{ENDPOINT}/{created['id']}").status_code == 404
