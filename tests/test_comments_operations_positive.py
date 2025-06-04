import allure
import pytest
from faker import Faker
from pydantic import ValidationError

from src.models.api_model import CommentApiResponse
from tests.conftest import sql_client

fake = Faker()

@allure.feature("Comment Controller")
@allure.story("Comment Operations Positive")
@pytest.mark.positive
class TestComments:
    def test_comment_reply(self, user, publish_post, add_comment, comments_service, sql_client):
        """
        Тест на добавление ответа (реплая) к существующему комментарию.
        """
        test_data = fake.text(10)
        with allure.step("Отправка запроса на публикацию ответа к комментарию"):
            try:
                response = comments_service.reply_to_comment(add_comment, test_data)
                response.raise_for_status()
            except Exception as e:
                pytest.fail(f"Ошибка при публикации комментария: {e}")

        with allure.step("Валидация ответа API на публикацию комментария"):
            try:
                validation_response = CommentApiResponse.model_validate(response.json())
            except ValidationError as e:
                pytest.fail(f"Ошибка валидации ответа публикации комментария: {e}")

        assert validation_response.status == "ok", "Статус ответа не 'ok'"
        assert validation_response.responseData.author == user.get("email"), \
            "Автор комментария не совпадает с ожидаемым"
        assert validation_response.responseData.text == test_data, \
            "Текст комментария не совпадает с ожидаемым"
        assert sql_client.get_comment_by_id(validation_response.responseData.id) is not None,\
            "Комментарий не найден в базе"

