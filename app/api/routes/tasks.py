from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.core.config import get_settings
from app.schemas.task import (
    Priority,
    StoredTaskResponse,
    TaskRequest,
    TaskStatus,
    TaskUpdate,
)
from app.services.ai_service import (
    AIProviderError,
    AIResponseError,
    AIService,
    AITimeoutError,
)
from app.services.task_classifier import (
    AITaskClassifier,
    MockTaskClassifier,
    TaskClassifier,
)
from app.services.task_repository import TaskRepository

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


def get_task_classifier() -> TaskClassifier:
    """Fornece o classificador conforme o provedor configurado."""
    settings = get_settings()
    if settings.ai_provider.strip().lower() == "mock":
        return MockTaskClassifier()
    return AITaskClassifier(AIService(settings))


@lru_cache
def get_task_repository() -> TaskRepository:
    return TaskRepository(get_settings().database_path)


ClassifierDep = Annotated[TaskClassifier, Depends(get_task_classifier)]
RepositoryDep = Annotated[TaskRepository, Depends(get_task_repository)]


@router.post("/organize", response_model=StoredTaskResponse)
def organize_task(
    payload: TaskRequest,
    classifier: ClassifierDep,
    repository: RepositoryDep,
) -> StoredTaskResponse:
    try:
        task = classifier.classify(payload.request_text.strip())
    except AITimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail={
                "code": "AI_TIMEOUT",
                "message": "O provedor de IA excedeu o tempo limite.",
            },
        ) from exc
    except AIResponseError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "code": "AI_INVALID_RESPONSE",
                "message": "A resposta da IA não pôde ser validada.",
            },
        ) from exc
    except AIProviderError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "code": "AI_PROVIDER_ERROR",
                "message": "Não foi possível organizar a tarefa neste momento.",
            },
        ) from exc
    return repository.create(payload.request_text, task)


@router.get("", response_model=list[StoredTaskResponse])
def list_tasks(
    repository: RepositoryDep,
    status: TaskStatus | None = None,
    priority: Priority | None = None,
) -> list[StoredTaskResponse]:
    return repository.list_tasks(status=status, priority=priority)


@router.get("/{task_id}", response_model=StoredTaskResponse)
def get_task(task_id: int, repository: RepositoryDep) -> StoredTaskResponse:
    task = repository.get(task_id)
    if task is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "TASK_NOT_FOUND", "message": "Tarefa não encontrada."},
        )
    return task


@router.patch("/{task_id}", response_model=StoredTaskResponse)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    repository: RepositoryDep,
) -> StoredTaskResponse:
    task = repository.update(task_id, payload)
    if task is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "TASK_NOT_FOUND", "message": "Tarefa não encontrada."},
        )
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, repository: RepositoryDep) -> None:
    if not repository.delete(task_id):
        raise HTTPException(
            status_code=404,
            detail={"code": "TASK_NOT_FOUND", "message": "Tarefa não encontrada."},
        )
