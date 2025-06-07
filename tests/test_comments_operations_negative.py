import allure
import pytest
from faker import Faker
from pydantic import ValidationError

from src.models.api_model import ApiResponse

fake = Faker()

@allure.feature("Comment Controller")
@allure.story("Comment Operations Negative")
@pytest.mark.negative
class TestCommentsNegative:
    @allure.title("Ответ на комментарий с несуществующим ID родителя")
    def test_comment_reply_invalid_id(self, user, comments_controller):
        """
        Тест попытки ответить на комментарий с несуществующим parent_comment_id
        """
        test_data = {
            "parent_comment_id": fake.uuid4(),
            "comment_text": fake.text(10)
        }
        with allure.step("Отправка запроса на ответ на комментарий с несуществующим ID родителя"):
            try:
                response = comments_controller.reply_to_comment(**test_data)
                response.raise_for_status()
            except Exception as e:
                pytest.fail(f"Ошибка при ответе на комментарий с несуществующим ID родителя: {e}")

        with allure.step("Валидация ответа API"):
            try:
                validation_response = ApiResponse.model_validate(response.json())
            except ValidationError as e:
                pytest.fail(f"Ошибка валидации ответа API: {e}")

        assert validation_response.status == "error", \
            f"Ожидался статус 'error', получен '{validation_response.status}'"
        assert validation_response.error == "Parent comment not found", \
            f"Ожидалось сообщение 'Parent comment not found', получено '{validation_response.error}'"
