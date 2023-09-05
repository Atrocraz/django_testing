import pytest

from django.conf import settings


@pytest.mark.django_db
def test_news_count(client, bulk_news, get_home_url):
    response = client.get(get_home_url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, bulk_news, get_home_url):
    response = client.get(get_home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    assert len(all_dates) > 0

    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(
    admin_client, bulk_comments, get_news_detail_url
):
    response = admin_client.get(get_news_detail_url)
    object_list = response.context['news']
    all_comments = object_list.comment_set.all()

    assert len(all_comments) > 0
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, result',
    (
        (pytest.lazy_fixture('admin_client'), True),
        (pytest.lazy_fixture('client'), False)
    ),
)
def test_pages_contains_form(
    parametrized_client, result, get_news_detail_url
):
    response = parametrized_client.get(get_news_detail_url)
    assert ('form' in response.context) is result
