import allure
import pytest
from faker import Faker

fake = Faker()

@allure.feature("Comment Controller")
@allure.story("Comment Operations Positive")
@pytest.mark.positive
@pytest.mark.comments
class TestComments:
    def test_comment_reply(self, clients, user, publish_post, add_comment):
        """Тест на добавление ответа (реплая) к существующему комментарию."""
        test_data = fake.text(10)
        validation_response = clients.comments.reply_to_comment(add_comment, test_data)

        assert validation_response.status == "ok", "Статус ответа не 'ok'"
        assert validation_response.responseData.author == user.get("email"), \
            "Автор комментария не совпадает с ожидаемым"
        assert validation_response.responseData.text == test_data, \
            "Текст комментария не совпадает с ожидаемым"
        assert clients.db.get_comment_by_id(validation_response.responseData.id) is not None,\
            "Комментарий не найден в базе"

