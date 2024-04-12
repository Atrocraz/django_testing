from http import HTTPStatus
from random import choice

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

NEW_COMMENT_TEXT = 'changed text'


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, result',
    ((pytest.lazy_fixture('author_client'), 1),
     (pytest.lazy_fixture('client'), 0)),
)
def test_diff_users_can_leave_comment(parametrized_client, result,
                                      get_news_detail_url, author, news):
    comment_text = 'test comm'
    parametrized_client.post(get_news_detail_url, data={'text': comment_text})
    assert Comment.objects.count() == result

    if result:
        comment = Comment.objects.get()
        assert comment.text == comment_text
        assert comment.author == author
        assert comment.news == news


def test_bad_language(admin_client, get_news_detail_url):
    bad_words_data = {
        'text': f'Какой-то текст, {choice(BAD_WORDS)}, еще текст'
    }
    expected_count = Comment.objects.count()
    response = admin_client.post(get_news_detail_url, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert Comment.objects.count() == expected_count


def test_user_cant_delete_comment_of_another_user(admin_client,
                                                  get_comm_delete_url):
    expected_count = Comment.objects.count()
    response = admin_client.delete(get_comm_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == expected_count


def test_user_can_delete_his_comment(author_client, get_comm_delete_url,
                                     get_news_detail_url_redir):
    expected_count = Comment.objects.count()
    response = author_client.delete(get_comm_delete_url)
    assertRedirects(response, get_news_detail_url_redir)
    assert Comment.objects.count() == expected_count - 1


def test_user_cant_edit_comment_of_another_user(admin_client,
                                                get_comm_edit_url, comment):
    response = admin_client.post(get_comm_edit_url,
                                 data={'text': NEW_COMMENT_TEXT})
    assert response.status_code == HTTPStatus.NOT_FOUND
    old_comment_text = comment.text
    old_comment_author = comment.author
    old_comment_news = comment.news
    comment.refresh_from_db()

    assert comment.text == old_comment_text
    assert comment.author == old_comment_author
    assert comment.news == old_comment_news


def test_user_can_edit_his_comment(
        author_client, get_comm_edit_url,
        get_news_detail_url_redir, comment):
    response = author_client.post(get_comm_edit_url,
                                  data={'text': NEW_COMMENT_TEXT})
    assertRedirects(response, get_news_detail_url_redir)
    old_comment_author = comment.author
    old_comment_news = comment.news
    comment.refresh_from_db()

    assert comment.text == NEW_COMMENT_TEXT
    assert comment.author == old_comment_author
    assert comment.news == old_comment_news
