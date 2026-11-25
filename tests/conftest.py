import pytest
from fastapi.testclient import TestClient

from app.api.routes.tasks import get_task_classifier, get_task_repository
from app.main import app
from app.services.task_classifier import MockTaskClassifier
from app.services.task_repository import TaskRepository


@pytest.fixture
def database_path(tmp_path):
    return tmp_path / "test-tasks.sqlite3"


@pytest.fixture
def task_repository(database_path):
    return TaskRepository(database_path)


@pytest.fixture(autouse=True)
def isolate_dependencies(task_repository):
    """Isola IA e banco de dados para cada teste."""
    app.dependency_overrides[get_task_classifier] = MockTaskClassifier
    app.dependency_overrides[get_task_repository] = lambda: task_repository
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
