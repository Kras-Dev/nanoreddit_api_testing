from typing import Any, Dict, Optional

import allure
import requests

from src.config.api_endpoints import ApiEndpoints


class BaseClient:
    def __init__(self):
        """Инициализация клиента с базовым URL и сессией requests."""
        self.base_url = ApiEndpoints.BASE_URL
        self.session = requests.Session()
        self._token: Optional[str] = None

    def set_token(self, token: str) -> None:
        """Установить JWT токен для авторизации.

        Токен добавляется в заголовок Authorization для всех последующих запросов.
        """
        self._token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    @property
    def token(self) -> Optional[str]:
        """Текущий JWT токен, используемый для авторизации."""
        return self._token

    def clear_token(self) -> None:
        """Очистить JWT токен из заголовков сессии."""
        self._token = None
        self.session.headers.pop('Authorization', None)

    def _url(self, path: str) -> str:
        """Сформировать полный URL, объединяя базовый URL и путь эндпоинта."""
        return f"{self.base_url}{path}"

    @allure.step("Отправить POST-запрос на {path}")
    def post_request(self, path: str, json: Optional[Dict[str, Any]] = None,
                     params: Optional[Dict[str, Any]] = None, expected_status: int = 200) -> requests.Response:
        """Отправить POST-запрос по указанному пути с JSON-данными и проверить статус."""
        url = self._url(path)
        response = self.session.post(url, json=json, params=params)
        self._check_status(response, expected_status)
        return response

    @allure.step("Отправить GET-запрос на {path}")
    def get_request(self, path: str, params: Optional[Dict[str, Any]] = None,
                    expected_status: int = 200) -> requests.Response:
        """Отправить GET-запрос по указанному пути с параметрами запроса и проверить статус."""
        url = self._url(path)
        response = self.session.get(url, params=params)
        self._check_status(response, expected_status)
        return response

    def _check_status(self, response: requests.Response, expected_status: int):
        """Проверяет, что HTTP-статус ответа совпадает с ожидаемым."""
        if response.status_code != expected_status:
            raise requests.HTTPError(
                f"Ожидался статус {expected_status}, получен {response.status_code}: {response.text}")

    def close_session(self) -> None:
        """Закрыть сессию requests."""
        self.session.close()