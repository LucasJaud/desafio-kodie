from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.config import get_settings


class Priority(str, Enum):
    CRITICA = "critica"
    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"


class Category(str, Enum):
    INCIDENTE = "incidente"
    CORRECAO = "correcao"
    FUNCIONALIDADE = "funcionalidade"
    MELHORIA = "melhoria"
    ADMINISTRATIVA = "administrativa"
    OUTRO = "outro"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskRequest(BaseModel):
    """Solicitação em linguagem natural enviada pelo solicitante."""

    model_config = ConfigDict(extra="forbid")

    request_text: str = Field(min_length=1)

    @field_validator("request_text")
    @classmethod
    def validate_max_length(cls, value: str) -> str:
        limit = get_settings().task_request_max_length
        if not value.strip():
            raise ValueError("request_text não pode ficar vazio.")
        if len(value) > limit:
            raise ValueError(f"request_text deve ter no máximo {limit} caracteres.")
        return value


class TaskResponse(BaseModel):
    """Tarefa estruturada devolvida pela API."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    description: str
    priority: Priority
    category: Category
    reason: str
    suggested_next_step: str
    due_date: date | None = None
    needs_human_review: bool


class StoredTaskResponse(TaskResponse):
    """Tarefa persistida, incluindo origem e estado no quadro."""

    id: int = Field(gt=0)
    request_text: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime


class TaskUpdate(BaseModel):
    """Campos que podem ser editados no cartão do Kanban."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    status: TaskStatus | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=4000)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is not None and not value:
            raise ValueError("title não pode ficar vazio.")
        return value

    @model_validator(mode="after")
    def require_update(self) -> "TaskUpdate":
        if self.status is None and self.title is None and self.description is None:
            raise ValueError("Informe ao menos um campo para atualizar.")
        return self
