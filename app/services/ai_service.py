import json
import logging
from typing import Any

import httpx
from pydantic import ValidationError

from app.core.config import Settings
from app.schemas.task import TaskResponse
from app.services.prompt import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Base para falhas controladas do serviço de IA."""


class AIProviderError(AIServiceError):
    """Falha de configuração, rede ou resposta HTTP do provedor."""


class AITimeoutError(AIServiceError):
    """Timeout na chamada ao provedor."""


class AIResponseError(AIServiceError):
    """Resposta do provedor não pôde ser validada."""


class AIService:
    """Cliente genérico para provedores compatíveis com OpenAI."""

    def __init__(self, settings: Settings, client: httpx.Client | None = None) -> None:
        self._settings = settings
        self._client = client

    def organize(self, request_text: str) -> TaskResponse:
        self._validate_configuration()

        payload: dict[str, Any] = {
            "model": self._settings.ai_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request_text},
            ],
            "temperature": self._settings.ai_temperature,
            "max_tokens": self._settings.ai_max_tokens,
        }
        if self._settings.ai_json_mode:
            payload["response_format"] = {"type": "json_object"}

        response = self._post(payload)
        content = self._extract_content(response)
        data = self._parse_json(content)

        try:
            return TaskResponse.model_validate(data)
        except ValidationError as exc:
            logger.warning("Resposta da IA fora do schema esperado.")
            raise AIResponseError("A resposta da IA não pôde ser validada.") from exc

    def _validate_configuration(self) -> None:
        if not self._settings.ai_base_url.strip():
            raise AIProviderError("AI_BASE_URL não configurada.")
        if not self._settings.ai_model.strip():
            raise AIProviderError("AI_MODEL não configurado.")

    def _post(self, payload: dict[str, Any]) -> httpx.Response:
        url = f"{self._settings.ai_base_url.rstrip('/')}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self._settings.ai_api_key:
            headers["Authorization"] = f"Bearer {self._settings.ai_api_key}"

        try:
            if self._client is not None:
                response = self._client.post(url, json=payload, headers=headers)
            else:
                with httpx.Client(timeout=self._settings.ai_timeout_seconds) as client:
                    response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            logger.warning("Timeout ao chamar o provedor de IA.")
            raise AITimeoutError("O provedor de IA excedeu o tempo limite.") from exc
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "Provedor de IA retornou HTTP %s.", exc.response.status_code
            )
            raise AIProviderError("O provedor de IA retornou um erro.") from exc
        except httpx.HTTPError as exc:
            logger.warning(
                "Falha de comunicação com o provedor de IA: %s.", type(exc).__name__
            )
            raise AIProviderError("Não foi possível contatar o provedor de IA.") from exc

        return response

    def _extract_content(self, response: httpx.Response) -> str:
        try:
            body = response.json()
        except ValueError as exc:
            logger.warning("Provedor de IA retornou corpo não JSON.")
            raise AIResponseError("A resposta da IA não pôde ser validada.") from exc

        try:
            content = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            logger.warning("Resposta do provedor sem o campo de conteúdo esperado.")
            raise AIResponseError("A resposta da IA não pôde ser validada.") from exc

        if not isinstance(content, str) or not content.strip():
            logger.warning("Provedor de IA retornou conteúdo vazio.")
            raise AIResponseError("A resposta da IA não pôde ser validada.")

        return content

    def _parse_json(self, content: str) -> dict[str, Any]:
        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            logger.warning("Conteúdo da IA não é JSON válido.")
            raise AIResponseError("A resposta da IA não pôde ser validada.") from exc

        if not isinstance(data, dict):
            logger.warning("Conteúdo da IA não é um objeto JSON.")
            raise AIResponseError("A resposta da IA não pôde ser validada.")

        return data
