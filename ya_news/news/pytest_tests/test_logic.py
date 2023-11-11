import pytest

from django.urls import reverse
from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_note(client, form_data, news):
    """
    Проверяет, что незарегистрированный пользователь
    не может создать комментарий.
    """
    url = reverse('news:detail', args=(news.pk,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, author, form_data, news):
    """
    Проверяет, что зарегистрированный пользователь может
    создать комментарий.
    """
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.news == news
    assert new_comment.author == author


def test_user_cant_use_bad_words(author_client, news):
    """
    Проверяет, что пользователь не может использовать
    запрещенные слова в комментариях.
    """
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, news, comment):
    """Проверяет, что автор комментария может его удалить."""
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.delete(reverse('news:delete', args=(comment.pk,)))
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(admin_client, comment):
    """
    Проверяет, что пользователь не может удалить комментарий
    другого пользователя.
    """
    response = admin_client.delete(reverse('news:delete', args=(comment.pk,)))
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(author_client, form_data, news, comment):
    """Проверяет, что автор комментария может его редактировать."""
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(
        reverse('news:edit', args=(comment.pk,)), data=form_data)
    assertRedirects(response, f'{url}#comments')
    comment.refresh_from_db()
    assert comment.text == 'Новый текст'


def test_user_cant_edit_comment_of_another_user(
    admin_client, form_data, comment
):
    """
    Проверяет, что пользователь не может редактировать комментарий
    другого пользователя.
    """
    response = admin_client.post(
        reverse('news:delete', args=(comment.pk,)), data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст'
