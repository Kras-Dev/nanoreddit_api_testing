import requests

from src.config.api_endpoints import ApiEndpoints
from src.clients.http_client.base_client import BaseClient
from src.models.api_model import RegistrationRequest, LoginRequest, ApiResponse


class AuthService:
    """
    Клиент для работы с регистрацией и авторизацией через API.
    """
    def __init__(self, base_client: BaseClient) -> None:
        self.api = base_client

    def register(self, data: dict) ->requests.Response:
        """
        Регистрация нового пользователя с валидацией данных через Pydantic.
        """
        data = RegistrationRequest.model_validate(data)
        response = self.api.post_request(ApiEndpoints.AUTH_REGISTER, json=data.model_dump())
        return response

    def login(self, data: dict) -> requests.Response:
        """
        Авторизация пользователя с валидацией данных через Pydantic.
        """
        data = LoginRequest.model_validate(data)
        response = self.api.post_request(ApiEndpoints.AUTH_LOGIN, json=data.model_dump())
        validation_response = ApiResponse.model_validate(response.json())
        token = (validation_response.responseData or {}).get("jwt")
        if token:
            self.api.set_token(token)
        return response