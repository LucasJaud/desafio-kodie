from fastapi.testclient import TestClient

from app.api.routes.tasks import get_task_classifier
from app.core.config import get_settings
from app.main import app
from app.schemas.task import TaskResponse
from app.services.ai_service import (
    AIProviderError,
    AIResponseError,
    AITimeoutError,
)
from app.services.task_classifier import TaskClassifier

client = TestClient(app)

ENDPOINT = "/api/v1/tasks/organize"
MAX_LENGTH = get_settings().task_request_max_length

RESPONSE_FIELDS = {
    "id",
    "request_text",
    "status",
    "created_at",
    "updated_at",
    "title",
    "description",
    "priority",
    "category",
    "reason",
    "suggested_next_step",
    "due_date",
    "needs_human_review",
}


def test_organize_valid_request_returns_structured_task() -> None:
    response = client.post(
        ENDPOINT,
        json={"request_text": "O relatório mensal precisa ser atualizado até sexta-feira."},
    )

    assert response.status_code == 200
    body = response.json()
    assert set(body) == RESPONSE_FIELDS
    assert body["request_text"] == (
        "O relatório mensal precisa ser atualizado até sexta-feira."
    )
    assert body["status"] == "todo"
    assert body["id"] > 0
    assert body["created_at"]
    assert body["updated_at"]
    assert body["title"] == "O relatório mensal precisa ser atualizado até sexta-feira."
    assert body["description"] == "O relatório mensal precisa ser atualizado até sexta-feira."
    assert body["priority"] in {"critica", "alta", "media", "baixa"}
    assert body["category"] in {
        "incidente",
        "correcao",
        "funcionalidade",
        "melhoria",
        "administrativa",
        "outro",
    }
    assert body["due_date"] is None
    assert body["needs_human_review"] is True
    assert body["reason"]
    assert body["suggested_next_step"]


def test_organize_strips_request_text() -> None:
    response = client.post(ENDPOINT, json={"request_text": "  Atualizar documentação.  "})

    assert response.status_code == 200
    assert response.json()["description"] == "Atualizar documentação."


def test_organize_rejects_empty_text() -> None:
    response = client.post(ENDPOINT, json={"request_text": ""})

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "INVALID_REQUEST"


def test_organize_rejects_whitespace_only_text() -> None:
    response = client.post(ENDPOINT, json={"request_text": "   \n\t  "})

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "INVALID_REQUEST"


def test_organize_rejects_missing_field() -> None:
    response = client.post(ENDPOINT, json={})

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "INVALID_REQUEST"


def test_organize_rejects_unknown_field() -> None:
    response = client.post(
        ENDPOINT,
        json={"request_text": "Tarefa válida.", "priority": "critica"},
    )

    assert response.status_code == 422


def test_organize_accepts_text_at_max_length() -> None:
    response = client.post(ENDPOINT, json={"request_text": "a" * MAX_LENGTH})

    assert response.status_code == 200


def test_organize_rejects_text_above_max_length() -> None:
    response = client.post(ENDPOINT, json={"request_text": "a" * (MAX_LENGTH + 1)})

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "INVALID_REQUEST"


def test_organize_truncates_long_title() -> None:
    response = client.post(ENDPOINT, json={"request_text": "palavra " * 50})

    assert response.status_code == 200
    title = response.json()["title"]
    assert len(title) <= 83
    assert title.endswith("...")


class RaisingClassifier(TaskClassifier):
    def __init__(self, error: Exception) -> None:
        self._error = error

    def classify(self, request_text: str) -> TaskResponse:
        raise self._error


def _override_classifier(error: Exception) -> None:
    app.dependency_overrides[get_task_classifier] = lambda: RaisingClassifier(error)


def test_ai_timeout_returns_504() -> None:
    _override_classifier(AITimeoutError("timeout simulado"))

    response = client.post(ENDPOINT, json={"request_text": "Tarefa válida."})

    assert response.status_code == 504
    assert response.json()["detail"] == {
        "code": "AI_TIMEOUT",
        "message": "O provedor de IA excedeu o tempo limite.",
    }


def test_ai_provider_error_returns_502() -> None:
    _override_classifier(AIProviderError("provedor indisponível"))

    response = client.post(ENDPOINT, json={"request_text": "Tarefa válida."})

    assert response.status_code == 502
    assert response.json()["detail"] == {
        "code": "AI_PROVIDER_ERROR",
        "message": "Não foi possível organizar a tarefa neste momento.",
    }


def test_ai_invalid_response_returns_502() -> None:
    _override_classifier(AIResponseError("resposta inválida"))

    response = client.post(ENDPOINT, json={"request_text": "Tarefa válida."})

    assert response.status_code == 502
    assert response.json()["detail"] == {
        "code": "AI_INVALID_RESPONSE",
        "message": "A resposta da IA não pôde ser validada.",
    }
