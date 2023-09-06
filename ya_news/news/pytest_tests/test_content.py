import pytest
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, bulk_news, get_home_url):
    response = client.get(get_home_url)
    all_news = response.context['object_list']
    news_count = all_news.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, bulk_news, get_home_url):
    response = client.get(get_home_url)
    news_in_context = response.context['object_list']
    all_dates = [news.date for news in news_in_context]
    assert len(all_dates) > 0

    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(
    admin_client, bulk_comments, get_news_detail_url
):
    response = admin_client.get(get_news_detail_url)
    all_comments = response.context['news'].comment_set.all()

    assert all_comments.count() > 0

    sorted_comments = all_comments.order_by('created')
    assert set(all_comments) == set(sorted_comments)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, exp_result',
    (
        (pytest.lazy_fixture('admin_client'), True),
        (pytest.lazy_fixture('client'), False)
    ),
)
def test_pages_contains_form(
    parametrized_client, exp_result, get_news_detail_url
):
    response = parametrized_client.get(get_news_detail_url)
    assert ('form' in response.context) is exp_result

    if exp_result is True:
        assert isinstance(response.context['form'], CommentForm)
