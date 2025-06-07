from uuid import UUID

import requests

from src.clients.http_client.base_client import BaseClient
from src.config.api_endpoints import ApiEndpoints
from src.models.api_model import NewCommentRequest


class CommentsController:
    def __init__(self, base_client: BaseClient):
        """
        Клиент для работы с комментариями через API.
        """
        self.api = base_client

    def reply_to_comment(self, parent_comment_id: str, comment_text: str) -> requests.Response:
        """
        Отправляет ответ на комментарий с указанным parent_comment_id.
        """
        try:
            UUID(parent_comment_id)
        except ValueError:
            raise ValueError(f"post_id '{parent_comment_id}' не является валидным UUID")
        data = NewCommentRequest(text=comment_text)
        endpoint = ApiEndpoints.COMMENT_REPLY.format(parentCommentId=str(parent_comment_id))
        params = {"text": data}
        response = self.api.post_request(endpoint, json=data.model_dump(), params=params)
        return response