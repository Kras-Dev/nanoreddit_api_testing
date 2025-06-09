import allure
import pytest
from faker import Faker
from pydantic import ValidationError

from src.models.api_model import ApiResponse

fake = Faker()

@allure.feature("Comment Controller")
@allure.story("Comment Operations Negative")
@pytest.mark.negative
@pytest.mark.comments
class TestCommentsNegative:
    @allure.title("Ответ на комментарий с несуществующим ID родителя")
    def test_comment_reply_invalid_id(self, clients, user):
        """Тест попытки ответить на комментарий с несуществующим parent_comment_id
        """
        test_data = {
            "parent_comment_id": fake.uuid4(),
            "comment_text": fake.text(10)
        }

        validation_response = clients.comments.reply_to_comment(**test_data)

        assert validation_response.status == "error", \
            f"Ожидался статус 'error', получен '{validation_response.status}'"
        assert validation_response.error == "Parent comment not found", \
            f"Ожидалось сообщение 'Parent comment not found', получено '{validation_response.error}'"
