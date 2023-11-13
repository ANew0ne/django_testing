import pytest
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(create_news_list, client, home_url):
    """
    Проверяет, что на главной странице отображается
    правильное количество новостей.
    """
    response = client.get(home_url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(create_news_list, client, home_url):
    """
    Проверяет, что новости на главной странице отсортированы
    в хронологическом порядке: от самых новых к самым старым.
    """
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(news, client, comments_create, detail_url):
    """
    Проверяет, что комментарии на странице отдельной новости отсортированы
    в хронологическом порядке: старые в начале списка, новые — в конце.
    """
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all().order_by('created')
    assert all_comments
    sorted_comments = sorted(
        all_comments, key=lambda comment: comment.created
    )
    assert list(all_comments) == sorted_comments


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, detail_url):
    """
    Проверяет, что на странице отдельной новости не отображается форма для
    комментариев для незарегистрированных пользователей.
    """
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(client, author, detail_url):
    """
    Проверяет, что на странице отдельной новости отображается форма для
    комментариев для зарегистрированных пользователей.
    """
    client.force_login(author)
    response = client.get(detail_url)
    assert response.context.get('form') is not None
    assert isinstance(response.context['form'], CommentForm)
