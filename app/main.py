from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import tasks
from app.api.routes.tasks import RepositoryDep
from app.core.config import get_settings
from app.services.task_repository import TaskRepositoryError

settings = get_settings()
STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API de organização inteligente de tarefas.",
)

app.include_router(tasks.router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def kanban_board() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(
    _request: Request, _exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "detail": {
                "code": "INVALID_REQUEST",
                "message": (
                    "A requisição está ausente ou contém campos inválidos."
                ),
            }
        },
    )


@app.exception_handler(TaskRepositoryError)
async def handle_task_repository_error(
    _request: Request, _exc: TaskRepositoryError
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "detail": {
                "code": "TASK_STORAGE_ERROR",
                "message": "Não foi possível acessar as tarefas salvas.",
            }
        },
    )


@app.get("/health", tags=["health"])
def health(repository: RepositoryDep) -> dict[str, str]:
    repository.health_check()
    return {"status": "ok"}
