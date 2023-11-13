from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_note(
        client, form_data, detail_url, login_url
):
    """
    Проверяет, что незарегистрированный пользователь
    не может создать комментарий.
    """
    response = client.post(detail_url, data=form_data)
    expected_url = f'{login_url}?next={detail_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    author_client, author, form_data, news, detail_url
):
    """
    Проверяет, что зарегистрированный пользователь может
    создать комментарий.
    """
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.news == news
    assert new_comment.author == author


def test_user_cant_use_bad_words(
        author_client, bad_words_data, detail_url
):
    """
    Проверяет, что пользователь не может использовать
    запрещенные слова в комментариях.
    """
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, delete_url, detail_url):
    """Проверяет, что автор комментария может его удалить."""
    response = author_client.delete(delete_url)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(user_client, delete_url):
    """
    Проверяет, что пользователь не может удалить комментарий
    другого пользователя.
    """
    response = user_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(
    author, author_client, form_data, news, comment, edit_url, detail_url
):
    """Проверяет, что автор комментария может его редактировать."""
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comment.refresh_from_db()
    assert comment.text == 'Новый текст'
    assert comment.news == news
    assert comment.author == author


def test_user_cant_edit_comment_of_another_user(
    user_client, form_data, comment, delete_url
):
    """
    Проверяет, что пользователь не может редактировать комментарий
    другого пользователя.
    """
    response = user_client.post(delete_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    new_comment = Comment.objects.get(pk=comment.id)
    assert comment.text == new_comment.text
