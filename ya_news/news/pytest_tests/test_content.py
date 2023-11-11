import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(comment_count, client):
    """
    Проверяет, что на главной странице отображается
    правильное количество новостей.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(comment_count, client):
    """
    Проверяет, что новости на главной странице отсортированы
    в хронологическом порядке: от самых новых к самым старым.
    """
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(news, client, comments_create):
    """
    Проверяет, что комментарии на странице отдельной новости отсортированы
    в хронологическом порядке: старые в начале списка, новые — в конце.
    """
    response = client.get(reverse('news:detail', args=(news.id,)))
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments
    sorted_comments = sorted(
        all_comments, key=lambda comment: comment.created, reverse=True
    )
    assert list(all_comments.order_by('-created')) == sorted_comments


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news):
    """
    Проверяет, что на странице отдельной новости не отображается форма для
    комментариев для незарегистрированных пользователей.
    """
    response = client.get(reverse('news:detail', args=(news.id,)))
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(client, author, news):
    """
    Проверяет, что на странице отдельной новости отображается форма для
    комментариев для зарегистрированных пользователей.
    """
    client.force_login(author)
    response = client.get(reverse('news:detail', args=(news.id,)))
    assert isinstance(response.context['form'], CommentForm)
