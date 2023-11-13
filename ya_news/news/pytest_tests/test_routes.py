"""Тестирование маршрутов."""
from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

HOME_URL = pytest.lazy_fixture('home_url')
DETAIL_URL = pytest.lazy_fixture('detail_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
LOGOUT_URL = pytest.lazy_fixture('logout_url')
SIGNUP_URL = pytest.lazy_fixture('signup_url')
EDIT_URL = pytest.lazy_fixture('edit_url')
DELETE_URL = pytest.lazy_fixture('delete_url')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    (
        HOME_URL,
        DETAIL_URL,
        LOGIN_URL,
        LOGOUT_URL,
        SIGNUP_URL,
    )
)
def test_pages_availability_for_anonymous_user(client, name):
    """Тест доступности страниц анонимному пользователю."""
    response = client.get(name)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('user_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize('name', (EDIT_URL, DELETE_URL),)
def test_pages_availability_for_different_users(
        parametrized_client, name, expected_status
):
    """
    Тест доступности редактирования и удаления заметок автору
    и недоступности другим пользователям.
    """
    response = parametrized_client.get(name)
    assert response.status_code == expected_status


@pytest.mark.parametrize('name', (EDIT_URL, DELETE_URL),)
def test_redirects(client, name, login_url):
    """Тест редиректа для анонимного пользователя."""
    expected_url = f'{login_url}?next={name}'
    response = client.get(name)
    assertRedirects(response, expected_url)
