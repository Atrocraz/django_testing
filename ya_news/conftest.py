from datetime import timedelta
import pytest

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.models import News, Comment

HOME_URL = 'news:home'
DETAIl_URL = 'news:detail'
COMM_EDIT_URL = 'news:edit'
COMM_DELETE_URL = 'news:delete'
LOGIN_URL = 'users:login'
LOGOUT_URL = 'users:logout'
SIGNUP_URL = 'users:signup'


@pytest.fixture
def get_home_url():
    return reverse(HOME_URL)


@pytest.fixture
def get_news_detail_url(news_id):
    return reverse(DETAIl_URL, args=news_id)


@pytest.fixture
def get_news_detail_url_redir(news_id):
    return reverse(DETAIl_URL, args=news_id) + '#comments'


@pytest.fixture
def get_comm_edit_url(comment_id):
    return reverse(COMM_EDIT_URL, args=comment_id)


@pytest.fixture
def get_comm_delete_url(comment_id):
    return reverse(COMM_DELETE_URL, args=comment_id)


@pytest.fixture
def get_login_url():
    return reverse(LOGIN_URL)


@pytest.fixture
def get_logout_url():
    return reverse(LOGOUT_URL)


@pytest.fixture
def get_signup_url():
    return reverse(SIGNUP_URL)


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title="Новая новость",
        text="Текст новости",
        date="2023-09-23"
    )
    return news


@pytest.fixture
def bulk_news():
    today = timezone.now()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def news_id(news):
    return (news.id, )


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        text="123",
        author=author,
    )
    return comment


@pytest.fixture
def bulk_comments(author, news):
    today = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Tекст {index}',
        )
        comment.created = today + timedelta(days=index)
        comment.save()


@pytest.fixture
def comment_id(comment):
    return (comment.id, )
