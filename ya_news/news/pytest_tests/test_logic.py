import pytest

from http import HTTPStatus

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from pytest_django.asserts import assertFormError, assertRedirects

NEW_COMMENT_TEXT = 'changed text'


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, result',
    (
        (pytest.lazy_fixture('admin_client'), 1),
        (pytest.lazy_fixture('client'), 0)
    ),
)
def test_diff_users_can_leave_comment(
    parametrized_client, result, get_news_detail_url
):
    parametrized_client.post(get_news_detail_url, data={'text': 'test comm'})
    assert Comment.objects.count() == result


@pytest.mark.django_db
def test_bad_language(
    admin_client, get_news_detail_url
):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = admin_client.post(get_news_detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
    admin_client, get_comm_delete_url,
):
    response = admin_client.delete(get_comm_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_user_can_delete_his_comment(
    author_client, get_comm_delete_url, get_news_detail_url_redir,
):
    response = author_client.delete(get_comm_delete_url)
    assertRedirects(response, get_news_detail_url_redir)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    admin_client, get_comm_edit_url, comment
):
    response = admin_client.post(
        get_comm_edit_url, data={'text': NEW_COMMENT_TEXT}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    old_comment_text = comment.text
    comment.refresh_from_db()

    assert comment.text == old_comment_text


@pytest.mark.django_db
def test_user_can_edit_his_comment(
    author_client, get_comm_edit_url, get_news_detail_url_redir, comment
):
    response = author_client.post(
        get_comm_edit_url, data={'text': NEW_COMMENT_TEXT}
    )
    assertRedirects(response, get_news_detail_url_redir)
    comment.refresh_from_db()

    assert comment.text == NEW_COMMENT_TEXT
