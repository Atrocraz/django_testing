from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('get_home_url'),
        pytest.lazy_fixture('get_login_url'),
        pytest.lazy_fixture('get_logout_url'),
        pytest.lazy_fixture('get_signup_url'),
        pytest.lazy_fixture('get_news_detail_url'),
    ),
)
def test_news_detail_availible(client, news, url):
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('get_comm_edit_url'),
        pytest.lazy_fixture('get_comm_delete_url'),
    ),
)
def test_pages_availability_for_different_users(
        parametrized_client, url, comment, expected_status
):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('get_comm_edit_url'),
        pytest.lazy_fixture('get_comm_delete_url'),
    ),
)
def test_redirects(client, url, get_login_url):
    login_url = get_login_url
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
