
from src.clients.http_client.base_client import BaseClient
from src.config.api_endpoints import ApiEndpoints
from src.models.api_model import ApiResponse, LoginRequest, RegistrationRequest


class AuthController:
    """Клиент для работы с регистрацией и авторизацией через API."""

    def __init__(self, base_client: BaseClient) -> None:
        self.api = base_client

    def register(self, data: RegistrationRequest) -> ApiResponse:
        """Регистрация нового пользователя с валидацией данных через Pydantic."""
        response = self.api.post_request(ApiEndpoints.AUTH_REGISTER, json=data.model_dump())
        validation_response = ApiResponse.model_validate(response.json())
        return validation_response

    def login(self, data: LoginRequest) -> ApiResponse:
        """Авторизация пользователя с валидацией данных через Pydantic."""
        response = self.api.post_request(ApiEndpoints.AUTH_LOGIN, json=data.model_dump())
        validation_response = ApiResponse.model_validate(response.json())
        token = (validation_response.responseData or {}).get("jwt")
        if token:
            self.api.set_token(token)
        return validation_response