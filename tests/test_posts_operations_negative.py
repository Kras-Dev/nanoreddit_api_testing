import allure
import pytest
from faker import Faker
from pydantic import ValidationError

from src.models.api_model import ApiResponse

fake = Faker()

@allure.feature("Post Controller")
@allure.story("Post Operations Negative")
@pytest.mark.negative
class TestPostsNegative:
    @allure.title("Получение поста без авторизации")
    def test_get_post_no_auth(self, posts_controller):
        """
        Тест получения информации о посте без авторизации
        """
        post_id = str(fake.uuid4())
        with allure.step("Отправка запроса на получение информации о посте"):
            try:
                response = posts_controller.get_post(post_id)
                response.raise_for_status()
            except Exception as e:
                pytest.fail(f"Ошибка при получении информации о посте: {e}")

        with allure.step("Валидация ответа информации о посте"):
            try:
                validation_response = ApiResponse.model_validate(response.json())
            except ValidationError as e:
                pytest.fail(f"Ошибка валидации ответа информации о посте: {e}")

            assert validation_response.status == "error", "Ожидался статус 'error' в ответе"
            assert validation_response.error == "Access denied", "Ожидалось сообщение об ошибке 'Access denied'"

    @allure.title("Получение поста с несуществующим ID")
    def test_get_post_invalid_id(self, posts_controller, user):
        """
        Тест получения поста с несуществующим ID.
        """
        post_id = fake.uuid4()
        with allure.step("Отправка запроса на получение информации о посте"):
            try:
                response = posts_controller.get_post(post_id)
                response.raise_for_status()
            except Exception as e:
                pytest.fail(f"Ошибка при получении информации о посте: {e}")

        with allure.step("Валидация ответа API"):
            try:
                validation_response = ApiResponse.model_validate(response.json())
            except ValidationError as e:
                pytest.fail(f"Ошибка валидации ответа при получении информации о посте: {e}")

        assert validation_response.status == "error", "Ожидался статус 'error' в ответе"
        assert validation_response.error == "Post not found", "Ожидалось сообщение об ошибке 'Post not found'"

    @allure.title("Добавление комментария к несуществующему посту")
    def test_add_comment_invalid_post_id(self, posts_controller, user):
        """
        Тест добавления комментария к посту с несуществующим ID.
        """
        test_data = {"post_id": fake.uuid4(), "comment_text": fake.text(12)}
        with allure.step("Отправка запроса на публикацию комментария"):
            try:
                response = posts_controller.add_comment(**test_data)
                response.raise_for_status()
            except Exception as e:
                pytest.fail(f"Ошибка при добавлении комментария: {e}")

        with allure.step("Валидация ответа добавления комментария"):
            try:
                validation_response = ApiResponse.model_validate(response.json())
            except ValidationError as e:
                pytest.fail(f"Ошибка валидации ответа добавления комментария: {e}")

            assert validation_response.status == "error", f"Статус ответа не 'error': {validation_response.status}"
            assert validation_response.error == "Post not found", "Ожидалось сообщение об ошибке 'Post not found'"

    @allure.title("Голосование за пост с несуществующим ID")
    def test_vote_post_invalid_id(self, posts_controller, user):
        """
        Тест голосования за пост с несуществующим ID.
        """
        test_data = {"post_id": fake.uuid4(), "value": 1}
        with allure.step("Отправка запроса на голосование за пост"):
            try:
                response = posts_controller.vote_post(**test_data)
                response.raise_for_status()
            except Exception as e:
                pytest.fail(f"Ошибка при голосовании за пост: {e}")

        with allure.step("Валидация ответа голосования за пост"):
            try:
                validation_response = ApiResponse.model_validate(response.json())
            except ValidationError as e:
                pytest.fail(f"Ошибка валидации ответа голосования за пост: {e}")

            assert validation_response.status == "error", f"Статус ответа не 'error': {validation_response.status}"
            assert validation_response.error == "Post not found", "Ожидалось сообщение об ошибке 'Post not found'"

