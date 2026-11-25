from abc import ABC, abstractmethod

from app.schemas.task import Category, Priority, TaskResponse
from app.services.ai_service import AIService


class TaskClassifier(ABC):
    """Contrato do serviço que transforma texto em tarefa estruturada."""

    @abstractmethod
    def classify(self, request_text: str) -> TaskResponse:
        """Classifica a solicitação e devolve uma tarefa validada."""


class AITaskClassifier(TaskClassifier):
    """Classificador que delega a extração ao provedor de IA configurado."""

    def __init__(self, service: AIService) -> None:
        self._service = service

    def classify(self, request_text: str) -> TaskResponse:
        return self._service.organize(request_text)


class MockTaskClassifier(TaskClassifier):
    """Classificador provisório da Etapa 1, sem chamada a provedor de IA.

    Mantém o contrato da API verificável até a integração real (Etapa 2).
    A resposta é explicitamente marcada para revisão humana, pois não há
    classificação automática nesta etapa.
    """

    def classify(self, request_text: str) -> TaskResponse:
        return TaskResponse(
            title=_build_title(request_text),
            description=request_text,
            priority=Priority.MEDIA,
            category=Category.OUTRO,
            reason=(
                "Classificação provisória de desenvolvimento (AI_PROVIDER=mock); "
                "a prioridade deve ser revisada por uma pessoa."
            ),
            suggested_next_step="Revisar a solicitação e confirmar a prioridade.",
            due_date=None,
            needs_human_review=True,
        )


def _build_title(request_text: str, limit: int = 80) -> str:
    lines = request_text.strip().splitlines()
    first_line = lines[0] if lines else ""
    normalized = " ".join(first_line.split()) or "Solicitação recebida"
    if len(normalized) <= limit:
        return normalized
    truncated = normalized[: limit - 3].rsplit(" ", 1)[0]
    return f"{truncated or normalized[: limit - 3]}..."
